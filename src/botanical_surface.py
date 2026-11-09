"""단일 잎의 외곽과 실제 천공을 앞뒤 곡면으로 구성합니다."""
import math
import numpy as np


def leaf_surface(key, width, length):
    """갈래와 부채꼴은 외곽으로, 몬스테라 구멍은 없는 면으로 표현합니다."""
    rings, sectors = 32, 160
    points=[]
    for row in range(rings+1):
        r=row/rings
        for col in range(sectors):
            t=math.tau*col/sectors
            if key in ('maple','ivy','grape_leaf','fig_leaf'):
                # 뾰족한 갈래 사이의 골도 같은 잎몸으로 이어집니다.
                a=math.atan2(math.sin(t),math.cos(t))
                if key=='ivy':
                    angles=(-math.pi,-1.9,-1.1,0.,1.1,1.9,math.pi)
                    radii=(.20,.90,.42,1.25,.42,.90,.20)
                else:
                    angles=(-math.pi,-2.4,-1.92,-1.48,-.98,-.53,0.,.53,.98,1.48,1.92,2.4,math.pi)
                    radii=(.18,.32,.82,.36,1.,.43,1.25,.43,1.,.36,.82,.32,.18)
                radius=float(np.interp(a,angles,radii))
                if key=='grape_leaf':radius=.30+.70*radius
                if key=='fig_leaf':radius*=1-.08*math.cos(3*a)
                radius*=1+.025*math.sin(37*a)
                x=length*.95*r*radius*math.sin(t)
                y=length*r*radius*math.cos(t)
            elif key=='ginkgo':
                a=-1.12+2.24*col/(sectors-1)
                radius=length*(1-.25*math.exp(-(a/.12)**2))
                x=r*radius*math.sin(a);y=r*radius*math.cos(a)-length*.35
            else:
                radius=1-.12*math.cos(t)
                if key in ('birch','poplar'):radius*=.72+.28*math.sin(t/2)**2
                if key=='elm':radius*=1+.13*math.sin(t)
                if key in ('mint','birch','elm','poplar'):radius*=1+.045*math.sin(32*t)
                if key=='oak':radius*=.80+.20*math.cos(9*t)
                if key in ('linden','philodendron','oxalis'):
                    radius*=1-.55*math.exp(-((math.atan2(math.sin(t),math.cos(t)))/.30)**2)
                if key=='monstera':
                    radius*=1-.30*(abs(math.sin(5*t))**18)*abs(math.sin(t))
                x=width*r*math.sin(t)*radius;y=length*r*math.cos(t)
            z=2.8*(1-r*r)+.12*abs(x)+.8*math.sin(y*.12)
            points.append((x,y,z))
    points=np.asarray(points,dtype=float)
    row,col=np.meshgrid(np.arange(rings),np.arange(sectors if key!='ginkgo' else sectors-1),indexing='ij')
    nxt=(col+1)%sectors;a=row*sectors+col;b=(row+1)*sectors+col
    faces=np.stack((np.stack((a,b,(row+1)*sectors+nxt),axis=-1),
                    np.stack((a,(row+1)*sectors+nxt,row*sectors+nxt),axis=-1)),axis=-2).reshape(-1,3).astype('u4')
    if key=='monstera':
        center=points[faces].mean(axis=1);hole=np.zeros(len(faces),dtype=bool)
        for side in (-1,1):
            for y0 in (-10.,1.,12.):
                hole|=((center[:,0]-side*width*.44)/(width*.12))**2+((center[:,1]-y0)/4.3)**2<1
        faces=faces[~hole]
    # 표면 법선을 매끈하게 누적하고 모든 경계에 옆면을 붙입니다.
    normal=np.zeros_like(points);tri=points[faces]
    face_normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    if face_normal[:,2].sum()<0:faces=faces[:,[0,2,1]];face_normal=-face_normal
    for j in range(3):np.add.at(normal,faces[:,j],face_normal)
    lengths=np.linalg.norm(normal,axis=1);normal[lengths<1e-9]=(0,0,1)
    normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-9)
    vertices=np.concatenate((points,normal),axis=1)
    back=vertices.copy();back[:,2]-=.65;back[:,3:]*=-1
    count=len(vertices);vertices=np.concatenate((vertices,back))
    all_faces=[faces,(faces[:,[0,2,1]]+count)]
    edges=np.sort(np.concatenate((faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]])),axis=1)
    edges,uses=np.unique(edges,axis=0,return_counts=True);boundary=edges[uses==1]
    a,b=boundary[:,0],boundary[:,1]
    sides=np.stack((np.stack((a,b,b+count),axis=-1),np.stack((a,b+count,a+count),axis=-1)),axis=1).reshape(-1,3)
    all_faces.append(np.asarray(sides,dtype='u4'))
    return vertices.astype('f4'),np.concatenate(all_faces).reshape(-1)


def cup_petal(radius, angle_width, depth, style='rose', phase=0.):
    """겹꽃 한 층의 꽃잎을 서로 관통하지 않는 둥근 컵 조각으로 만듭니다."""
    rows,cols=24,48
    t,u=np.meshgrid(np.linspace(0,1,rows+1),np.linspace(-1,1,cols+1),indexing='ij')
    # 종별 꽃잎 끝과 주름은 색 그림이 아니라 정점 위치를 바꿉니다.
    edge=(.84+.16*np.cos(u*math.pi/2))
    if style in ('dahlia','chrysanthemum'):edge=.65+.35*np.cos(u*math.pi/2)**2
    if style in ('carnation','peony'):edge+=.02*np.sin(u*7+phase)*t**4
    r=radius*(.17+.83*t)*edge
    a=u*angle_width*.48
    x=r*np.sin(a);y=r*np.cos(a)
    z=depth*t*t+.8*u*u*t
    if style=='rose':z+=2.2*np.sin(u*1.5+phase)*t*t+1.5*(1-t)**2
    elif style in ('carnation','peony'):z+=.7*np.sin(u*7+phase)*t**4
    elif style in ('dahlia','chrysanthemum'):z+=3.5*u*u*t
    else:z+=.65*np.sin(u*4+phase)*t*t
    points=np.stack((x,y,z),axis=-1).reshape(-1,3)
    faces=[]
    for row in range(rows):
        for col in range(cols):
            i=row*(cols+1)+col;j=i+cols+1
            faces.extend(((i,j,i+1),(i+1,j,j+1)))
    faces=np.asarray(faces,dtype='u4')
    tri=points[faces];face_normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    if face_normal[:,2].sum()<0:faces=faces[:,[0,2,1]];face_normal=-face_normal
    normals=np.zeros_like(points)
    for j in range(3):np.add.at(normals,faces[:,j],face_normal)
    normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-9)
    front=np.concatenate((points,normals),axis=1);back=front.copy();back[:,2]-=.55;back[:,3:]*=-1
    count=len(front);all_faces=[faces,faces[:,[0,2,1]]+count]
    boundary=list(range(cols+1))+[r*(cols+1)+cols for r in range(1,rows+1)]
    boundary+=list(range(rows*(cols+1)+cols-1,rows*(cols+1)-1,-1))
    boundary+=[r*(cols+1) for r in range(rows-1,0,-1)]
    sides=[]
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):sides.extend(((a,b,b+count),(a,b+count,a+count)))
    all_faces.append(np.asarray(sides,dtype='u4'))
    return np.concatenate((front,back)).astype('f4'),np.concatenate(all_faces).reshape(-1)
