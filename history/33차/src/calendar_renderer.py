"""현재 날짜의 실제 메시를 소유 스레드의 오프스크린 GPU에서 렌더합니다."""

from __future__ import annotations

import math
from functools import lru_cache

import hashlib

import threading

import numpy as np

import moderngl

from PySide6.QtGui import QImage

from calendar_art import design_for_date
from fruit_surface import fruit_mesh, petal_mesh, instrument_body, surface_tube, organic_shaders
from pathlib import Path

VERTEX = '#version 330\nin vec3 in_position;\nin vec3 in_normal;\nuniform mat4 model;\nuniform mat4 view_projection;\nout vec3 position;\nout vec3 normal;\nvoid main() {\n    vec4 world = model * vec4(in_position, 1.0);\n    position = world.xyz;\n    normal = mat3(model) * in_normal;\n    gl_Position = view_projection * world;\n}\n'

FRAGMENT = '#version 330\nin vec3 position;\nin vec3 normal;\nuniform vec3 camera;\nuniform float metallic;\nuniform vec3 base_color;\nuniform float roughness;\nout vec4 color;\nconst float PI = 3.14159265359;\n// 실제 월드 반사 방향이 스튜디오의 긴 면광원을 바라보는 정도를 계산합니다.\nfloat box_light(vec3 direction, vec3 center, vec3 up, vec2 bounds, float softness) {\n    vec3 forward = normalize(center);\n    vec3 side = normalize(cross(forward, up));\n    vec3 vertical = cross(side, forward);\n    float facing = dot(direction, forward);\n    if (facing <= 0.0) return 0.0;\n    vec2 uv = vec2(dot(direction, side), dot(direction, vertical)) / facing;\n    vec2 edge = smoothstep(bounds, bounds + vec2(softness), abs(uv));\n    return (1.0 - edge.x) * (1.0 - edge.y);\n}\nfloat studio(vec3 direction, float blur) {\n    float value = .075 + .10 * (direction.y*.5+.5);\n    value += 3.8 * box_light(direction, vec3(-.52, .72, .62), vec3(0,1,0), vec2(.27,.82), .055+blur);\n    value += 2.4 * box_light(direction, vec3(.90, .05, .32), vec3(0,1,0), vec2(.105,.78), .035+blur);\n    value += 2.8 * box_light(direction, vec3(.10, .90, -.48), vec3(0,0,1), vec2(.68,.12), .045+blur);\n    value += .65 * box_light(direction, vec3(-.65, -.40, .35), vec3(0,1,0), vec2(.40,.62), .20+blur);\n    value += .25 * box_light(direction, vec3(.2,-.4,.9), vec3(0,1,0), vec2(.8,.45), .35+blur);\n    return value;\n}\n// 거칠기에 따른 반사 방향 원판을 고정 표본으로 적분하여 시간별 잡음을 만들지 않습니다.\nfloat filtered_studio(vec3 reflected, float rough) {\n    vec3 up = abs(reflected.y)<.95 ? vec3(0,1,0) : vec3(1,0,0);\n    vec3 tangent = normalize(cross(up,reflected));\n    vec3 bitangent = cross(reflected,tangent);\n    float total=0.0;\n    float weight_sum=0.0;\n    for(int i=0;i<12;i++) {\n        float radius=sqrt((float(i)+.5)/12.0);\n        float theta=float(i)*2.39996323;\n        float weight=exp(-2.2*radius*radius);\n        vec3 sample_direction=normalize(reflected+rough*1.7*radius*(cos(theta)*tangent+sin(theta)*bitangent));\n        total+=studio(sample_direction,rough*.30)*weight;\n        weight_sum+=weight;\n    }\n    return total/weight_sum;\n}\nfloat distribution(float nh, float alpha) {\n    float a2 = alpha * alpha;\n    float d = nh * nh * (a2 - 1.0) + 1.0;\n    return a2 / max(PI * d * d, .00001);\n}\nfloat visibility(float nv, float nl, float alpha) {\n    float k = (alpha + 1.0) * (alpha + 1.0) / 8.0;\n    return (nv / (nv * (1.0-k) + k)) * (nl / (nl * (1.0-k) + k));\n}\nfloat aces(float x) {\n    return clamp((x*(2.51*x+.03))/(x*(2.43*x+.59)+.14),0.0,1.0);\n}\nvoid main() {\n    vec3 n = normalize(normal);\n    vec3 v = normalize(camera-position);\n    float nv = max(dot(n,v),.001);\n    vec3 r = reflect(-v,n);\n    vec3 f0 = mix(vec3(.04),base_color,metallic);\n    vec3 fresnel = f0 + (1.0-f0)*pow(1.0-nv,5.0);\n    float environment = filtered_studio(r,roughness);\n    vec3 reflected = environment * fresnel * (1.0-.28*roughness);\n    vec3 l = normalize(vec3(-.4,.7,.8));\n    vec3 h = normalize(v+l);\n    float nl = max(dot(n,l),0.0);\n    float nh = max(dot(n,h),0.0);\n    float vh = max(dot(v,h),0.0);\n    vec3 f = f0+(1.0-f0)*pow(1.0-vh,5.0);\n    float alpha = max(.04,roughness*roughness);\n    vec3 specular = distribution(nh,alpha)*visibility(nv,nl,roughness)*f/max(4.0*nv*nl,.01);\n    vec3 diffuse = (1.0-metallic)*base_color*(.16+.48*nl);\n    vec3 radiance = reflected + diffuse + .25*specular*nl;\n    vec3 display = pow(vec3(aces(radiance.r),aces(radiance.g),aces(radiance.b)),vec3(1.0/2.2));\n    color = vec4(display,1.0);\n}\n'

def rotation(axis, angle):
    """정규화된 실제 3D축을 중심으로 로드리게스 회전행렬을 만듭니다."""
    axis = np.asarray(axis, dtype=np.float64)
    axis /= np.linalg.norm(axis)
    x, y, z = axis
    c, s, t = (math.cos(angle), math.sin(angle), 1 - math.cos(angle))
    return np.array([[t * x * x + c, t * x * y - s * z, t * x * z + s * y], [t * x * y + s * z, t * y * y + c, t * y * z - s * x], [t * x * z - s * y, t * y * z + s * x, t * z * z + c]], dtype=np.float64)

def sphere_mesh(radius, longitude=96, latitude=48):
    vertices = []
    indices = []
    for i in range(latitude + 1):
        phi = math.pi * i / latitude
        for j in range(longitude + 1):
            theta = math.tau * j / longitude
            n = (math.sin(phi) * math.cos(theta), math.cos(phi), math.sin(phi) * math.sin(theta))
            vertices.append((*[radius * v for v in n], *n))
    for i in range(latitude):
        for j in range(longitude):
            a = i * (longitude + 1) + j
            b = a + longitude + 1
            indices.extend((a, a + 1, b, a + 1, b + 1, b))
    return (np.asarray(vertices, dtype='f4'), np.asarray(indices, dtype='u4'))

def finish(vertices, indices):
    """표면 법선과 삼각형 winding을 일치시킵니다."""
    v = np.asarray(vertices, dtype='f4')
    ix = np.asarray(indices, dtype='u4').reshape(-1, 3)
    p = v[ix, :3]
    n = v[ix, 3:].mean(axis=1)
    reverse = np.einsum('ij,ij->i', np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]), n) < 0
    ix[reverse] = ix[reverse][:, [0, 2, 1]]
    return (v, ix.reshape(-1))

def box(size, bevel=3, steps=14):
    """육면체 면을 실제 둥근 모서리와 구면 꼭짓점으로 투영합니다."""
    half = np.asarray(size, dtype=float) / 2
    inner = half - bevel
    vertices = []
    indices = []
    for axis in range(3):
        other = [i for i in range(3) if i != axis]
        for sign in (-1, 1):
            start = len(vertices)
            for i in range(steps + 1):
                for j in range(steps + 1):
                    p = np.zeros(3)
                    p[axis] = sign * half[axis]
                    p[other] = [(2 * i / steps - 1) * half[other[0]], (2 * j / steps - 1) * half[other[1]]]
                    q = np.clip(p, -inner, inner)
                    n = p - q
                    n /= np.linalg.norm(n)
                    vertices.append((*list(q + bevel * n), *list(n)))
            for i in range(steps):
                for j in range(steps):
                    a = start + i * (steps + 1) + j
                    b = a + steps + 1
                    indices.extend((a, b, a + 1, a + 1, b, b + 1))
    return finish(vertices, indices)

def lathe(profile, sides=64, smooth=True):
    """회전체의 실제 앞뒤·옆면을 만들며 다각 단면은 평면 법선을 보존합니다."""
    vertices = []
    indices = []
    for row in range(len(profile) - 1):
        radius, y = profile[row]
        next_radius, next_y = profile[row + 1]
        for j in range(sides):
            a = math.tau * j / sides
            b = math.tau * (j + 1) / sides
            corners = [(radius * math.cos(a), y, radius * math.sin(a)), (radius * math.cos(b), y, radius * math.sin(b)), (next_radius * math.cos(b), next_y, next_radius * math.sin(b)), (next_radius * math.cos(a), next_y, next_radius * math.sin(a))]
            start = len(vertices)
            for k, p in enumerate(corners):
                t = (a if k in (0, 3) else b) if smooth else (a + b) / 2
                n = np.array([(next_y - y) * math.cos(t), radius - next_radius, (next_y - y) * math.sin(t)])
                n /= np.linalg.norm(n)
                vertices.append((*p, *n))
            indices.extend((start, start + 1, start + 2, start, start + 2, start + 3))
    return finish(vertices, indices)

def tube(points, radius=3, closed=False, sides=14):
    """3D 경로를 따라 원형 단면을 운반합니다. 코일은 실제 깊이를 가집니다."""
    points = np.asarray(points, dtype=float)
    vertices = []
    indices = []
    count = len(points)
    for i, p in enumerate(points):
        before = points[(i - 1) % count] if closed or i else points[0]
        after = points[(i + 1) % count] if closed or i < count - 1 else points[-1]
        tangent = after - before
        tangent /= np.linalg.norm(tangent)
        up = np.array([0.0, 1.0, 0.0]) if abs(tangent[1]) < 0.95 else np.array([1.0, 0.0, 0.0])
        side = np.cross(tangent, up)
        side /= np.linalg.norm(side)
        vertical = np.cross(tangent, side)
        for j in range(sides):
            n = side * math.cos(math.tau * j / sides) + vertical * math.sin(math.tau * j / sides)
            vertices.append((*list(p + radius * n), *list(n)))
    for i in range(count if closed else count - 1):
        for j in range(sides):
            a = i * sides + j
            b = (i + 1) % count * sides + j
            c = (i + 1) % count * sides + (j + 1) % sides
            d = i * sides + (j + 1) % sides
            indices.extend((a, b, c, a, c, d))
    return finish(vertices, indices)


PERIOD = 12.0
SIZE = 384


def _transformed(mesh, pos=(0,0,0), scale=(1,1,1), angle=0):
    vertices,indices=mesh; vertices=vertices.copy()
    matrix=rotation((0,0,1),angle)
    vertices[:,:3]=(vertices[:,:3]*np.asarray(scale,dtype=float))@matrix.T+np.asarray(pos,dtype=float)
    normals=(vertices[:,3:]/np.asarray(scale,dtype=float))@matrix.T
    normals/=np.linalg.norm(normals,axis=1)[:,None]; vertices[:,3:]=normals
    return vertices,indices


def _object_geometry(spec, color, material_specs=None):
    """대상 이름에 연결된 주요 구조를 실제 삼각형 부품으로 구성합니다."""
    if spec.recipe.startswith('city_'):
        from city_festival_geometry import city_festival_geometry
        return city_festival_geometry(spec,color)
    if spec.category=='특집':
        from calendar_special_geometry import special_geometry
        return special_geometry(spec,color)
    if spec.category=='악기' and spec.recipe in ('piano','sax','brass','horn','drum','bowl_drum','tambourine'):
        from calendar_instruments import instrument_geometry
        return instrument_geometry(spec)
    parts=[]
    sphere=sphere_mesh(1,40,24)
    green=(.025,.12,.018); gold=(.68,.48,.16); dark=(.11,.12,.17)
    n=spec.count; w=spec.width; h=spec.length; recipe=spec.recipe
    def add(mesh,pos=(0,0,0),scale=(1,1,1),angle=0,tint=None,metal=None,rough=None):
        base=tint or color
        natural=spec.category in ('꽃','열매','잎')
        brass=spec.key in ('saxophone','trumpet','trombone','horn','tuba','handbell','timpani')
        silver_part=base==(.65,.72,.78)
        if metal is None:metal=0. if natural else (1. if silver_part or (brass and base!=dark) or spec.key=='flute' else 0.)
        if not natural and tint is None:
            if brass:base=(.56,.30,.075)
            elif spec.key in ('clarinet','oboe','piano'):base=(.012,.014,.018)
            elif spec.key=='flute':base=(.65,.72,.78)
            else:base=(.24,.105,.035)
        if rough is None:
            rough={'coconut':.88,'kiwi':.85,'peach':.76,'apricot':.67,'orange':.57,'mandarin':.55,'lemon':.56,'lime':.46,
                   'raspberry':.74,'blackberry':.48,'blueberry':.82,'apple':.34,'plum_fruit':.30,'grape':.31,'muscat':.30}.get(spec.key,.64 if spec.category=='꽃' else .54 if natural else .23 if metal else .34)
        parts.append((_transformed(mesh,pos,scale,angle),base,metal,rough))
        if material_specs is not None:
            points=mesh[0][:,:3];low=points.min(axis=0);span=np.maximum(np.ptp(points,axis=0),.001)
            local=np.eye(4);local[:3,:3]=rotation((0,0,1),angle)@np.diag(scale);local[:3,3]=pos
            normalized=np.eye(4);normalized[:3,:3]=np.diag(1/span);normalized[:3,3]=-low/span
            material_specs.append({'enabled':natural and tint is None,'mapping':normalized@np.linalg.inv(local)})
    def orb(pos,scale,tint=None,angle=0):add(sphere,pos,scale,angle,tint)
    def rod(points,radius=1.2,tint=None,closed=False):add(surface_tube(points,radius,closed,12),tint=tint)
    def petal(x,y,z,width,length,angle,tint=None,tilt=0.,twist=0.):
        vertices,indices=petal_mesh(width,length,leaf=spec.category=='잎' or tint==green)
        matrix=rotation((1,0,0),tilt)@rotation((0,1,0),twist)
        vertices=vertices.copy();vertices[:,:3]=vertices[:,:3]@matrix.T;vertices[:,3:]=vertices[:,3:]@matrix.T
        add((vertices,indices),(x,y,z),angle=angle,tint=tint)
    def stem():
        rod([(0,-7,-3),(1,-26,-3),(3,-37,-2)],1.4,green)
        petal(-7,-25,-3,3,10,.8,green)
    def radial(count,radius,length,width,z=0,tint=None,tilt=.20,phase=0.):
        for j in range(count):
            t=math.tau*j/count+phase
            petal(radius*math.cos(t),radius*math.sin(t)+5,z+.8*math.sin(j*2.4),width,length,t-math.pi/2,tint,tilt+.06*math.sin(j*1.7),.10*math.sin(j*2.2))
    if spec.category=='꽃':
        if recipe in ('bloom','disc','rosette','star_bloom'):
            if recipe=='rosette':
                from botanical_surface import cup_petal
                for layer in range(spec.layers+1):
                    count=max(4,n-layer) if spec.key=='rose' else n
                    radius=(h+14)*((.68 if spec.key=='lotus' else .78 if spec.key=='rose' else .74)**layer)
                    for j in range(count):
                        angle=j*math.tau/count+layer*.41+.035*math.sin(j*2.4+layer)
                        varied_radius=radius*(1+.045*math.sin(j*1.7+layer))
                        add(cup_petal(varied_radius,math.tau/count,9 if spec.key=='rose' else 5,style=spec.key,phase=j*1.3),
                            pos=(0,5,layer*4.6),angle=angle)
                orb((0,5,(spec.layers+1)*4.6),(2,2,1.4),color if spec.key=='rose' else gold)
            else:
                for layer in range(spec.layers):
                    radial(n+layer*2,14-layer*2,h-layer,w,layer*6.,tilt=.25+layer*.16,phase=layer*.43)
                orb((0,5,spec.layers*5.+2),(10 if recipe=='disc' else 4,)*2+(3,),(.045,.018,.004) if spec.key=='sunflower' else (.012,.009,.018) if spec.key in ('poppy','anemone') else gold)
            if spec.key in ('lily','plum','hibiscus'):
                for j in range(5):
                    t=j*math.tau/5
                    rod([(0,5,4),(4*math.cos(t),5+4*math.sin(t),15)],.55,gold)
                    orb((4*math.cos(t),5+4*math.sin(t),15),(1.1,)*3,gold)
        elif recipe=='cup':
            for j in range(n):
                t=j*math.tau/n
                petal(9*math.cos(t),9+9*math.sin(t),3+j*.3,w,h,t-math.pi/2,tilt=.95,twist=.08*math.sin(t))
        elif recipe in ('trumpet','funnel'):
            if recipe=='trumpet':radial(n,14,h,w)
            radius=12 if recipe=='trumpet' else w
            outer=[(2+(radius-2)*t**2.2,-12+30*t) for t in np.linspace(0,1,32)]
            inner=[(max(.4,r-.6),y) for r,y in reversed(outer)]
            vertices,indices=lathe(outer+inner+[outer[0]],64)
            theta=np.arctan2(vertices[:,2],vertices[:,0]);wave=1+.045*np.cos(n*theta)*np.clip((vertices[:,1]+12)/30,0,1)**3
            vertices[:,0]*=wave;vertices[:,2]*=wave
            matrix=rotation((1,0,0),math.pi/2-.18)
            vertices[:,:3]=vertices[:,:3]@matrix.T;vertices[:,3:]=vertices[:,3:]@matrix.T
            add((vertices,indices),pos=(0,6,0),tint=gold if recipe=='trumpet' else color)
        elif recipe=='spike':
            rod([(0,-31,0),(0,34,0)],1.5,green)
            for j in range(n):
                y=-5+j*34/max(1,n-1); side=1 if j%2 else -1
                if spec.key=='foxglove':
                    add(lathe([(0,5),(4,4),(5,-5),(7,-7),(5,-7),(3,2),(0,3)],20),pos=(side*7,y,1),angle=side*.35)
                else:
                    for floret in range(4):
                        phase=floret*math.tau/4+j*.7
                        petal(side*6+3*math.cos(phase),y+2*math.sin(phase),3+math.sin(phase),w*.65,h*.55,phase,tilt=.55)
                    orb((side*6,y,1),(2,2,2),green)
        elif recipe=='umbel':
            for j in range(n):
                t=j*2.399963; r=math.sqrt(j/n)*23
                for k in range(4):
                    angle=k*math.tau/4
                    petal(r*math.cos(t)+3*math.cos(angle),r*math.sin(t)+9+3*math.sin(angle),5+6*(1-r/23),3,4,angle)
        stem()
    elif spec.category=='열매':
        if spec.key=='coconut':
            add(fruit_mesh(spec),tint=(.16,.065,.023))
            for ex,ey in ((-.24,.32),(.24,.32),(0.,-.12)):
                ez=math.sqrt(1-ex*ex-ey*ey)
                orb((ex*w,ey*h,ez*w*.88-.45),(2.15,2.7,.32),(.009,.004,.001),angle=-ex*.6)
            rng=np.random.default_rng(32010)
            chunks=[];faces=[];offset=0
            for j in range(96):
                y=rng.uniform(-.92,.92);a=rng.uniform(0,math.tau);r=math.sqrt(1-y*y)
                normal=np.array((r*math.cos(a),y,r*math.sin(a)))
                start=normal*np.array((w,h,w*.88))
                tangent=np.cross(normal,(0,1,0));tangent/=max(np.linalg.norm(tangent),.001)
                length=rng.uniform(1.2,3.8)
                mesh=tube([start,start+normal*.6+tangent*length*.3,start+normal*.5+tangent*length],.055,False,4)
                chunks.append(mesh[0]);faces.append(mesh[1]+offset);offset+=len(mesh[0])
            add((np.concatenate(chunks),np.concatenate(faces)),tint=(.11,.045,.012))
        elif recipe in ('round_fruit','lobed_fruit','striped_fruit','crowned_fruit','pear'):
            add(fruit_mesh(spec))
            if recipe=='crowned_fruit':radial(n,5,5,2,h+1,green)
        elif recipe=='berry':
            # 작은 과립을 빈 입구 둘레와 아래쪽에 쌓아 산딸기와 검은딸기를 구분합니다.
            rows=7 if spec.key=='raspberry' else 8
            for row in range(rows):
                u=row/(rows-1)
                radius=(12.5*(1-.65*u*u) if spec.key=='raspberry' else 12*math.sin(.40+u*2.40))
                count=max(5,round(math.tau*radius/4.6))
                for j in range(count):
                    angle=(j+.5*(row%2))*math.tau/count
                    orb((radius*math.cos(angle),17-row*4.4,radius*math.sin(angle)),(2.7,2.8,2.7))
            if spec.key=='blackberry':orb((0,3,0),(7,16,7))
        elif recipe=='cluster':
            for row in range(spec.layers):
                count=max(1,n-row)
                for j in range(count):
                    t=j*math.tau/count
                    orb((w*count*.42*math.cos(t),(spec.layers/2-row)*h*1.35,w*count*.42*math.sin(t)),(w,h,w))
                    if spec.key=='blueberry':
                        # 분말층의 무광 과피 위에 오각 꽃받침과 움푹한 중심을 실제 부품으로 붙입니다.
                        cx=w*count*.42*math.cos(t);cy=(spec.layers/2-row)*h*1.35;cz=w*count*.42*math.sin(t)
                        orb((cx,cy,cz+w*.97),(2.7,2.7,.45),(.022,.025,.05))
                        for tip in range(5):
                            a=tip*math.tau/5
                            petal(cx+2.4*math.cos(a),cy+2.4*math.sin(a),cz+w*.99,.65,2.1,a-math.pi/2,(.045,.055,.09),tilt=.2)

            if recipe=='cluster':
                top=spec.layers*h*.675
                rod([(0,top-4,-2),(1,top+5,-2),(5,top+8,-1)],1.2,(.13,.065,.015))
                for side in (-1,1):rod([(1,top+2,-2),(side*w*n*.25,top-1,-1)],.6,(.09,.13,.015))
        elif recipe=='paired_fruit':
            for side in (-1,1):
                orb((side*13,-9,0),(w,h,w));rod([(side*13,1,0),(side*6,22,0),(0,30,0)],1,green)
        elif recipe=='banana':
            for j in range(n):
                points=[(j*6-6+12*math.cos(t),h*math.sin(t),j*3) for t in np.linspace(-1.2,1.2,40)]
                add(surface_tube(points,w,False,20))
                for point in (points[0],points[-1]):orb(point,(w,)*3)
        elif recipe=='citrus':
            add(fruit_mesh(spec))
        elif recipe in ('seeded_fruit','pineapple','dragonfruit'):
            body=fruit_mesh(spec);add(body)
            body_vertices=body[0].reshape(49,81,6)
            for j in range(0 if spec.key in ('papaya','pineapple') else n*spec.layers):
                t=j*2.399963
                sample=body_vertices[9+(j%7)*5,int((t%math.tau)/math.tau*80)]
                point,normal=sample[:3],sample[3:]
                if recipe=='dragonfruit':
                    mesh=petal_mesh(3.0,8,leaf=True)
                    scale_vertices,scale_indices=mesh;scale_vertices=scale_vertices.copy()
                    scale_vertices[:,2]+=2.5+.30*scale_vertices[:,1]
                    scale_vertices[:,4]-=.30*scale_vertices[:,5]
                    scale_vertices[:,3:]/=np.linalg.norm(scale_vertices[:,3:],axis=1)[:,None]
                    mesh=(scale_vertices,scale_indices)
                else:
                    mesh=_transformed(sphere,scale=(.65,1.15,.25))
                vertices,indices=mesh;vertices=vertices.copy()
                axis=np.cross((0,0,1),normal);length=np.linalg.norm(axis)
                matrix=rotation(axis,math.acos(float(np.clip(normal[2],-1,1)))) if length>1e-6 else np.eye(3)
                vertices[:,:3]=vertices[:,:3]@matrix.T+point+normal*.12
                vertices[:,3:]=vertices[:,3:]@matrix.T
                add((vertices,indices),tint=green if recipe=='dragonfruit' else (.42,.24,.055))
            if recipe=='pineapple':
                for j in range(7):petal((j-3)*3,h+7,0,2,12,(j-3)*.2,green)
        elif recipe=='starfruit':
            add(fruit_mesh(spec))
        if recipe not in ('paired_fruit','banana','cluster','berry','pineapple') and spec.key!='coconut':
            rod([(0,h*.8,0),(2,h+6,0),(5,h+9,1)],1.5,green)
            petal(8,h+4,1,3,9,-.8,green)
    elif spec.category=='잎':
        rod([(0,-32,0),(0,26,0)],1.2,green)
        if recipe in ('leaf','round_leaf','heart_leaf','lobed_leaf') or spec.key in ('maple','ivy','grape_leaf','fig_leaf','ginkgo','monstera'):
            from botanical_surface import leaf_surface
            add(leaf_surface(spec.key,w,h),pos=(0,3,0))
            if spec.key=='maple':
                for t in (-1.18,-.60,0.,.60,1.18):
                    rod([(0,3,3),(h*.62*math.sin(t),3+h*.62*math.cos(t),3.7)],.18,(.12,.18,.025))
            elif spec.key=='ginkgo':
                for t in np.linspace(-1.05,1.05,13):
                    rod([(0,3-h*.35,3),(h*.88*math.sin(t),3+h*(.88*math.cos(t)-.35),3.6)],.10,(.24,.26,.045))
            else:
                for y0 in (-16,-5,6,17):
                    for side in (-1,1):rod([(0,y0,3),(side*w*.25,y0+4,4.8)],.13,(.09,.20,.035))
        elif recipe in ('palmate','palm','compound'):
            for j in range(n):
                t=-1.25+2.5*j/max(1,n-1)
                petal(13*math.sin(t),7+13*math.cos(t),j*.65,w,h*.6,-t)
        elif spec.key=='pine':
            # count는 마디 수가 아니라 한 묶음의 바늘 수입니다.
            for cluster in range(spec.layers*3):
                y=-24+cluster*48/(spec.layers*3-1)
                phase=cluster*2.399963
                for needle in range(n):
                    a=phase+(needle-.5)*.16
                    tip=np.array((math.cos(a)*h*.70,y+11,math.sin(a)*h*.36))
                    base=np.array((0.,y,0.))
                    points=[base+(tip-base)*t+np.array((0,3*math.sin(math.pi*t),0)) for t in np.linspace(0,1,10)]
                    rod(points,.38)
        elif recipe in ('pinnate','fern','needle'):
            for j in range(n):
                y=-22+j*46/max(1,n-1)
                for side in (-1,1):
                    length=h*(.55+.45*math.sin((j+1)*math.pi/(n+1)))
                    if recipe=='needle':rod([(0,y,0),(side*length,y+7,1)],max(.55,w*.45))
                    else:petal(side*length*.45,y+3,0,w,length*.65,-side*.9)
        elif recipe=='fan':
            for j in range(n):
                t=-1.1+2.2*j/(n-1)
                petal(12*math.sin(t),5+12*math.cos(t),j*.45,5,h*.75,-t)
        elif recipe in ('split_leaf','lobed_leaf'):
            for j in range(n):
                y=-15+j*32/(n-1); length=w*(.4+.6*math.sin((j+1)*math.pi/(n+1)))
                for side in (-1,1):petal(side*length*.5,y,0,4,length,-side*1.0)
        elif recipe=='heart_leaf':
            petal(-w*.32,5,0,w*.65,h*.8,-.35);petal(w*.32,5,0,w*.65,h*.8,.35)
        else:petal(0,3,0,w,h,0)
        if recipe not in ('palmate','palm','compound','pinnate','fern','needle','fan','split_leaf','lobed_leaf','heart_leaf'):
            def leaf_front(x,y):
                unit_y=(y-3)/h
                return h*(.13*(1-unit_y*unit_y)-.055*unit_y)+.20*w*(x/w)**2+.55
            ys=np.linspace(-h*.90+3,h*.90+3,17)
            rod([(0,y,leaf_front(0,y)) for y in ys],.20,(.12,.22,.035))
            for j in range(1,9):
                y=-h*.65+3+j*h*.15
                length=w*.72*math.sqrt(max(0,1-((y-3)/h)**2))
                for side in (-1,1):
                    points=[(side*length*t,y+h*.13*t,leaf_front(side*length*t,y+h*.13*t)) for t in np.linspace(0,1,7)]
                    rod(points,.10,(.12,.22,.035))
    else:
        silver=(.65,.72,.78)
        if recipe in ('bowed','guitar','lute'):
            add(instrument_body(w,h*.85,bowed=recipe=='bowed',lute=recipe=='lute'),pos=(0,-10,0))
            neck_bottom=h*.85-13;neck_top=neck_bottom+23
            add(box((4.5,25,3.5),.65,4),pos=(0,(neck_bottom+neck_top)/2,3),tint=(.025,.012,.007))
            add(box((7,8,4),.8,4),pos=(0,neck_top+4,2))
            if recipe=='bowed':
                for side in (-1,1):rod([(side*7,-4,5),(side*5,-8,5.5),(side*7,-13,5),(side*5,-17,5)],.55,(.012,.006,.003))
            else:orb((0,-5,5.9),(w*.22,h*.19,.18),(.008,.004,.002))
            add(box((w*.5,2,2),.3,3),pos=(0,-h*.5-10,6),tint=(.065,.027,.009))
            for j in range(min(n,8)):rod([((j-(n-1)/2)*.42,-h*.5-10,7),((j-(n-1)/2)*.42,neck_top+4,5)],.12,silver)
            if spec.key in ('cello','bass'):rod([(0,-h-10,0),(0,-h-18,0)],.8,silver)
        elif recipe in ('harp','lyre'):
            if recipe=='harp':points=[(-w,-h,0),(-w*.7,h,0),(w,h*.4,0),(-w,-h,0)]
            else:points=[(-w,h,0),(-w,-h*.5,0),(0,-h,0),(w,-h*.5,0),(w,h,0),(-w,h,0)]
            rod(points,2.5)
            for j in range(n):
                x=-w*.65+j*w*1.3/(n-1)
                rod([(x,-h*.65,0),(x,h*(.8-.4*j/n),0)],.35,silver)
        elif recipe in ('piano','accordion','bars'):
            add(box((w*2,h*1.6,9),3,5),tint=dark)
            if recipe=='piano':orb((w*.5,h*.4,-2),(w*.7,h,5))
            for j in range(n):
                x=-w+(j+.5)*2*w/n
                length=h*(1.3-.65*j/n) if recipe=='bars' else h*.6
                add(box((w*1.6/n,length,3),.5,2),pos=(x,-h*.25,7),tint=(.78,.75,.65) if recipe!='bars' else color,metal=0.)
                if recipe=='piano' and j%7 not in (2,6):
                    add(box((w*.85/n,length*.55,2),.3,2),pos=(x+w/n,-h*.10,9.4),tint=(.008,.008,.01),metal=0.)
                if recipe=='accordion':rod([(x,-h,0),(x,h,0)],1.4,color)
        elif recipe in ('flute','reed'):
            rod([(0,-h,0),(0,h,0)],w)
            for j in range(n):orb((w*.6,-h*.6+j*h*1.2/n,w),(1.7,1.7,1),silver)
            if recipe=='reed':add(lathe([(w,-h+7),(w*2,-h),(w*2-1,-h),(w-1,-h+7)],24))
        elif recipe in ('sax','brass','horn'):
            if recipe=='horn':points=[(w*math.cos(t),h*.75*math.sin(t),0) for t in np.linspace(0,math.tau*1.6,55)]
            else:points=[(-w,h,0),(-w,-h*.5,0),(-w*.4,-h,0),(w,-h*.6,0),(w,h*.5,0)]
            rod(points,3 if recipe=='sax' else 2.3)
            add(lathe([(3,-8),(5,0),(12,10),(11,11),(4,0),(2,-8)],24),pos=(w,h*.6,0),tint=color)
            for j in range(min(n,7)):orb((-w+5,-h*.4+j*6,3),(2,2,2),silver)
        elif recipe in ('drum','bowl_drum','tambourine'):
            count=2 if spec.key=='bongo' else 1
            for j in range(count):
                x=(j-(count-1)/2)*w*1.7
                profile=[(0,-h),(w*.7,-h),(w,h),(0,h)] if recipe=='bowl_drum' else [(0,-h),(w,-h),(w,h),(0,h)]
                add(lathe(profile,64),pos=(x,0,0),metal=1. if spec.key=='snare' else None)
                add(lathe([(0,0),(w*.94,0),(w*.94,.35),(0,.35)],64),pos=(x,h+.15,0),tint=(.65,.59,.46),metal=0.,rough=.75)
                for k in range(n if count==1 else 6):
                    t=k*math.tau/(n if count==1 else 6)
                    orb((x+w*math.cos(t),0,w*math.sin(t)),(2,3,2),silver)
        elif recipe=='triangle':rod([(-w,-h*.5,0),(0,h,0),(w,-h*.5,0),(-w*.7,-h*.5,0)],2,silver)
        elif recipe=='bell':
            add(lathe([(0,-h),(w,-h),(w*.6,-h*.4),(w*.3,h*.4),(0,h*.55)],32))
            rod([(0,h*.5,0),(0,h+10,0)],2,dark)
        else:raise ValueError('지원하지 않는 실제 대상 형상: '+recipe)
    return parts


@lru_cache(maxsize=1)
def _ring_geometry():
    """날짜와 무관한 세 링만 읽기 전용 배열로 한 번 생성합니다."""
    rings=[]
    ts=np.linspace(0,math.tau,128,endpoint=False)
    for radius in (49,56,62):
        vertices,indices=tube([(radius*math.cos(t),radius*math.sin(t),0) for t in ts],2.5,True,12)
        vertices.setflags(write=False); indices.setflags(write=False)
        rings.append((vertices,indices))
    return tuple(rings)


def build_geometry(design, material_specs=None):
    """날짜 매핑의 주제 하나만 충분한 크기로 표시하며 보조물과 고리는 만들지 않습니다."""
    from calendar_specials import subject_for_id
    subject=subject_for_id(design.object_id)
    if subject.recipe!=design.shape_recipe:raise ValueError('대상과 형상 규칙이 일치하지 않습니다.')
    accent=tuple((int(design.accent[i:i+2],16)/255)**2.2 for i in (1,3,5))
    if subject.category=='열매':
        import colorsys
        hue,saturation,value=colorsys.rgb_to_hsv(*accent)
        accent=colorsys.hsv_to_rgb(hue,min(.96,saturation*1.35),value*.85)
    local_materials=[] if material_specs is not None else None
    parts=(_object_geometry(subject,accent,local_materials) if local_materials is not None and subject.category in ('꽃','잎','열매')
           else _object_geometry(subject,accent))
    points=np.concatenate([mesh[0][:,:3] for mesh,*_ in parts])
    low,high=points.min(axis=0),points.max(axis=0)
    center=(low+high)/2
    size=96/max(high-low)*(.96+.04*design.year_variant)
    angle=(design.date.day-16)*.006
    result=[]
    if material_specs is not None:
        global_matrix=np.eye(4);global_matrix[:3,:3]=rotation((0,0,1),angle)*size
        global_matrix[:3,3]=-global_matrix[:3,:3]@center
        inverse=np.linalg.inv(global_matrix)
        material_specs.extend([{'enabled':row['enabled'],'mapping':row['mapping']@inverse} for row in local_materials]
                              if local_materials else [{'enabled':False,'mapping':np.eye(4)} for _ in parts])
    for mesh,base,metal,rough in parts:
        vertices,indices=mesh
        vertices=vertices.copy();vertices[:,:3]-=center
        result.append((_transformed((vertices,indices),scale=(size,)*3,angle=angle),base,metal,rough))
    return result


def matrices(elapsed):
    if type(elapsed) not in (int,float):raise ValueError('모션 시각은 유한한 숫자여야 합니다.')
    try:valid=math.isfinite(elapsed)
    except OverflowError:valid=False
    if not valid:raise ValueError('모션 시각은 유한한 숫자여야 합니다.')
    phase=math.tau*(elapsed%PERIOD)/PERIOD
    center=np.eye(4); center[:3,:3]=rotation((0,1,0),.20*math.sin(phase))@rotation((1,0,0),.10*math.sin(phase+.5)); center[1,3]=1.4*math.sin(phase)
    result=[center]
    # 서로 다른 축과 정수 회전수로 12/6/4초 완전 회전 및 공통 루프를 유지합니다.
    for index,axis in enumerate(((.6,1,.3),(-.3,1,.4),(.4,-.8,1))):
        matrix=np.eye(4); matrix[:3,:3]=rotation(axis,(1,-2,3)[index]*phase)@rotation((0,0,1),(.2,1.2,-.6)[index])@rotation((1,0,0),(.8,-.7,1.1)[index])
        result.append(matrix)
    return result


def _crescent_geometry():
    """평면 그림이 아닌 앞뒤 면과 곡면 옆면을 갖는 초승달 메시입니다."""
    outer = [(22 * math.cos(t), 22 * math.sin(t)) for t in np.linspace(math.pi / 3, 5 * math.pi / 3, 49)]
    angle = math.atan2(-outer[-1][1], outer[-1][0] - 14)
    inner = [(14 + math.hypot(3, outer[0][1]) * math.cos(t),
              math.hypot(3, outer[0][1]) * math.sin(t))
             for t in np.linspace(-angle, angle - math.tau, 49)]
    points = outer + inner
    vertices, indices = [], []
    for z, nz in ((5, 1), (-5, -1)):
        start = len(vertices)
        vertices.append((-13, 0, z, 0, 0, nz))
        vertices.extend((x, y, z, 0, 0, nz) for x, y in points)
        for i in range(len(points)):
            indices.extend((start, start + 1 + i, start + 1 + (i + 1) % len(points)))
    for i, (x, y) in enumerate(points):
        nx, ny = points[(i + 1) % len(points)]
        normal = np.array((ny - y, x - nx, 0.), dtype=float)
        if np.linalg.norm(normal) < 1e-8:
            continue
        normal /= np.linalg.norm(normal)
        start = len(vertices)
        vertices.extend((a, b, z, *normal) for a, b, z in ((x, y, -5), (nx, ny, -5), (nx, ny, 5), (x, y, 5)))
        indices.extend((start, start + 1, start + 2, start, start + 2, start + 3))
    return finish(vertices, indices)


def build_observatory_geometry(scene):
    """모델 코어·입자·용기·명시 작업자 위성을 실제 삼각형 부품으로 만듭니다."""
    from observatory_scene import normalize_scene, model_family, particle_count
    scene = normalize_scene(scene)
    family = model_family(scene['model'])
    parts = []
    silver = (.67, .74, .79)
    def add(mesh, color=silver, metal=1., rough=.23, kind='core', index=0):
        parts.append((mesh, color, metal, rough, kind, index))
    if family == 'sol':
        add(sphere_mesh(16, 32, 20), (.82, .50, .13), .78, .25)
        for i in range(12):
            angle = i * math.tau / 12
            add(_transformed(lathe([(0, -5), (2.4, -4), (1.7, 3), (0, 7)], 10),
                             (22 * math.cos(angle), 22 * math.sin(angle), 0), angle=angle - math.pi / 2),
                (.90, .63, .20), .85, .25)
    elif family == 'astra':
        add(lathe([(0, -25), (16, -3), (14, 6), (0, 25)], 6, False), (.49, .35, .78), .8, .20)
    elif family == 'terra':
        add(sphere_mesh(19, 36, 24), (.14, .47, .44), .65, .27)
        for angle in (0, math.pi / 3, 2 * math.pi / 3):
            mesh = tube([(19.4 * math.cos(t), 19.4 * math.sin(t), 0) for t in np.linspace(0, math.tau, 64, endpoint=False)], .65, True, 8)
            vertices, indices = mesh
            vertices[:, :3] = vertices[:, :3] @ rotation((0, 1, 0), angle).T
            vertices[:, 3:] = vertices[:, 3:] @ rotation((0, 1, 0), angle).T
            add((vertices, indices), (.38, .78, .66), .9, .20)
    elif family == 'luna':
        add(_crescent_geometry(), (.68, .72, .86), .87, .22)
    else:
        add(sphere_mesh(17, 24, 16), (.44, .49, .52), .85, .30)
    for index, mesh in enumerate(_ring_geometry()):
        add(mesh, kind='ring', index=index)
    count = particle_count(scene['effort'])
    if count:
        chunks, indices, offset = [], [], 0
        for i in range(count):
            angle = i * 2.39996323
            z = 24 * (2 * (i + .5) / count - 1)
            radius = math.sqrt(max(0, 37 ** 2 - z ** 2))
            vertices, ix = _transformed(sphere_mesh(1.1, 8, 5), (radius * math.cos(angle), radius * math.sin(angle), z))
            chunks.append(vertices); indices.append(ix + offset); offset += len(vertices)
        add((np.concatenate(chunks), np.concatenate(indices)), (.46, .80, .74), .75, .22, 'particles')
    colors = {'running': (.20, .73, .55), 'working': (.20, .73, .55), 'assigned': (.24, .70, .62),
              'resumed': (.24, .70, .62), 'waiting': (.86, .65, .22), 'waiting_user': (.86, .65, .22),
              'completed': (.32, .57, .86), 'done': (.32, .57, .86), 'error': (.86, .24, .26),
              'retrying': (.94, .46, .18), 'retry': (.94, .46, .18)}
    for index, agent in enumerate(scene['agents']):
        add(sphere_mesh(3.4 if agent['pinned'] else 2.8, 16, 10),
            colors.get(agent['status'], silver), .75, .24, 'agent', index)
    for y in (-49, -29):
        add(tube([(9 * math.cos(t), y, 12 + 9 * math.sin(t)) for t in np.linspace(0, math.tau, 48, endpoint=False)], .7, True, 8), kind='vessel')
    for x, z in ((-9, 12), (9, 12), (0, 3), (0, 21)):
        add(tube([(x, -49, z), (x, -29, z)], .55, False, 8), kind='vessel')
    fraction = scene['usage_fraction']
    if fraction is None:
        add(_transformed(sphere_mesh(2.2, 12, 8), (0, -39, 12)), (.45, .49, .53), .4, .4, 'usage_unknown')
    elif fraction > 0:
        height = 18 * fraction
        add(_transformed(lathe([(0, 0), (7.8, 0), (7.8, height), (0, height)], 32), (0, -48, 12)),
            (.13, .64, .48), .35, .25, 'usage_fill')
    return parts


class CalendarRenderer:
    """컨텍스트를 만든 스레드에서만 사용하고 현재 날짜의 버퍼만 보유합니다."""
    def __init__(self,size=384):
        if type(size) is int and 32<=size<=768:
            dimensions=(size,size)
        elif type(size) is tuple and len(size)==2 and all(type(v) is int for v in size) and size==(3840,2160):
            dimensions=size
        else:raise ValueError('렌더 크기는32~768 정수 또는3840×2160이어야 합니다.')
        width,height=dimensions
        self.thread_id=threading.get_ident(); self.size=size; self.dimensions=dimensions; self.ctx=None; self.resources=[]; self.vaos=[]; self.buffers=[]; self.parts=[]; self.design=None
        self.output_resources=[]; self.output_size=0; self.output=None; self.observatory_key=None
        self.species_texture=None;self.species_key=None;self.material_specs=[];self.atlas_path=None;self.atlas_image=None
        try:
            self.ctx=moderngl.create_standalone_context(require=330)
            vertex_shader,fragment_shader=organic_shaders(VERTEX,FRAGMENT)
            self.program=self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader); self.resources.append(self.program)
            import sys
            asset_root=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parents[1]))/'assets'
            from material_catalog32 import load_catalog
            self.material_catalog=load_catalog(asset_root/'materials')
            material=QImage(str(asset_root/'materials/코코넛_껍질_섬유.png')).convertToFormat(QImage.Format.Format_RGBA8888)
            if material.isNull():raise RuntimeError('코코넛 표면 재질을 읽을 수 없습니다.')
            self.shell_texture=self.ctx.texture((material.width(),material.height()),4,bytes(material.constBits()))
            self.resources.append(self.shell_texture);self.shell_texture.build_mipmaps()
            self.shell_texture.filter=(moderngl.LINEAR_MIPMAP_LINEAR,moderngl.LINEAR)
            self.shell_texture.repeat_x=True;self.shell_texture.repeat_y=True
            self.program['shell_texture'].value=1
            self.detail_textures=[]
            for name in ('과피_미세결_높이맵.png','식물_미세결_높이맵.png'):
                heightmap=QImage(str(asset_root/'materials'/name)).convertToFormat(QImage.Format.Format_RGBA8888)
                if heightmap.isNull():raise RuntimeError('표면 높이 재질을 읽을 수 없습니다: '+name)
                texture=self.ctx.texture((heightmap.width(),heightmap.height()),4,bytes(heightmap.constBits()))
                self.resources.append(texture);self.detail_textures.append(texture);texture.build_mipmaps()
                texture.filter=(moderngl.LINEAR_MIPMAP_LINEAR,moderngl.LINEAR);texture.repeat_x=True;texture.repeat_y=True
            self.color=self.ctx.renderbuffer(dimensions,components=4,samples=4); self.resources.append(self.color)
            self.depth=self.ctx.depth_renderbuffer(dimensions,samples=4); self.resources.append(self.depth)
            self.target=self.ctx.framebuffer([self.color],self.depth); self.resources.append(self.target)
            self.texture=self.ctx.texture(dimensions,components=4,dtype='f1'); self.resources.append(self.texture)
            self.texture.filter=(moderngl.LINEAR,moderngl.LINEAR)
            self.resolved=self.ctx.framebuffer([self.texture]); self.resources.append(self.resolved)
            self.downsample_program=self.ctx.program(vertex_shader='''#version 330
                out vec2 uv;
                uniform vec2 crop_scale;
                void main() {
                    vec2 p=vec2((gl_VertexID<<1)&2,gl_VertexID&2);
                    uv=(p-0.5)*crop_scale+0.5;
                    gl_Position=vec4(p*2.0-1.0,0.0,1.0);
                }''',fragment_shader='''#version 330
                uniform sampler2D source_image;
                in vec2 uv;
                out vec4 color;
                void main() { color=texture(source_image,uv); }
                '''); self.resources.append(self.downsample_program)
            self.downsample_program['crop_scale'].value=(min(width,height)/width,min(width,height)/height)
            self.downsample_vao=self.ctx.vertex_array(self.downsample_program,[]); self.resources.append(self.downsample_vao)
            self.set_output_size(size if type(size) is int else 384)
            self.ctx.enable(moderngl.DEPTH_TEST)
            near,far,camera,extent=1.,1200.,700.,69.
            projection=np.array([[camera/extent*height/width,0,0,0],[0,camera/extent,0,0],[0,0,(far+near)/(near-far),2*far*near/(near-far)],[0,0,-1,0]],dtype='f4')
            view=np.eye(4,dtype='f4'); view[2,3]=-camera
            self.program['view_projection'].write((projection@view).T.astype('f4').tobytes()); self.program['camera'].value=(0.,0.,camera)
        except Exception:
            self.close(); raise

    def _assert_thread(self):
        if threading.get_ident()!=self.thread_id:raise RuntimeError('GPU 컨텍스트는 생성 스레드에서만 사용할 수 있습니다.')

    def set_output_size(self,size):
        """원본 타깃은 유지하고 중앙 정사각형의 GPU 전달 크기만 변경합니다."""
        self._assert_thread()
        if type(size) is not int or not 32<=size<=2160:raise ValueError('전달 크기는32~2160 정수여야 합니다.')
        if self.output_size==size:return
        for resource in reversed(self.output_resources):resource.release()
        self.output_resources=[]
        texture=self.ctx.texture((size,size),4); self.output_resources.append(texture)
        self.output=self.ctx.framebuffer([texture]); self.output_resources.append(self.output)
        self.output_size=size

    def _set_species_texture(self,key):
        if key==self.species_key:return
        if self.species_texture is not None:
            self.species_texture.release();self.resources.remove(self.species_texture);self.species_texture=None
        entry=self.material_catalog.get(key)
        if entry is not None and entry['enabled']:
            from material_catalog32 import extract_tile
            if self.atlas_path!=entry['path']:
                self.atlas_image=QImage(str(entry['path'])).convertToFormat(QImage.Format.Format_RGBA8888)
                self.atlas_path=entry['path']
            tile=extract_tile(self.atlas_image,entry['index'])
            self.species_texture=self.ctx.texture((tile.width(),tile.height()),4,bytes(tile.constBits()))
            self.resources.append(self.species_texture);self.species_texture.build_mipmaps()
            self.species_texture.filter=(moderngl.LINEAR_MIPMAP_LINEAR,moderngl.LINEAR)
            self.species_texture.repeat_x=False;self.species_texture.repeat_y=False
        self.species_key=key

    def set_date(self,value,country='KR',city_ref=None):
        self._assert_thread(); design=design_for_date(value,country,city_ref)
        if self.design==design:return
        self._clear_meshes(); self.material_specs=[];self.parts=build_geometry(design,self.material_specs)
        self._set_species_texture(design.object_id)
        for (vertices,indices),_,_,_ in self.parts:
            vertex=self.ctx.buffer(vertices.tobytes()); self.buffers.append(vertex)
            index=self.ctx.buffer(indices.tobytes()); self.buffers.append(index)
            self.vaos.append(self.ctx.vertex_array(self.program,[(vertex,'3f 3f','in_position','in_normal')],index))
        self.design=design; self.observatory_key=None

    def _draw_observatory(self, scene, elapsed):
        from observatory_scene import normalize_scene, scene_time, world_matrix, agent_world_positions
        self._assert_thread()
        scene = normalize_scene(scene); elapsed = scene_time(scene, elapsed)
        key = (scene['model'], scene['effort'], scene['usage_fraction'],
               tuple((a['target'], a['status'], a['pinned']) for a in scene['agents']))
        if self.observatory_key != key:
            self._clear_meshes(); self.parts = build_observatory_geometry(scene)
            for (vertices, indices), *_ in self.parts:
                vertex = self.ctx.buffer(vertices.tobytes()); self.buffers.append(vertex)
                index = self.ctx.buffer(indices.tobytes()); self.buffers.append(index)
                self.vaos.append(self.ctx.vertex_array(self.program, [(vertex, '3f 3f', 'in_position', 'in_normal')], index))
            self.observatory_key = key
        self.program['species_enabled'].value=0
        self.program['organic_kind'].value=0
        self.program['skin_kind'].value=0
        self.program['detail_strength'].value=0.
        self.program['translucency'].value=0.
        world = np.asarray(world_matrix(scene), dtype=float)
        agents = agent_world_positions(scene, elapsed)
        transition = scene['transition']; blend = transition * transition * (3 - 2 * transition)
        self.ctx.enable(moderngl.DEPTH_TEST); self.target.use(); self.target.clear(0, 0, 0, 0, depth=1)
        for index, (_, color, metal, rough, kind, part_index) in enumerate(self.parts):
            transform = np.eye(4)
            if kind == 'ring':
                axis = ((.6, 1, .3), (-.3, 1, .4), (.4, -.8, 1))[part_index]
                phase = math.tau * elapsed / 12 * (1, -2, 3)[part_index] * blend
                transform[:3, :3] = rotation(axis, phase) @ rotation((1, 0, 0), (.8, -.7, 1.1)[part_index] * blend)
            elif kind == 'agent':
                transform[:3, 3] = agents[part_index]['position']
            elif kind == 'particles':
                transform[:3, :3] = rotation((.2, 1, .3), elapsed * .16)
            elif kind == 'core':
                transform[:3, :3] = rotation((0, 1, 0), .10 * math.sin(elapsed)) * (.78 + .22 * blend)
                transform[1, 3] = 1.2 * math.sin(elapsed)
            transform = world @ transform
            self.program['model'].write(transform.T.astype('f4').tobytes())
            self.program['metallic'].value = metal; self.program['base_color'].value = color; self.program['roughness'].value = rough
            self.vaos[index].render(moderngl.TRIANGLES)
        self.ctx.copy_framebuffer(self.resolved, self.target)

    def render_observatory(self, scene, elapsed=0):
        """같은 컨텍스트·4K 타깃과 깊이 버퍼에서 관측소를 렌더합니다."""
        self._draw_observatory(scene, elapsed)
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.output.use(); self.texture.use(location=0)
        self.downsample_vao.render(moderngl.TRIANGLES, vertices=3)
        return self._image(self.output, self.output_size, self.output_size)

    def _draw(self,value,elapsed,country='KR',city_ref=None):
        self._assert_thread(); transforms=matrices(elapsed); self.set_date(value,country,city_ref)
        from calendar_specials import subject_for_id
        subject=subject_for_id(self.design.object_id)
        self.program['organic_kind'].value=2 if subject.key=='coconut' else (1 if subject.category in ('꽃','열매','잎','특집') else 3)
        self.program['skin_kind'].value={'watermelon':1,'melon':2,'kiwi':3,'pineapple':4}.get(subject.key,0)
        plant=subject.category in ('꽃','잎')
        self.detail_textures[1 if plant else 0].use(location=2)
        self.program['detail_texture'].value=2
        self.program['detail_strength'].value=.035 if plant else {'orange':.23,'mandarin':.20,'lemon':.18,'lime':.16,'kiwi':.27,'apple':.045,'peach':.085}.get(subject.key,.075)
        self.program['translucency'].value=.8 if plant else 0.
        self.shell_texture.use(location=1)
        self.program['species_texture'].value=3
        if self.species_texture is not None:self.species_texture.use(location=3)
        self.program['species_projection'].value=1 if subject.category=='열매' else 0
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.target.use(); self.target.clear(0,0,0,0,depth=1)
        for index,(_,color,metal,rough) in enumerate(self.parts):
            metadata=self.material_specs[index]
            self.program['species_enabled'].value=int(self.species_texture is not None and metadata['enabled'])
            self.program['species_mapping'].write(metadata['mapping'].T.astype('f4').tobytes())
            transform=transforms[0]
            self.program['model'].write(transform.T.astype('f4').tobytes())
            self.program['metallic'].value=metal; self.program['base_color'].value=color; self.program['roughness'].value=rough
            self.vaos[index].render(moderngl.TRIANGLES)
        self.ctx.copy_framebuffer(self.resolved,self.target)

    def _image(self,framebuffer,width,height):
        raw=framebuffer.read(components=4,alignment=1)
        # MSAA 결과는 사전곱 알파입니다. 복사해 GPU 버퍼 수명에서 분리합니다.
        image=QImage(raw,width,height,width*4,QImage.Format.Format_RGBA8888_Premultiplied).copy().mirrored(False,True)
        return image

    def render(self,value,elapsed=0,country='KR',city_ref=None):
        self._draw(value,elapsed,country,city_ref)
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.output.use(); self.texture.use(location=0)
        self.downsample_vao.render(moderngl.TRIANGLES,vertices=3)
        return self._image(self.output,self.output_size,self.output_size)

    def render_original(self,value,elapsed=0,country='KR',city_ref=None):
        """검증·내보내기 때만 실제 직사각형 원본 전체를 CPU로 읽습니다."""
        self._draw(value,elapsed,country,city_ref)
        return self._image(self.resolved,*self.dimensions)

    def _clear_meshes(self):
        for value in reversed(self.vaos):value.release()
        for value in reversed(self.buffers):value.release()
        self.vaos.clear(); self.buffers.clear(); self.parts=[]; self.design=None; self.observatory_key=None

    def close(self):
        self._assert_thread(); self._clear_meshes()
        for value in reversed(self.output_resources):value.release()
        self.output_resources.clear(); self.output=None; self.output_size=0
        for value in reversed(self.resources):value.release()
        self.resources.clear()
        self.species_texture=None;self.species_key=None;self.atlas_image=None;self.atlas_path=None;self.material_specs=[]
        if self.ctx is not None:self.ctx.release(); self.ctx=None


def render_date(value,elapsed=0.0,size=384):
    """미리보기와 직접 검증용 동기 렌더입니다. 앱은 공유 작업 스레드를 사용합니다."""
    renderer=CalendarRenderer(size)
    try:return renderer.render(value,elapsed)
    finally:renderer.close()
