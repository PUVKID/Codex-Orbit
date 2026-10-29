"""현재 날짜의 실제 메시를 소유 스레드의 오프스크린 GPU에서 렌더합니다."""

from __future__ import annotations

import math

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


def build_geometry(design):
    """월별 구조와 일별 부품 수·비율·곡률을 바꾸며 색만 바꾼 복제를 피합니다."""
    day=design.date.day; month=design.date.month; variation=design.year_variant
    accent=tuple((int(design.accent[i:i+2],16)/255)**2.2 for i in (1,3,5))
    silver=(.66,.74,.80); pale=tuple(.35+.55*c for c in accent)
    parts=[]; sphere=sphere_mesh(1,32,16)
    def add(mesh,pos=(0,0,0),scale=(1,1,1),angle=0,color=None,metal=.65,rough=.28):
        parts.append((_transformed(mesh,pos,scale,angle),color or accent,metal,rough))
    def orb(pos,scale,color=None,angle=0):add(sphere,pos,scale,angle,color)
    def rod(points,radius=1.5,color=None,closed=False):add(tube(points,radius,closed,10),color=color or silver)
    def leaf(pos,length,width,angle,color=None):orb(pos,(width,length,3.4),color,angle)
    # 일자는 불연속 형태 선택과 연속 비율에 모두 들어가고 연도는 기하 위상을 바꿉니다.
    phase=variation*math.tau; fraction=(day-1)/30; count=5+(day-1)%7
    if month==1:
        family=(day-1)%7; group=(day-1)//7
        if family==1:
            # 닫힌 봉오리는 긴 세 꽃잎이 중심을 감싸는 수직 실루엣입니다.
            for j in range(3+group):
                t=math.tau*j/(3+group)+phase*.2
                orb((8*math.cos(t),10,7*math.sin(t)),(8,24+group,8),pale if j%2 else accent,.12*math.sin(t))
            for sign in (-1,1):leaf((sign*8,-8,2),13,5,sign*.6,(.28,.57,.40))
        elif family==3:
            # 고개를 숙인 종꽃을 각각의 줄기 끝에 달아 평면 방사꽃과 구분합니다.
            for j in range(2+group%3):
                x=(j-(1+group%3)/2)*20; y=13+8*math.cos(j+phase)
                add(lathe([(0,14),(5,12),(6,0),(12,-10),(10,-12),(5,-4),(0,-3)],48),pos=(x,y,0),angle=(j-.5)*.25,color=pale if j%2 else accent)
                rod([(0,-15,-4),(x,y+18,-4),(x,y+13,0)],1.2,(.25,.53,.40))
        elif family==4:
            # 나팔형의 벌어진 입구와 길게 좁아지는 목을 실제 회전체로 만듭니다.
            add(lathe([(0,-20),(5,-18),(7,-3),(22,15),(23,19),(20,20),(8,3),(3,-14),(0,-15)],64),pos=(0,8,0),angle=-.25+fraction*.35)
            orb((0,14,9),(4,4,4),(.85,.73,.39))
        else:
            layers=3 if family==2 else 2 if family==5 else 1
            for layer in range(layers):
                petals=(6 if family==6 else 7 if family==5 else 8 if family==2 else 5+group*2)+layer*2
                for j in range(petals):
                    t=math.tau*j/petals+layer*.32+phase*.15
                    radius=(18-layer*5) if layers>1 else 15
                    length=(19 if family==6 else 11 if family==5 else 14)+fraction*4-layer*1.4
                    width=(4.5 if family==6 else 10 if family==5 else 7)+group*.4
                    orb((radius*math.cos(t),radius*math.sin(t)+6,layer*4),(width,length,4+layer),pale if layer%2 else accent,t-math.pi/2)
            orb((0,6,5+layers*3),(6 if family==6 else 8,)*3,(.85,.73,.39))
        rod([(0,-2,-3),(-2,-18,-2),(3+fraction*4,-33,-1)],2.1,(.25,.53,.40))
        leaf((-9,-20,-1),11,4,.8,(.31,.64,.45))
    elif month==2:
        sides=4+day%7
        add(lathe([(0,-29),(19+fraction*7,-15),(24,5),(13+variation*6,23),(0,34)],sides,False),angle=-.22+fraction*.4,metal=.92,rough=.15)
        for j in range(2+day%4):
            t=math.tau*j/(2+day%4)+phase
            add(lathe([(0,-10),(5,0),(0,13)],4+j%3,False),pos=(32*math.cos(t),26*math.sin(t),-4),angle=t,color=pale,metal=.9,rough=.16)
    elif month==3:
        wing=18+fraction*8
        for sign in (-1,1):
            orb((sign*17,12,0),(wing*.7,wing,4+variation*3),angle=-sign*(.35+fraction*.3))
            orb((sign*15,-13,2),(12+day%6,13+day%4,5),pale,sign*.45)
            rod([(sign*2,15,2),(sign*5,25,3),(sign*(10+day%5),30,4)],1.1)
            orb((sign*(10+day%5),30,4),(2,2,2),silver)
        orb((0,0,5),(3.5,22,4),silver)
        for j in range(day%5):orb(((1 if j%2 else -1)*21,10-j*5,6),(2.6,2.6,1.5),silver)
    elif month==4:
        add(lathe([(0,-28),(14,-23),(21,-9),(18,5),(8,24),(0,35)],64),angle=-.2+fraction*.4,metal=.75,rough=.14)
        for j in range(2+day%5):
            t=math.tau*j/(2+day%5)+phase
            orb((31*math.cos(t),28*math.sin(t),-2),(2.8,5+day%4,2.8),pale,-.3)
        ts=np.linspace(.15,math.pi*1.65,90)
        rod([(34*math.cos(t),-21+8*math.sin(t),14*math.sin(t)) for t in ts],1.7)
    elif month==5:
        rod([(0,-33,0),(0,22,0)],3.2,(.40,.31,.22))
        for j in range(5+day%6):
            t=math.tau*j/(5+day%6)+phase*.3; y=-8+j*4
            pos=(math.cos(t)*(15+fraction*8),y,math.sin(t)*10)
            rod([(0,y-8,0),pos],1.5,(.40,.31,.22))
            leaf(pos,12+variation*5,7+day%3,t,accent if j%2 else pale)
        leaf((0,27,0),12,7,0,pale)
    elif month==6:
        arms=4+day%5
        for j in range(arms):
            t=math.tau*j/arms+phase*.15
            orb((14*math.cos(t),14*math.sin(t),0),(7+fraction*4,22+variation*3,5),angle=t-math.pi/2)
            for k in range(3):orb(((8+k*9)*math.cos(t),(8+k*9)*math.sin(t),5),(1.7,1.7,1.7),pale)
        orb((0,0,4),(12,12,7),pale)
        for j in range(day%4):orb((-32+j*8,28+math.sin(j)*4,-1),(2.2,2.2,2.2),silver)
    elif month==7:
        orb((0,0,0),(21+fraction*6,21+fraction*6,21+fraction*6),pale)
        ts=np.linspace(0,math.tau,100,endpoint=False)
        rod([(36*math.cos(t),12*math.sin(t),17*math.sin(t)) for t in ts],3+day%3,accent,True)
        for j in range(2+day%5):
            t=math.tau*j/(2+day%5)+phase
            orb((42*math.cos(t),36*math.sin(t),6),(2.2+j*.4,)*3,silver)
    elif month==8:
        if day%3==0:
            for row in range(4):
                for j in range(4-row):orb(((j-(3-row)/2)*12,20-row*13,(j%2)*4),(8+fraction*2,9,8))
        else:
            add(lathe([(0,-29),(15,-25),(25,-8),(23,6),(12 if day%3==1 else 20,22),(0,27)],64),angle=.12*math.sin(phase),rough=.22)
        rod([(0,24,0),(2,34,0),(7,37,0)],2,(.40,.32,.22))
        leaf((10,30,0),11+day%6,5,-1.0,(.34,.60,.38))
    elif month==9:
        notes=2+day%3
        for j in range(notes):
            x=(j-(notes-1)/2)*18; y=-15+8*math.sin(j+phase)
            orb((x,y,0),(8,5.6,4),angle=.3)
            rod([(x+6,y,0),(x+6,27-fraction*8,0)],1.8)
        rod([((j-(notes-1)/2)*18+6,27-fraction*8,0) for j in range(notes)],3,pale)
        if day>15:
            ts=np.linspace(-1.4,1.4,60); rod([(33+4*math.cos(t),12*math.sin(t),-4) for t in ts],1.1,silver)
    elif month==10:
        lobes=3+day%5
        for j in range(lobes):
            t=-1.2+2.4*j/(lobes-1)
            leaf((15*math.sin(t),8+12*math.cos(t),j*.4),18+fraction*7,7,t,pale if j%2 else accent)
        rod([(0,-31,1),(0,24,5)],1.5,(.65,.45,.25))
        for sign in (-1,1):rod([(0,-4,4),(sign*20,17,5)],1,(.65,.45,.25))
    elif month==11:
        towers=3+day%4
        for j in range(towers):
            height=26+17*math.sin(j*1.7+phase)+fraction*10
            add(box((9+day%4,height,12),2,5),pos=((j-(towers-1)/2)*12,height/2-23,(j%2)*5),color=pale if j%2 else accent,metal=.85)
        ts=np.linspace(0,math.pi,64); rod([(36*math.cos(t),7+28*math.sin(t),-7) for t in ts],2.4,silver)
        orb((0,37,0),(3+day%3,)*3,(.91,.82,.56))
    else:
        arms=5+day%4
        for j in range(arms):
            t=math.tau*j/arms+phase*.12; direction=np.array([math.cos(t),math.sin(t),0.])
            rod([direction*5,direction*(31+fraction*5)],2,pale)
            for distance in (17,26):
                for side in (-1,1):
                    branch=np.array([math.cos(t+side*.65),math.sin(t+side*.65),0.])
                    rod([direction*distance,direction*(distance-5)+branch*12],1.4,accent)
        add(lathe([(0,-8),(9,0),(0,8)],6,False),color=silver)
    # 모든 분기의 실제 정점에 연도 인자를 전달합니다. 깊이 비율도 달라져 색만 바뀌지 않습니다.
    year_scale=(.95+.1*variation,.95+.1*variation,.90+.2*variation)
    parts=[(_transformed(mesh,scale=year_scale),color,metal,rough) for mesh,color,metal,rough in parts]
    # 고유 중심 형상 밖의 두 얇은 궤도는 서로 다른 축으로 움직입니다.
    for index in range(2):
        ts=np.linspace(0,math.tau,128,endpoint=False); radius=49+index*7
        mesh=tube([(radius*math.cos(t),radius*math.sin(t),0) for t in ts],.85,True,10)
        parts.append((mesh,silver,1.,.23))
    return parts


def matrices(elapsed):
    if type(elapsed) not in (int,float):raise ValueError('모션 시각은 유한한 숫자여야 합니다.')
    try:valid=math.isfinite(elapsed)
    except OverflowError:valid=False
    if not valid:raise ValueError('모션 시각은 유한한 숫자여야 합니다.')
    phase=math.tau*(elapsed%PERIOD)/PERIOD
    center=np.eye(4); center[:3,:3]=rotation((0,1,0),.20*math.sin(phase))@rotation((1,0,0),.10*math.sin(phase+.5)); center[1,3]=1.4*math.sin(phase)
    result=[center]
    for index,axis in enumerate(((.6,1,.3),(-.9,.3,1))):
        matrix=np.eye(4); matrix[:3,:3]=rotation(axis,(.40,-.44)[index]*math.sin(phase+index))@rotation((0,0,1),(.2,1.2)[index])@rotation((1,0,0),(.8,-.7)[index])
        result.append(matrix)
    return result


class CalendarRenderer:
    """컨텍스트를 만든 스레드에서만 사용하고 현재 날짜의 버퍼만 보유합니다."""
    def __init__(self,size=384):
        if type(size) is not int or not 32<=size<=768:raise ValueError('렌더 크기는32~768 정수여야 합니다.')
        self.thread_id=threading.get_ident(); self.size=size; self.ctx=None; self.resources=[]; self.vaos=[]; self.buffers=[]; self.parts=[]; self.design=None
        try:
            self.ctx=moderngl.create_standalone_context(require=330)
            self.program=self.ctx.program(vertex_shader=VERTEX,fragment_shader=FRAGMENT); self.resources.append(self.program)
            self.color=self.ctx.renderbuffer((size,size),components=4,samples=4); self.resources.append(self.color)
            self.depth=self.ctx.depth_renderbuffer((size,size),samples=4); self.resources.append(self.depth)
            self.target=self.ctx.framebuffer([self.color],self.depth); self.resources.append(self.target)
            self.resolved=self.ctx.simple_framebuffer((size,size),components=4,dtype='f1'); self.resources.append(self.resolved)
            self.ctx.enable(moderngl.DEPTH_TEST)
            near,far,camera,extent=1.,1200.,700.,69.
            projection=np.array([[camera/extent,0,0,0],[0,camera/extent,0,0],[0,0,(far+near)/(near-far),2*far*near/(near-far)],[0,0,-1,0]],dtype='f4')
            view=np.eye(4,dtype='f4'); view[2,3]=-camera
            self.program['view_projection'].write((projection@view).T.astype('f4').tobytes()); self.program['camera'].value=(0.,0.,camera)
        except Exception:
            self.close(); raise

    def _assert_thread(self):
        if threading.get_ident()!=self.thread_id:raise RuntimeError('GPU 컨텍스트는 생성 스레드에서만 사용할 수 있습니다.')

    def set_date(self,value):
        self._assert_thread(); design=design_for_date(value)
        if self.design==design:return
        self._clear_meshes(); self.parts=build_geometry(design)
        for (vertices,indices),_,_,_ in self.parts:
            vertex=self.ctx.buffer(vertices.tobytes()); self.buffers.append(vertex)
            index=self.ctx.buffer(indices.tobytes()); self.buffers.append(index)
            self.vaos.append(self.ctx.vertex_array(self.program,[(vertex,'3f 3f','in_position','in_normal')],index))
        self.design=design

    def render(self,value,elapsed=0):
        self._assert_thread(); transforms=matrices(elapsed); self.set_date(value)
        self.target.use(); self.target.clear(0,0,0,0,depth=1)
        for index,(_,color,metal,rough) in enumerate(self.parts):
            transform=transforms[0] if index<len(self.parts)-2 else transforms[index-len(self.parts)+3]
            self.program['model'].write(transform.T.astype('f4').tobytes())
            self.program['metallic'].value=metal; self.program['base_color'].value=color; self.program['roughness'].value=rough
            self.vaos[index].render(moderngl.TRIANGLES)
        self.ctx.copy_framebuffer(self.resolved,self.target)
        raw=self.resolved.read(components=4,alignment=1)
        # MSAA 결과는 사전곱 알파입니다. 복사해 GPU 버퍼 수명에서 분리합니다.
        image=QImage(raw,self.size,self.size,self.size*4,QImage.Format.Format_RGBA8888_Premultiplied).copy().mirrored(False,True)
        return image

    def _clear_meshes(self):
        for value in reversed(self.vaos):value.release()
        for value in reversed(self.buffers):value.release()
        self.vaos.clear(); self.buffers.clear(); self.parts=[]; self.design=None

    def close(self):
        self._assert_thread(); self._clear_meshes()
        for value in reversed(self.resources):value.release()
        self.resources.clear()
        if self.ctx is not None:self.ctx.release(); self.ctx=None


def render_date(value,elapsed=0.0,size=384):
    """미리보기와 직접 검증용 동기 렌더입니다. 앱은 공유 작업 스레드를 사용합니다."""
    renderer=CalendarRenderer(size)
    try:return renderer.render(value,elapsed)
    finally:renderer.close()
