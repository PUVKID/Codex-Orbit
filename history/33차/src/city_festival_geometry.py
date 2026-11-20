"""도시 행사 종류를 구분하는 단일 입체 물체의 실제 메시를 구성합니다."""
import math
import numpy as np


def city_festival_geometry(spec,color):
    from calendar_renderer import sphere_mesh,box,lathe,_transformed
    from fruit_surface import surface_tube
    parts=[]
    silver=(.48,.52,.58);dark=(.015,.02,.03);gold=(.65,.36,.07)
    def add(mesh,pos=(0,0,0),tint=color,metal=0.,rough=.4,angle=0.):
        parts.append((_transformed(mesh,pos,angle=angle),tint,metal,rough))
    def block(size,pos,tint=color,metal=0.,angle=0.):
        add(box(size,min(.7,min(size)/4),4),pos,tint,metal,angle=angle)
    def ball(pos,scale,tint=color,metal=0.):
        add(_transformed(sphere_mesh(1,40,24),scale=scale),pos,tint,metal)
    def stroke(points,radius,tint=color,metal=0.):
        add(surface_tube(points,radius,False,12),tint=tint,metal=metal)
    kind=spec.recipe.removeprefix('city_')
    if kind=='music':
        # 마이크 헤드의 격자와 받침은 물체 자체의 구조입니다.
        ball((0,17,0),(14,21,12),silver,.75)
        block((9,31,9),(0,-12,0),dark,.25)
        add(lathe([(0,-39),(21,-39),(21,-35),(0,-35)],48),tint=dark,metal=.4)
        stroke([(0,-35,0),(0,-22,0)],3,silver,.7)
        for y in range(3,34,5):
            span=12*math.sqrt(max(.08,1-((y-17)/22)**2))
            stroke([(-span,y,10),(span,y,10)],.65,dark,.3)
    elif kind=='film':
        block((59,35,12),(0,-9,0),dark,.2)
        block((60,10,13),(0,16,0),silver,.4)
        # 열려 있는 클래퍼의 대각 줄무늬와 경첩을 두께 있는 부품으로 만듭니다.
        for i in range(6):block((7,9,13.6),(-25+i*10,16,0),dark,angle=-.35)
        block((59,9,12),(-1,31,0),dark,.2,angle=.16)
        for i in range(6):block((6,8,12.6),(-25+i*10,27+i*1.5,0),silver,.4,angle=-.2)
        ball((-26,18,8),(3,3,2),gold,.6)
        for y in (-4,-13):block((40,1.1,1),(-1,y,6.6),silver)
    elif kind=='snow':
        ice=(.35,.63,.78)
        # 각진 얼음 탑과 중앙 아치가 있는 눈 축제 모형입니다.
        block((65,8,30),(0,-30,0),(.65,.79,.86))
        for x,height in ((-23,32),(0,49),(23,35)):
            add(lathe([(0,-26),(9,-26),(9,height-22),(0,height-10)],6),pos=(x,0,0),tint=ice,rough=.18)
            block((14,7,18),(x,height-24,0),(.7,.86,.91))
        block((9,19,2),(0,-16,10),(.035,.1,.16))
    elif kind=='lights':
        # 종이등 하나에 세로 골과 위아래 금속 뚜껑을 구성합니다.
        ball((0,0,0),(25,32,22),(.82,.25,.035))
        for j in range(12):
            angle=math.tau*j/12
            points=[(25*math.sin(t)*math.cos(angle),32*math.cos(t),22*math.sin(t)*math.sin(angle)) for t in np.linspace(.15,math.pi-.15,32)]
            stroke(points,.65,gold,.4)
        for y in (-31,31):block((18,4,16),(0,y,0),dark,.3)
        stroke([(-7,33,0),(-7,40,0),(7,40,0),(7,33,0)],1.2,gold,.6)
        for x in (-4,0,4):stroke([(x,-33,0),(x,-44,0)],.8,gold)
    elif kind=='carnival':
        # 앞면의 눈 오목부와 굽은 코를 가진 무도회 가면입니다.
        ball((0,1,0),(31,18,9),color,.4)
        for x in (-14,14):
            ball((x,3,7),(9,5,2.5),dark)
            points=[(x+10*math.cos(t),3+6*math.sin(t),8) for t in np.linspace(0,math.tau,36)]
            stroke(points,1.2,gold,.6)
        ball((0,-3,9),(4,10,5),gold,.5)
        for side in (-1,1):
            for j in range(3):
                stroke([(side*22,11,0),(side*(25+j*5),25+j*4,-3)],2,(.04,.2,.31))
        stroke([(26,-8,0),(30,-40,0)],2,gold,.5)
    elif kind=='flowers':
        add(lathe([(0,-36),(13,-36),(18,-13),(0,-13)],48),tint=(.26,.12,.035),rough=.7)
        for x,y in ((-15,9),(0,23),(15,7)):
            stroke([(x*.3,-17,0),(x,y,0)],1.5,(.025,.16,.04))
            for j in range(7):
                t=j*math.tau/7
                ball((x+9*math.cos(t),y+9*math.sin(t),1),(7,6,3),(.7,.19,.3))
            ball((x,y,4),(4,4,3),gold)
    elif kind=='balloon':
        # 기낭 패널과 줄·바구니가 연결된 열기구 한 대입니다.
        ball((0,13,0),(25,31,23),(.75,.23,.045))
        for j in range(8):
            angle=j*math.tau/8
            points=[(25*math.sin(t)*math.cos(angle),13+31*math.cos(t),23*math.sin(t)*math.sin(angle)) for t in np.linspace(.12,math.pi-.25,40)]
            stroke(points,.9,gold if j%2 else (.05,.2,.45))
        for x,z in ((-7,-6),(-7,6),(7,-6),(7,6)):
            stroke([(x,-12,z),(x,-28,z)],.8,(.22,.12,.055))
        block((18,13,15),(0,-34,0),(.29,.12,.035))
        for y in (-38,-35,-32,-29):block((18.5,.7,15.5),(0,y,0),gold)
    elif kind=='culture':
        # 가죽 면과 금속 조임쇠를 가진 축제 북 하나입니다.
        add(lathe([(0,-23),(25,-23),(25,23),(0,23)],64),tint=(.35,.075,.025),rough=.5)
        for y in (-24,24):
            add(lathe([(0,-1),(25,-1),(25,1),(0,1)],64),pos=(0,y,0),tint=(.75,.66,.48),rough=.65)
        for j in range(10):
            t=j*math.tau/10;x,z=25*math.cos(t),25*math.sin(t)
            stroke([(x,-22,z),(x,22,z)],1,silver,.7)
    else:raise ValueError('지원하지 않는 도시 행사 형상')
    return parts
