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


def _object_geometry(spec, color):
    """대상 이름에 연결된 주요 구조를 실제 삼각형 부품으로 구성합니다."""
    parts=[]
    sphere=sphere_mesh(1,20,12)
    green=(.22,.43,.29); gold=(.68,.48,.16); dark=(.11,.12,.17)
    n=spec.count; w=spec.width; h=spec.length; recipe=spec.recipe
    def add(mesh,pos=(0,0,0),scale=(1,1,1),angle=0,tint=None):
        parts.append((_transformed(mesh,pos,scale,angle),tint or color,.52,.31))
    def orb(pos,scale,tint=None,angle=0):add(sphere,pos,scale,angle,tint)
    def rod(points,radius=1.2,tint=None,closed=False):add(tube(points,radius,closed,8),tint=tint)
    def petal(x,y,z,width,length,angle,tint=None):orb((x,y,z),(width,length,2.5),tint,angle)
    def stem():
        rod([(0,-7,-3),(1,-26,-3),(3,-37,-2)],1.4,green)
        petal(-7,-25,-3,3,10,.8,green)
    def radial(count,radius,length,width,z=0,tint=None):
        for j in range(count):
            t=math.tau*j/count
            petal(radius*math.cos(t),radius*math.sin(t)+5,z,width,length,t-math.pi/2,tint)
    if spec.category=='꽃':
        if recipe in ('bloom','disc','rosette','star_bloom'):
            for layer in range(spec.layers):
                radial(n+layer*2,max(4,14-layer*2),h-layer*1.1,w,layer*3)
            orb((0,5,spec.layers*3+2),(10 if recipe=='disc' else 4,)*2+(3,),dark if spec.key in ('sunflower','poppy','anemone') else gold)
            if spec.key in ('lily','plum','hibiscus'):
                for j in range(5):
                    t=j*math.tau/5
                    rod([(0,5,4),(4*math.cos(t),5+4*math.sin(t),15)],.55,gold)
                    orb((4*math.cos(t),5+4*math.sin(t),15),(1.1,)*3,gold)
        elif recipe=='cup':
            for j in range(n):
                t=j*math.tau/n
                orb((9*math.cos(t),9,9*math.sin(t)),(w,h,3),angle=-.18*math.cos(t))
        elif recipe in ('trumpet','funnel'):
            if recipe=='trumpet':radial(n,14,h,w)
            add(lathe([(0,-12),(3,-11),(5,1),(12 if recipe=='trumpet' else w,16),(11 if recipe=='trumpet' else w-2,18),(4,1),(0,-8)],32),pos=(0,6,7),scale=(1,1,1),angle=-.18,tint=gold if recipe=='trumpet' else color)
        elif recipe=='spike':
            rod([(0,-31,0),(0,34,0)],1.5,green)
            for j in range(n):
                y=-5+j*34/max(1,n-1); side=1 if j%2 else -1
                if spec.key=='foxglove':
                    add(lathe([(0,5),(4,4),(5,-5),(7,-7),(5,-7),(3,2),(0,3)],20),pos=(side*7,y,1),angle=side*.35)
                else:orb((side*(5+(n-j)*.3),y,2),(w,h,4))
        elif recipe=='umbel':
            for j in range(n):
                t=j*2.399963; r=math.sqrt(j/n)*23
                for k in range(4):
                    angle=k*math.tau/4
                    petal(r*math.cos(t)+3*math.cos(angle),r*math.sin(t)+9+3*math.sin(angle),5+6*(1-r/23),3,4,angle)
        stem()
    elif spec.category=='열매':
        if recipe in ('round_fruit','lobed_fruit','striped_fruit','crowned_fruit'):
            if recipe=='lobed_fruit':
                for j in range(n):
                    t=math.tau*j/n; orb((w*.24*math.cos(t),0,w*.24*math.sin(t)),(w*.78,h,w*.78))
            else:orb((0,0,0),(w,h,w*.8))
            if recipe=='striped_fruit':
                for j in range(n):
                    t=math.tau*j/n
                    rod([(w*math.sin(u)*math.cos(t),h*math.cos(u),w*.81*math.sin(u)*math.sin(t)) for u in np.linspace(.15,math.pi-.15,20)],.7,green)
            if recipe=='crowned_fruit':
                radial(n,5,5,2,h+1,green)
        elif recipe=='pear':
            add(lathe([(0,-h),(w*.6,-h*.8),(w,-h*.2),(w*.7,h*.35),(w*.28,h*.8),(0,h)],32))
        elif recipe in ('cluster','berry'):
            for row in range(spec.layers):
                count=max(1,n-row)
                for j in range(count):
                    t=j*math.tau/count
                    orb((w*count*.42*math.cos(t),(spec.layers/2-row)*h*1.35,w*count*.42*math.sin(t)),(w,h,w))
        elif recipe=='paired_fruit':
            for side in (-1,1):
                orb((side*13,-9,0),(w,h,w));rod([(side*13,1,0),(side*6,22,0),(0,30,0)],1,green)
        elif recipe=='banana':
            for j in range(n):
                rod([(j*6-6+12*math.cos(t),h*math.sin(t),j*3) for t in np.linspace(-1.2,1.2,24)],w)
        elif recipe=='citrus':
            orb((0,0,-4),(w,h,w*.60))
            # 정면의 방사 단면은 감귤과 키위의 구조를 보여줍니다.
            for j in range(n):
                t=math.tau*j/n
                rod([(0,0,w*.60),(w*.82*math.cos(t),h*.82*math.sin(t),w*.50)],.65,(.78,.72,.50))
        elif recipe in ('seeded_fruit','pineapple','dragonfruit'):
            add(lathe([(0,-h),(w*.6,-h*.55),(w,h*.15),(w*.75,h*.75),(0,h)],32))
            for j in range(n):
                t=j*2.399963; y=-h*.55+(j%7)*h*.18
                r=w*math.sqrt(max(.1,1-(y/h)**2))
                if recipe=='dragonfruit':petal(r*math.cos(t),y,r*math.sin(t),3,8,t,green)
                else:orb((r*math.cos(t),y,r*math.sin(t)),(1.2,2,1.2),gold)
            if recipe=='pineapple':
                for j in range(7):petal((j-3)*3,h+7,0,2,12,(j-3)*.2,green)
        elif recipe=='starfruit':
            for j in range(5):
                t=j*math.tau/5
                orb((w*.55*math.cos(t),0,w*.55*math.sin(t)),(w*.4,h,w*.4))
        if recipe not in ('paired_fruit','banana'):
            rod([(0,h*.8,0),(2,h+6,0),(5,h+9,1)],1.5,green)
            petal(8,h+4,1,3,9,-.8,green)
    elif spec.category=='잎':
        rod([(0,-32,0),(0,26,0)],1.2,green)
        if recipe in ('palmate','palm','compound'):
            for j in range(n):
                t=-1.25+2.5*j/max(1,n-1)
                petal(13*math.sin(t),7+13*math.cos(t),j*.12,w,h*.6,-t)
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
                petal(12*math.sin(t),5+12*math.cos(t),0,5,h*.75,-t)
        elif recipe in ('split_leaf','lobed_leaf'):
            for j in range(n):
                y=-15+j*32/(n-1); length=w*(.4+.6*math.sin((j+1)*math.pi/(n+1)))
                for side in (-1,1):petal(side*length*.5,y,0,4,length,-side*1.0)
        elif recipe=='heart_leaf':
            petal(-w*.32,5,0,w*.65,h*.8,-.35);petal(w*.32,5,0,w*.65,h*.8,.35)
        else:orb((0,3,0),(w,h,2.4))
        for j in range(1,min(n,12)):
            y=-16+j*32/min(n,12)
            for side in (-1,1):rod([(0,y,3),(side*w*.68,y+8,3)],.45,green)
    else:
        silver=(.65,.72,.78)
        if recipe in ('bowed','guitar','lute'):
            if recipe=='lute':orb((0,-10,0),(w,h*.8,7))
            else:
                orb((0,-17,0),(w,h*.53,7));orb((0,3,0),(w*.72,h*.40,6))
            add(box((5,34,5),1,3),pos=(0,24,2),tint=dark)
            add(box((9,9,5),1,3),pos=(0,44,2))
            orb((0,-6,7),(4,5,1),dark)
            for j in range(min(n,8)):rod([((j-(n-1)/2)*.5,-23,8),((j-(n-1)/2)*.5,43,5)],.22,silver)
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
                add(box((w*1.6/n,length,3),.5,2),pos=(x,-h*.25,7),tint=silver if j%3 else color)
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
                add(lathe(profile,32),pos=(x,0,0))
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


def build_geometry(design):
    """날짜별 주연과 서로 다른 두 월 모티프를 명시적 대상 사전에서 렌더합니다."""
    from calendar_catalog import OBJECTS
    subject=OBJECTS[design.object_id]
    if subject.recipe!=design.shape_recipe:raise ValueError('대상과 형상 규칙이 일치하지 않습니다.')
    accent=tuple((int(design.accent[i:i+2],16)/255)**2.2 for i in (1,3,5))
    slots={
        'bouquet':((-28,-20,-8),(29,-16,3)), 'diagonal':((-28,-26,-5),(28,27,2)),
        'shelter':((-29,15,-8),(29,-18,1)), 'stage':((-30,-21,-6),(30,-21,1)),
        'triangle':((-27,-25,-3),(27,-25,2)), 'fan':((-30,9,-6),(30,9,1)),
    }
    left,right=slots[design.composition]
    variation=design.year_variant
    result=[]
    objects=((subject,(0,5,6),.73,accent),(OBJECTS[design.anchor_id],left,.34,None),
             (OBJECTS[design.companion_id],right,.34,None))
    for index,(spec,pos,size,color) in enumerate(objects):
        tint=color or tuple((int(spec.color[i:i+2],16)/255)**2.2 for i in (1,3,5))
        # 연도별 깊이 변화와 함께 날짜별로 세 대상의 기울기를 바꿉니다.
        angle=(design.date.day-16)*.006*(1 if index==0 else (-1 if index==1 else 1))
        scale=(size*(.95+.1*variation),size*(.95+.1*variation),size*(.90+.2*variation))
        for mesh,base,metal,rough in _object_geometry(spec,tint):
            result.append((_transformed(mesh,pos,scale,angle),base,metal,rough))
    silver=(.66,.74,.80)
    for mesh in _ring_geometry():
        result.append((mesh,silver,1.,.23))
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
        self.output_resources=[]; self.output_size=0; self.output=None
        try:
            self.ctx=moderngl.create_standalone_context(require=330)
            self.program=self.ctx.program(vertex_shader=VERTEX,fragment_shader=FRAGMENT); self.resources.append(self.program)
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

    def set_date(self,value):
        self._assert_thread(); design=design_for_date(value)
        if self.design==design:return
        self._clear_meshes(); self.parts=build_geometry(design)
        for (vertices,indices),_,_,_ in self.parts:
            vertex=self.ctx.buffer(vertices.tobytes()); self.buffers.append(vertex)
            index=self.ctx.buffer(indices.tobytes()); self.buffers.append(index)
            self.vaos.append(self.ctx.vertex_array(self.program,[(vertex,'3f 3f','in_position','in_normal')],index))
        self.design=design

    def _draw(self,value,elapsed):
        self._assert_thread(); transforms=matrices(elapsed); self.set_date(value)
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.target.use(); self.target.clear(0,0,0,0,depth=1)
        for index,(_,color,metal,rough) in enumerate(self.parts):
            transform=transforms[0] if index<len(self.parts)-3 else transforms[index-len(self.parts)+4]
            self.program['model'].write(transform.T.astype('f4').tobytes())
            self.program['metallic'].value=metal; self.program['base_color'].value=color; self.program['roughness'].value=rough
            self.vaos[index].render(moderngl.TRIANGLES)
        self.ctx.copy_framebuffer(self.resolved,self.target)

    def _image(self,framebuffer,width,height):
        raw=framebuffer.read(components=4,alignment=1)
        # MSAA 결과는 사전곱 알파입니다. 복사해 GPU 버퍼 수명에서 분리합니다.
        image=QImage(raw,width,height,width*4,QImage.Format.Format_RGBA8888_Premultiplied).copy().mirrored(False,True)
        return image

    def render(self,value,elapsed=0):
        self._draw(value,elapsed)
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.output.use(); self.texture.use(location=0)
        self.downsample_vao.render(moderngl.TRIANGLES,vertices=3)
        return self._image(self.output,self.output_size,self.output_size)

    def render_original(self,value,elapsed=0):
        """검증·내보내기 때만 실제 직사각형 원본 전체를 CPU로 읽습니다."""
        self._draw(value,elapsed)
        return self._image(self.resolved,*self.dimensions)

    def _clear_meshes(self):
        for value in reversed(self.vaos):value.release()
        for value in reversed(self.buffers):value.release()
        self.vaos.clear(); self.buffers.clear(); self.parts=[]; self.design=None

    def close(self):
        self._assert_thread(); self._clear_meshes()
        for value in reversed(self.output_resources):value.release()
        self.output_resources.clear(); self.output=None; self.output_size=0
        for value in reversed(self.resources):value.release()
        self.resources.clear()
        if self.ctx is not None:self.ctx.release(); self.ctx=None


def render_date(value,elapsed=0.0,size=384):
    """미리보기와 직접 검증용 동기 렌더입니다. 앱은 공유 작업 스레드를 사용합니다."""
    renderer=CalendarRenderer(size)
    try:return renderer.render(value,elapsed)
    finally:renderer.close()
