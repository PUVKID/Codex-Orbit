"""자연물의 연속 표면과 실제 표면 재질을 구성합니다."""
import math
import numpy as np


def surface_tube(points, radius=1., closed=False, sides=16):
    """이전 단면을 다음 접선에 투영하여 축 선택 경계의 반전을 막습니다."""
    points=np.asarray(points,dtype=float);count=len(points)
    vertices=[];indices=[];side=None
    for i,point in enumerate(points):
        before=points[(i-1)%count] if closed or i else point
        after=points[(i+1)%count] if closed or i<count-1 else point
        tangent=after-before;tangent/=np.linalg.norm(tangent)
        if side is None:
            basis=np.eye(3)[np.argmin(np.abs(tangent))]
            side=np.cross(tangent,basis)
        else:side=side-tangent*np.dot(side,tangent)
        length=np.linalg.norm(side)
        if length<1e-8:
            basis=np.eye(3)[np.argmin(np.abs(tangent))];side=np.cross(tangent,basis);length=np.linalg.norm(side)
        side/=length;vertical=np.cross(tangent,side)
        for j in range(sides):
            normal=side*math.cos(math.tau*j/sides)+vertical*math.sin(math.tau*j/sides)
            vertices.append((*list(point+radius*normal),*normal))
    for i in range(count if closed else count-1):
        for j in range(sides):
            a=i*sides+j;b=((i+1)%count)*sides+j
            c=((i+1)%count)*sides+(j+1)%sides;d=i*sides+(j+1)%sides
            indices.extend((a,b,c,a,c,d))
    vertices=np.asarray(vertices,dtype='f4');ix=np.asarray(indices,dtype='u4').reshape(-1,3)
    p=vertices[ix,:3];normal=vertices[ix,3:].mean(axis=1)
    flip=np.einsum('ij,ij->i',np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]),normal)<0
    ix[flip]=ix[flip][:,[0,2,1]]
    return vertices,ix.reshape(-1)


def instrument_body(width, length, bowed=False, lute=False):
    """현악기의 허리와 앞뒤 곡판을 하나의 닫힌 표면으로 연결합니다."""
    phi,theta=np.meshgrid(np.linspace(0,math.pi,49),np.linspace(0,math.tau,81),indexing='ij')
    y=np.cos(phi);s=np.sin(phi)
    waist=np.ones_like(y) if lute else 1-(.48 if bowed else .34)*np.exp(-((y-.05)/.27)**2)
    x=width*s*waist*np.cos(theta)*(1-.12*y)
    z=(4.5 if bowed else 6)*s*np.sin(theta)
    points=np.stack((x,length*y,z),axis=-1).reshape(-1,3)
    ix=[]
    for row in range(48):
        for col in range(80):
            a=row*81+col;b=a+81;ix.extend(((a,a+1,b),(a+1,b+1,b)))
    ix=np.asarray(ix,dtype='u4');tri=points[ix]
    normals=np.zeros_like(points);face=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    for c in range(3):np.add.at(normals,ix[:,c],face)
    grid=normals.reshape(49,81,3);seam=grid[:,0]+grid[:,-1];grid[:,0]=seam;grid[:,-1]=seam
    grid[0]=(0,1,0);grid[-1]=(0,-1,0)
    normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
    return np.concatenate((points,normals),axis=1).astype('f4'),ix.reshape(-1)


def petal_mesh(width, length, leaf=False, longitude=48, latitude=32):
    """종이처럼 얇지만 앞뒤 두께와 휘어진 표면이 있는 꽃잎·잎을 만듭니다."""
    phi,theta=np.meshgrid(np.linspace(0,math.pi,latitude+1),np.linspace(0,math.tau,longitude+1),indexing='ij')
    s=np.sin(phi); y=np.cos(phi)
    edge=1+.025*np.sin(phi*28) if leaf else 1+.045*np.sin(phi*8)
    x=width*s**(1.5 if leaf else .85)*np.cos(theta)*edge
    curve=length*((.13 if leaf else .30)*(1-y*y)-.055*y)
    z=(.40 if leaf else .65)*s*np.sin(theta)+curve+(.20 if leaf else .34)*width*(x/width)**2
    positions=np.stack((x,length*y,z),axis=-1).reshape(-1,3)
    indices=[]
    for row in range(latitude):
        for col in range(longitude):
            a=row*(longitude+1)+col;b=a+longitude+1
            indices.extend(((a,a+1,b),(a+1,b+1,b)))
    ix=np.asarray(indices,dtype='u4');tri=positions[ix]
    face=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normals=np.zeros_like(positions)
    for column in range(3):np.add.at(normals,ix[:,column],face)
    grid=normals.reshape(latitude+1,longitude+1,3);seam=grid[:,0]+grid[:,-1];grid[:,0]=seam;grid[:,-1]=seam
    grid[0]=(0,1,0);grid[-1]=(0,-1,0)
    normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
    return np.concatenate((positions,normals),axis=1).astype('f4'),ix.reshape(-1)


def fruit_mesh(spec, longitude=80, latitude=48):
    """과일 표면을 매끈한 연속 메시로 만들고 삼각형에서 법선을 계산합니다."""
    phi, theta = np.meshgrid(np.linspace(0, math.pi, latitude + 1),
                             np.linspace(0, math.tau, longitude + 1), indexing='ij')
    s, y = np.sin(phi), np.cos(phi)
    key = spec.key
    radius = np.ones_like(phi)
    if key == 'coconut':
        radius += .035 * np.cos(3 * theta + .4) * s ** 2
        radius += .012 * np.sin(11 * theta + 3 * phi) * s
        radius += .005 * np.sin(39 * theta - 13 * phi) * s
    elif key in ('apple', 'quince', 'persimmon'):
        radius += .045 * np.cos(spec.count * theta) * s ** 2
        y = y * (1 - .17 * np.abs(y) ** 10)
    elif spec.recipe == 'lobed_fruit':
        radius -= .085 * np.exp(-((np.cos(theta) / .13) ** 2)) * s
    elif spec.recipe == 'pear':
        radius *= .72 - .23 * y + .12 * s
    elif spec.recipe == 'seeded_fruit':
        radius *= .76 + .22 * y
    elif spec.recipe == 'starfruit':
        radius *= .57 + .43*((1+np.cos(5*theta))*.5)**2
    elif spec.recipe == 'pineapple':
        radius *= .90 + .10*s + .025*np.cos(12*theta+14*phi)*np.cos(12*theta-14*phi)*s
    x, z = s * np.cos(theta) * radius, s * np.sin(theta) * radius
    if key == 'mango':
        x = x*(.83+.16*y) + .43*s**2*y + .18*(1-y)
        z *= .74
        y += .10*x*s
    if key == 'coconut':
        # 세 눈이 놓이는 곡면의 국소 함몰을 실제 정점에 만듭니다.
        for ex, ey in ((-.24, .32), (.24, .32), (0., -.12)):
            ez = math.sqrt(1 - ex * ex - ey * ey)
            dent = .045 * np.exp(-((x-ex)**2 + (y-ey)**2 + (z-ez)**2) / .013)
            x *= 1-dent; y *= 1-dent; z *= 1-dent
    positions = np.stack((x * spec.width, y * spec.length, z * spec.width * .88), axis=-1).reshape(-1, 3)
    ix = []
    for row in range(latitude):
        for col in range(longitude):
            a = row * (longitude + 1) + col; b = a + longitude + 1
            ix.extend(((a, a+1, b), (a+1, b+1, b)))
    ix = np.asarray(ix, dtype='u4')
    triangles = positions[ix]
    normals = np.cross(triangles[:, 1]-triangles[:, 0], triangles[:, 2]-triangles[:, 0])
    reverse = np.einsum('ij,ij->i', normals, triangles.mean(axis=1)) < 0
    ix[reverse] = ix[reverse][:, [0, 2, 1]]; normals[reverse] *= -1
    accumulated = np.zeros_like(positions)
    for column in range(3): np.add.at(accumulated, ix[:, column], normals)
    grid = accumulated.reshape(latitude+1, longitude+1, 3)
    seam = grid[:, 0] + grid[:, -1]; grid[:, 0] = seam; grid[:, -1] = seam
    grid[0] = (0, 1, 0); grid[-1] = (0, -1, 0)
    accumulated /= np.maximum(np.linalg.norm(accumulated, axis=1)[:, None], 1e-12)
    return np.concatenate((positions, accumulated), axis=1).astype('f4'), ix.reshape(-1)


def organic_shaders(vertex, fragment):
    """기존 금속 셰이더 경로를 유지하고 자연물에만 표면 결을 적용합니다."""
    vertex = vertex.replace('out vec3 normal;', 'out vec3 normal;\nout vec3 surface_position;\nout vec3 surface_normal;')
    vertex = vertex.replace('position = world.xyz;', 'position = world.xyz;\n    surface_position = in_position;\n    surface_normal = in_normal;')
    declarations = '''
in vec3 surface_position;
in vec3 surface_normal;
uniform int organic_kind;
uniform sampler2D species_texture;
uniform int species_enabled;
uniform int species_projection;
uniform mat4 species_mapping;
vec3 species_albedo(vec3 p,vec3 normal_local) {
    vec3 q=(species_mapping*vec4(p,1.)).xyz;
    q=clamp(q,vec3(.002),vec3(.998));
    if(species_projection==0) return pow(texture(species_texture,vec2(q.x,1.-q.y)).rgb,vec3(2.2));
    vec3 n=normalize(transpose(inverse(mat3(species_mapping)))*normal_local);
    vec3 weight=pow(abs(n),vec3(6));weight/=max(dot(weight,vec3(1)),.0001);
    vec3 a=texture(species_texture,vec2(q.z,1.-q.y)).rgb;
    vec3 b=texture(species_texture,q.xz).rgb;
    vec3 c=texture(species_texture,vec2(q.x,1.-q.y)).rgb;
    return pow(a*weight.x+b*weight.y+c*weight.z,vec3(2.2));
}
uniform int skin_kind;
uniform sampler2D shell_texture;
uniform sampler2D detail_texture;
uniform float detail_strength;
uniform float translucency;
float surface_height(vec3 p,vec3 n) {
    vec3 weight=pow(abs(n),vec3(6));weight/=max(dot(weight,vec3(1)),.0001);
    return texture(detail_texture,p.yz*.018).r*weight.x
         + texture(detail_texture,p.xz*.018).r*weight.y
         + texture(detail_texture,p.xy*.018).r*weight.z;
}
float grain(vec3 p) {
    vec3 cell=floor(p), f=fract(p); f=f*f*(3.-2.*f);
    float v=0.;
    for(int x=0;x<2;x++) for(int y=0;y<2;y++) for(int z=0;z<2;z++) {
        vec3 offset=vec3(x,y,z), w=mix(1.-f,f,offset);
        float h=fract(sin(dot(cell+offset,vec3(127.1,311.7,74.7)))*43758.5453);
        v+=w.x*w.y*w.z*h;
    }
    return v*2.-1.;
}
vec3 shell(vec3 p, vec3 n) {
    vec3 weight=pow(abs(n),vec3(6)); weight/=max(dot(weight,vec3(1)),.0001);
    vec3 a=texture(shell_texture,p.yz*.012).rgb;
    vec3 b=texture(shell_texture,p.xz*.012).rgb;
    vec3 c=texture(shell_texture,p.xy*.012).rgb;
    return pow(a*weight.x+b*weight.y+c*weight.z,vec3(2.2));
}
'''
    fragment = fragment.replace('in vec3 normal;', 'in vec3 normal;\n'+declarations)
    start = fragment.index('void main()')
    head, body = fragment[:start], fragment[start:]
    body = body.replace('base_color', 'albedo')
    body = body.replace('vec3 n = normalize(normal);', '''vec3 albedo=base_color;
    vec3 n = normalize(normal);
    if (organic_kind > 0 && metallic < .5) {
        float detail=surface_height(surface_position,normalize(surface_normal));
        albedo *= .88+.22*detail;
        if(skin_kind==1 && base_color.g>base_color.r) {
            float stripe=sin(atan(surface_position.z,surface_position.x)*10.+grain(surface_position*.12)*.7);
            albedo=mix(vec3(.018,.075,.009),vec3(.13,.30,.045),smoothstep(-.25,.25,stripe));
        }
        if(skin_kind==2 && base_color.g>base_color.r) {
            vec3 p=surface_position*.48;
            float net=min(abs(sin(p.x+p.y+grain(p*.3)*.4)),abs(sin(p.z-p.y+grain(p*.3)*.4)));
            albedo=mix(vec3(.44,.34,.13),albedo,smoothstep(.06,.14,net));
        }
        if(skin_kind==3 && base_color.g>base_color.r) albedo=vec3(.18,.083,.025)*(.85+.15*detail);
        if(skin_kind==4 && base_color.r>base_color.g) {
            float a=atan(surface_position.z,surface_position.x)*8.;
            float b=surface_position.y*.22;
            float edge=min(abs(sin(a+b)),abs(sin(a-b)));
            albedo=mix(vec3(.12,.065,.009),albedo,smoothstep(.05,.18,edge));
        }
        if(organic_kind==3 && base_color.r>base_color.b*1.3) {
            float wood=sin(surface_position.y*.85+grain(surface_position*.13)*5.);
            albedo*=.88+.12*wood;
        }
        if (organic_kind == 2 && base_color.r > .05) {
            albedo=shell(surface_position,normalize(surface_normal));
        }
        if(species_enabled==1) {
            vec3 surface_color=species_albedo(surface_position,normalize(surface_normal));
            albedo=mix(base_color,surface_color,.88)*(.94+.10*detail);
        }
        // 화면 미분으로 실제 표면의 작은 요철에 따른 법선 변화를 계산합니다.
        float height=(detail-.5)*detail_strength;
        if (organic_kind == 2) height=dot(albedo,vec3(.3,.5,.2))*.06+(detail-.5)*.015;
        vec3 q0=dFdx(position), q1=dFdy(position);
        vec3 r0=cross(q1,n), r1=cross(n,q0);
        float det=dot(q0,r0);
        if (abs(det)>.000001) n=normalize(n-(r0*dFdx(height)+r1*dFdy(height))/det);
    }''')
    body=body.replace('vec3 radiance = reflected + diffuse + .25*specular*nl;',
                      'vec3 radiance = reflected + diffuse + .25*specular*nl;\n    if(organic_kind>0 && metallic<.5) radiance=albedo*(.10+.66*nl+translucency*(.20*max(dot(-n,l),0.)+.08*pow(1.-nv,3.)))+reflected*.24+.18*specular*nl;')
    return vertex, head+body
