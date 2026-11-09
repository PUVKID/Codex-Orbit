"""날짜별 악기의 식별 구조를 실제 몸체·관·건반·북면으로 구성합니다."""
import math
import numpy as np
from fruit_surface import surface_tube


def instrument_geometry(spec):
    from calendar_renderer import sphere_mesh, box, lathe, _transformed, rotation, finish
    parts=[]
    brass=(.60,.34,.065);silver=(.60,.65,.69);black=(.009,.011,.014)
    wood=(.25,.10,.026);ivory=(.75,.70,.58)
    def add(mesh,pos=(0,0,0),color=brass,metal=1.,rough=.25,matrix=None):
        vertices,indices=mesh
        if matrix is not None:
            vertices=vertices.copy();vertices[:,:3]=vertices[:,:3]@matrix.T;vertices[:,3:]=vertices[:,3:]@matrix.T
        parts.append((_transformed((vertices,indices),pos),color,metal,rough))
    def block(size,pos,color=black,metal=0.,matrix=None):
        add(box(size,min(.6,min(size)/4),4),pos,color,metal,.28,matrix)
    def rod(points,r=1.5,color=brass,metal=1.):add(surface_tube(points,r,False,16),color=color,metal=metal)
    def orb(pos,size,color=brass,metal=1.):add(_transformed(sphere_mesh(1,24,16),scale=size),pos,color,metal)
    def circle(radius,y,center=(0,0,0),r=.8):
        add(surface_tube([(center[0]+radius*math.cos(t),y,center[2]+radius*math.sin(t)) for t in np.linspace(0,math.tau,64,endpoint=False)],r,True,12),color=silver)
    def bell(pos,size=1.,matrix=None):
        profile=[(2,-12),(2.5,-5),(3.5,2),(6,8),(11,13),(10.4,13.4),(5.5,8),(3,2),(2,-5),(1.5,-12)]
        add(_transformed(lathe(profile,64),scale=(size,)*3),pos,matrix=matrix)
    def slab(outline,bottom,top,color=black,matrix=None,pos=(0,0,0)):
        vertices=[];indices=[];center=np.mean(outline,axis=0)
        for y,ny in ((bottom,-1),(top,1)):
            start=len(vertices);vertices.append((center[0],y,center[1],0,ny,0))
            vertices.extend((x,y,z,0,ny,0) for x,z in outline)
            for i in range(len(outline)):indices.extend((start,start+1+i,start+1+(i+1)%len(outline)))
        for i,(x,z) in enumerate(outline):
            nx,nz=outline[(i+1)%len(outline)];normal=np.array((nz-z,0,x-nx),dtype=float);normal/=np.linalg.norm(normal)
            start=len(vertices)
            vertices.extend((a,y,b,*normal) for a,y,b in ((x,bottom,z),(nx,bottom,nz),(nx,top,nz),(x,top,z)))
            indices.extend((start,start+1,start+2,start,start+2,start+3))
        add(finish(vertices,indices),pos,color,0.,.23,matrix)

    if spec.recipe=='piano':
        outline=[(-29,-20),(29,-20),(29,5),(26,17),(18,26),(5,30),(-12,29),(-24,21),(-29,9)]
        slab(outline,1,9)
        # 열린 뚜껑은 실제 기울어진 판이며 몸체 위의 지지봉과 연결됩니다.
        slab(outline,0,1.5,matrix=rotation((0,0,1),-.28),pos=(2,19,0))
        rod([(22,9,13),(22,14,13)],.6,brass)
        for x,z in ((-24,-14),(24,-14),(0,22)):
            block((4,26,4),(x,-12,z));orb((x,-26,z),(2.5,1.2,2.5),brass)
        block((60,5,11),(0,0,-23))
        for j in range(22):
            x=-27+j*2.5
            block((2.3,1.3,9),(x,3.4,-25),ivory)
            if j%7 not in (2,6):block((1.3,1.5,5.2),(x+1.25,4.7,-23.1))
        block((15,1,10),(0,-23,-7),brass,1.)
        # 앞 건반과 상판을 함께 보이도록 악기 자체를 기울입니다.
        matrix=rotation((1,0,0),.37)@rotation((0,1,0),math.pi-.26)
        result=[]
        for (v,ix),color,metal,rough in parts:
            v=v.copy();v[:,:3]=v[:,:3]@matrix.T;v[:,3:]=v[:,3:]@matrix.T
            result.append(((v,ix),color,metal,rough))
        return result
    if spec.recipe=='sax':
        points=[(-7,30,0),(-4,26,0),(-4,20,0),(-7,13,0),(-9,4,0),(-9,-17,0)]
        points.extend((1+10*math.cos(t),-17+10*math.sin(t),0) for t in np.linspace(math.pi,math.tau,24)[1:])
        points.extend(((11,-8,0),(11,-3,0)))
        rod(points,2.7);bell((11,6,0),.85)
        rod([(-7,30,0),(-14,32,0),(-19,29,0)],1.6,black,0.)
        for j in range(8):
            y=15-j*4.4;rod([(-8,y,1),(-3,y,3)],.5,silver);orb((-3,y,3),(1.6,1.6,.8),silver)
    elif spec.key=='trumpet':
        # 주관은 수평이며 세 피스톤과 접힌 하부 관을 따로 배치합니다.
        rod([(-30,7,0),(18,7,0)],1.7)
        bell((26,7,0),.8,rotation((0,0,1),-math.pi/2))
        points=[(-22,3,0),(-22,-6,0)]
        points.extend((-15+7*math.cos(t),-6+7*math.sin(t),0) for t in np.linspace(math.pi,math.tau*1.5,26)[1:])
        points.extend(((16,-13,0),(20,-9,0),(20,4,0)))
        rod(points,1.5)
        for j in range(3):
            x=-7+j*7;rod([(x,-12,0),(x,16,0)],2.2);orb((x,17,0),(3,1,3),silver)
        add(lathe([(0,-2),(3,-2),(3,1),(0,1)],32),(-32,7,0),silver,matrix=rotation((0,0,1),math.pi/2))
    elif spec.key=='trombone':
        points=[(-9,28,0),(-9,-29,0)]
        points.extend((9*math.cos(t),-29+9*math.sin(t),0) for t in np.linspace(math.pi,math.tau,24)[1:])
        points.extend(((9,22,0),))
        rod(points,1.5);rod([(-9,3,0),(9,3,0)],.8);rod([(-9,18,0),(9,18,0)],.8)
        bell((-9,33,0),.65);rod([(9,22,0),(14,26,0),(18,26,0)],1.2)
    elif spec.recipe=='horn':
        points=[(18*math.cos(t),18*math.sin(t),0) for t in np.linspace(0,math.tau*2,100)]
        rod(points,2.3);bell((23,11,0),1.1,rotation((0,0,1),-.8))
        for j in range(3):rod([(-5+j*5,-7,2),(-5+j*5,8,2)],1.,silver)
    elif spec.key=='tuba':
        for k in range(3):
            width=17-k*5;bottom=-23+k*3
            points=[(-width,22-k*4,0),(-width,bottom,0)]
            points.extend((width*math.cos(t),bottom+width*.6*math.sin(t),0) for t in np.linspace(math.pi,math.tau,26)[1:])
            points.append((width,18-k*3,0));rod(points,2.7-k*.3)
        bell((17,26,0),1.25)
        for j in range(4):orb((-9+j*6,9,4),(2,1,2),silver)
    elif spec.recipe in ('drum','bowl_drum','tambourine'):
        count=2 if spec.key=='bongo' else 1
        for j in range(count):
            w=spec.width*(1-.13*j);h=spec.length*(1-.2*j);x=(j-(count-1)/2)*spec.width*1.8
            if spec.recipe=='bowl_drum':
                profile=[(0,-h)]+[(w*math.sin(t),-h*math.cos(t)) for t in np.linspace(.04,math.pi/2,32)]+[(0,0)]
                add(lathe(profile,64),(x,0,0),(.42,.21,.055),.9)
                top=0
                for leg in (-1,1):rod([(x+leg*w*.6,-h*.6,0),(x+leg*w*.7,-h-13,0)],1.4,silver)
            else:
                add(lathe([(w*.92,-h),(w,-h),(w,h),(w*.92,h),(w*.92,-h)],64),(x,0,0),silver if spec.key=='snare' else wood,1. if spec.key=='snare' else 0.,.3)
                top=h
            add(lathe([(0,0),(w*.95,0),(w*.95,.3),(0,.3)],64),(x,top,0),ivory,0.,.82)
            circle(w,top+.6,(x,0,0),1.)
            if spec.recipe!='bowl_drum':circle(w,-h,(x,0,0),.8)
            for k in range(10 if count==1 else 6):
                t=math.tau*k/(10 if count==1 else 6);px=x+w*math.cos(t);pz=w*math.sin(t)
                rod([(px,top-2,pz),(px,top-min(10,h),pz)],.55,silver)
            if spec.key=='tambourine':
                for k in range(8):
                    t=math.tau*k/8;orb((x+w*math.cos(t),0,w*math.sin(t)),(3,.6,3),silver)
        matrix=rotation((1,0,0),.33)
        for index,((v,ix),color,metal,rough) in enumerate(parts):
            v=v.copy();v[:,:3]=v[:,:3]@matrix.T;v[:,3:]=v[:,3:]@matrix.T;parts[index]=((v,ix),color,metal,rough)
    else:raise ValueError('전용 악기 형상이 없습니다: '+spec.key)
    return parts
