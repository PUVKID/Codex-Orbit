"""31개 원소의 서로 다른 실제3D 조형과 RGB 금속 모션을 제작합니다."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import sys
import time
import traceback
import zipfile
from datetime import datetime,timezone,timedelta

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'17차/work/render-deps'))
sys.path.insert(0,str(ROOT/'src'))
import render_atom3d as atom
from render_atom3d import np,Image,moderngl
from render_symbols3d import box,arc,finish
from elements import ELEMENTS
from PIL import ImageDraw,ImageFont

SIZE=192
FPS=30
COUNT=540
PERIOD=18
# 색은 물리적 불꽃색이 아닌 원소별 조형의 디자인 팔레트입니다.
COLORS=('53c9ef','b3a0f5','ef718c','69c8b5','a77bcb','99ddf4','668ce9','e96d7e',
        'a1cf62','f68d58','f1c455','c4dbe9','9ebbd5','7889d9','dc8167','e9d34a',
        '84c754','a197e5','c284dd','ddd0a6','77bdc8','96adce','7b83cb','69b6ae',
        'b67db5','b87561','477bd9','91b59b','d38951','81acc2','a7c3e4')
FEATURES=(
 ('가벼운 단일 물방울','수소의 가벼움에서 착안한 단일 유선형. 물분자 모형 아님'),
 ('서로 뜬 쌍구체','헬륨 기체와 풍선의 부유감을 두 구체로 표현. 실제 이원자분자 아님'),
 ('배터리 코어','리튬 이차전지의 쓰임을 단자 있는 코어로 표현'),
 ('항공 합금 십자빔','가벼운 강성 합금의 쓰임에서 착안한 교차빔'),
 ('보라색 다면 결정','붕소의 결정성을 추상 다면체로 표현'),
 ('컷 다이아몬드','탄소의 다이아몬드 동소체에서 착안한 보석형'),
 ('삼중 연결 캡슐','질소의 삼중결합에서 착안한 세 연결봉. 축척분자모형 아님'),
 ('겹친 산소 구체','산소 이원자분자에서 착안한 두 겹의 둥근 실루엣'),
 ('형석 영감 결정군','플루오린을 포함한 형석의 결정에서 착안. 원소 자체 모양 아님'),
 ('광관 매듭','네온 조명의 용도를 닫힌 금속 광관 매듭으로 표현'),
 ('분할 소금 큐브','나트륨 화합물 소금에서 착안한 네 분할 큐브'),
 ('금속 빛살','마그네슘의 밝은 연소에서 착안한 여섯 빛살. 불꽃색 재현 아님'),
 ('겹친 금속 포일','알루미늄의 얇은 포일 가공을 굽은 세 판으로 표현'),
 ('반도체 웨이퍼','실리콘 반도체의 쓰임에서 착안한 원판과 칩 격자'),
 ('사면체 결절','인의 동소체에서 착안한 네 결절과 사면체 구조'),
 ('노란 결정 왕관','황의 노란 결정과 고리에서 착안한 여덟 결정 왕관'),
 ('쌍기둥 정화체','염소의 소독 용도를 쌍기둥으로 추상화. 장치 설계 아님'),
 ('보호 가스 격자','아르곤 보호가스에서 착안한 열린 정육면체 보호틀'),
 ('보라 세잎','칼륨의 생물학적 역할을 세잎 조형으로 비유'),
 ('방해석 경사 결정','칼슘 화합물 방해석에서 착안한 기울어진 결정'),
 ('세날 합금 로터','스칸듐 합금의 쓰임을 세날 로터로 추상화'),
 ('육각 체결 코어','타이타늄의 강성·경량 쓰임을 육각 체결부로 표현'),
 ('강철 V 지지대','바나듐 강철의 쓰임과 기호 V를 입체 지지대로 표현'),
 ('크롬 반사 껍질','크로뮴 도금에서 착안한 반사 곡면 껍질 세 장'),
 ('층진 광석 탑','망가니즈 광석과 합금의 쓰임을 층진 결정으로 표현'),
 ('자성 말굽 구조','철의 자성에서 착안한 두 극의 말굽 구조'),
 ('코발트 터빈','코발트 내열 합금에서 착안한 여섯 날개 터빈'),
 ('니켈 주화','니켈의 주화 쓰임에서 착안한 이중 테두리 원판'),
 ('구리 전도 코일','구리의 전기전도성과 권선 용도를 실제 나선 코일로 표현'),
 ('아연 육각 기둥','아연의 육방 결정에서 착안한 세 육각 기둥'),
 ('액체 금속 방울','갈륨의 낮은 녹는점에서 착안한 방울·웅덩이·위성방울'),
)


def rgb(number,factor=1):
    value=COLORS[number-1]
    return tuple((int(value[i:i+2],16)/255)**2.2*factor for i in (0,2,4))


def transformed(mesh,pos=(0,0,0),angles=(0,0,0),scale=(1,1,1)):
    v,ix=mesh;v=v.copy()
    r=atom.rotation((0,0,1),math.radians(angles[2]))@atom.rotation((0,1,0),math.radians(angles[1]))@atom.rotation((1,0,0),math.radians(angles[0]))
    v[:,:3]=(v[:,:3]*np.asarray(scale))@r.T+np.asarray(pos)
    normals=(v[:,3:]/np.asarray(scale))@r.T
    v[:,3:]=normals/np.linalg.norm(normals,axis=1)[:,None]
    return v,ix


def lathe(profile,sides=64,smooth=True):
    """회전체의 실제 앞뒤·옆면을 만들며 다각 단면은 평면 법선을 보존합니다."""
    vertices=[];indices=[]
    for row in range(len(profile)-1):
        radius,y=profile[row];next_radius,next_y=profile[row+1]
        for j in range(sides):
            a=math.tau*j/sides;b=math.tau*(j+1)/sides
            corners=[(radius*math.cos(a),y,radius*math.sin(a)),(radius*math.cos(b),y,radius*math.sin(b)),
                     (next_radius*math.cos(b),next_y,next_radius*math.sin(b)),(next_radius*math.cos(a),next_y,next_radius*math.sin(a))]
            start=len(vertices)
            for k,p in enumerate(corners):
                t=(a if k in (0,3) else b) if smooth else (a+b)/2
                n=np.array([(next_y-y)*math.cos(t),radius-next_radius,(next_y-y)*math.sin(t)])
                n/=np.linalg.norm(n)
                vertices.append((*p,*n))
            indices.extend((start,start+1,start+2,start,start+2,start+3))
    return finish(vertices,indices)


def tube(points,radius=3,closed=False,sides=14):
    """3D 경로를 따라 원형 단면을 운반합니다. 코일은 실제 깊이를 가집니다."""
    points=np.asarray(points,dtype=float);vertices=[];indices=[];count=len(points)
    for i,p in enumerate(points):
        before=points[(i-1)%count] if closed or i else points[0]
        after=points[(i+1)%count] if closed or i<count-1 else points[-1]
        tangent=after-before;tangent/=np.linalg.norm(tangent)
        up=np.array([0.,1.,0.]) if abs(tangent[1])<.95 else np.array([1.,0.,0.])
        side=np.cross(tangent,up);side/=np.linalg.norm(side);vertical=np.cross(tangent,side)
        for j in range(sides):
            n=side*math.cos(math.tau*j/sides)+vertical*math.sin(math.tau*j/sides)
            vertices.append((*list(p+radius*n),*list(n)))
    for i in range(count if closed else count-1):
        for j in range(sides):
            a=i*sides+j;b=((i+1)%count)*sides+j;c=((i+1)%count)*sides+(j+1)%sides;d=i*sides+(j+1)%sides
            indices.extend((a,b,c,a,c,d))
    # 끝점은 작은 구면으로 가려지는 조립부이며 열린 단면의 용도를 기록합니다.
    return finish(vertices,indices)


def design(number):
    parts=[]
    def add(mesh,pos=(0,0,0),angles=(0,0,0),scale=(1,1,1),shade=1,metal=.83,rough=.24):
        parts.append((transformed(mesh,pos,angles,scale),rgb(number,shade),metal,rough))
    def orb(radius,pos=(0,0,0),scale=(1,1,1),shade=1):add(atom.sphere_mesh(radius,48,24),pos=pos,scale=scale,shade=shade)
    def bar(size,pos=(0,0,0),angles=(0,0,0),shade=1):add(box(size,min(2,min(size)/3),8),pos,angles,shade=shade)
    crystal=lambda r,h,n=6:lathe([(0,-h/2),(r,-h*.2),(r*.7,h*.27),(0,h/2)],n,False)
    if number==1:
        add(lathe([(0,-28),(13,-25),(23,-14),(24,-4),(19,10),(8,24),(0,34)],72),angles=(0,0,-12))
    elif number==2:
        orb(21,(-13,-5,0),scale=(.9,1.18,1));orb(16,(16,14,4),scale=(.9,1.2,1),shade=.65)
    elif number==3:
        bar((39,52,27),angles=(8,-18,-8));bar((19,7,17),(0,30,0));bar((28,5,4),(0,4,17),shade=.27);bar((5,20,4),(0,4,17),shade=.27)
    elif number==4:
        for angle in (-38,38):bar((12,65,19),angles=(5,0,angle))
        orb(9,(0,0,11),shade=.45)
    elif number==5:add(crystal(32,62,5),angles=(17,23,8))
    elif number==6:add(lathe([(0,-33),(32,5),(27,19),(15,27),(0,27)],8,False),angles=(8,15,-8),metal=.65,rough=.13)
    elif number==7:
        orb(18,(-21,0,0));orb(18,(21,0,0))
        for y in (-8,0,8):bar((32,4,6),(0,y,3))
    elif number==8:
        orb(25,(-10,-7,0));orb(23,(12,12,6),shade=.65)
    elif number==9:
        for pos,angle in (((-13,-12,0),-15),((13,-6,0),20),((0,15,2),0)):add(crystal(17,40,4),pos,angles=(0,15,angle))
    elif number==10:
        ts=np.linspace(0,math.tau,160,endpoint=False);add(tube([(26*math.cos(t),27*math.sin(t),10*math.sin(2*t)) for t in ts],6,True),angles=(12,18,0))
    elif number==11:
        for x in (-13,13):
            for y in (-13,13):bar((23,23,31),(x,y,0),angles=(8,-15,0))
    elif number==12:
        for angle in range(0,360,60):bar((9,61,12),angles=(0,0,angle))
        orb(12,(0,0,9),shade=.65)
    elif number==13:
        for z,y in ((-12,10),(0,0),(12,-10)):bar((49,26,4),(0,y,z),angles=(20,-18,12),shade=.8+z/80)
    elif number==14:
        add(lathe([(0,-3),(31,-3),(31,3),(0,3)],72),angles=(67,0,-13),shade=.6)
        for x in (-12,0,12):
            for y in (-12,0,12):bar((9,9,3),(x,y,8),angles=(0,0,-13),shade=1.3)
    elif number==15:
        points=[(-21,-17,5),(21,-17,5),(0,24,5),(0,0,-21)]
        for p in points:orb(11,p)
        for i in range(4):
            for j in range(i):add(tube([points[i],points[j]],2.5))
    elif number==16:
        for i in range(8):
            t=math.tau*i/8;add(crystal(9,25,5),(24*math.cos(t),19*math.sin(t),4*math.cos(2*t)),angles=(0,0,math.degrees(t)-90))
    elif number==17:
        for x,angle in ((-16,-12),(16,12)):add(lathe([(0,-27),(12,-25),(12,19),(6,27),(0,27)],6,False),(x,0,0),angles=(0,10,angle))
        bar((22,8,10))
    elif number==18:
        for x in (-22,22):
            for y in (-22,22):bar((5,5,44),(x,y,0))
        for z in (-22,22):
            for y in (-22,22):bar((44,5,5),(0,y,z))
            for x in (-22,22):bar((5,44,5),(x,0,z))
        parts=[(transformed(mesh,angles=(18,25,12)),c,m,r) for mesh,c,m,r in parts]
    elif number==19:
        for angle in (0,120,240):add(atom.sphere_mesh(15,48,24),(15*math.sin(math.radians(angle)),15*math.cos(math.radians(angle)),0),angles=(0,0,-angle),scale=(.67,1.65,.7))
    elif number==20:bar((43,44,36),angles=(20,25,24));bar((29,4,4),(0,7,24),angles=(0,0,24),shade=.5)
    elif number==21:
        for angle in (0,120,240):
            t=math.radians(angle);add(box((14,32,7),3,8),(16*math.sin(t),16*math.cos(t),0),angles=(17,12,-angle-18))
        orb(10,(0,0,8),shade=.5)
    elif number==22:
        add(lathe([(0,-18),(17,-18),(17,12),(30,12),(30,25),(0,25)],6,False),angles=(26,15,8))
        add(arc(12,0,math.tau,5,4),(0,19,17),angles=(0,0,0),shade=.35)
    elif number==23:
        bar((12,59,18),(-11,0,0),angles=(0,0,23));bar((12,59,18),(11,0,0),angles=(0,0,-23))
    elif number==24:
        for angle in (-55,0,55):add(arc(27,.2,math.pi-.2,9,8),angles=(20,angle,angle),metal=1,rough=.12)
    elif number==25:
        for y,r,h in ((-21,24,17),(-2,20,22),(20,14,25)):add(crystal(r,h,5),(0,y,0),angles=(0,y*2,0),shade=1+y/100)
    elif number==26:
        add(arc(22,math.pi,math.tau,15,18),pos=(0,2,0),angles=(0,0,0))
        for x in (-22,22):bar((15,29,18),(x,16,0));bar((15,8,19),(x,31,0),shade=.35)
    elif number==27:
        for angle in range(0,360,60):
            t=math.radians(angle);bar((13,28,11),(19*math.sin(t),19*math.cos(t),0),angles=(16,0,-angle-25))
        orb(12,(0,0,9),shade=.45)
    elif number==28:
        add(lathe([(0,-6),(29,-6),(29,6),(0,6)],64),angles=(76,15,0))
        add(arc(24,0,math.tau,3,4),(0,0,12));bar((6,26,4),(0,0,14),angles=(0,0,-25),shade=.5)
    elif number==29:
        ts=np.linspace(0,math.tau*3.5,220);add(tube([(22*math.cos(t),-28+56*t/(math.tau*3.5),22*math.sin(t)) for t in ts],4.7),angles=(12,10,-10),metal=1,rough=.19)
    elif number==30:
        for x,y,h in ((-16,-6,42),(0,5,61),(16,-10,34)):add(lathe([(0,-h/2),(10,-h/2),(10,h/2),(0,h/2)],6,False),(x,y,0),angles=(7,15,0))
    elif number==31:
        orb(27,(0,-18,0),scale=(1.2,.35,.9));add(lathe([(0,-15),(17,-12),(21,0),(15,13),(4,30),(0,36)],64),pos=(-5,0,2),angles=(0,0,-16),metal=1,rough=.14);orb(8,(25,8,6));orb(5,(-25,-5,7))
    return parts


def rgb_shader():
    """기존 검증된 스튜디오 조명을 RGB 금속 반사율로 확장합니다."""
    s=atom.FRAGMENT.replace('uniform float base_color;','uniform vec3 base_color;')
    for name in ('f0','fresnel','reflected','f','specular','diffuse','radiance'):
        s=s.replace('float '+name+' =','vec3 '+name+' =')
    s=s.replace('mix(.04,base_color,metallic)','mix(vec3(.04),base_color,metallic)')
    s=s.replace('float display = pow(aces(radiance),1.0/2.2);','vec3 display = pow(vec3(aces(radiance.r),aces(radiance.g),aces(radiance.b)),vec3(1.0/2.2));')
    return s.replace('vec4(display,display,display,1.0)','vec4(display,1.0)')


def orbit_mesh(number,index):
    """원소별 단면 폭과 완만한 가장자리 장식을 실제 메시로 변주합니다."""
    radius=atom.RADII[index];width=2.0+(number%5)*.22;depth=1.35+(number%3)*.15
    vertices=[];indices=[];segments=160;sections=24
    waves=3+number%5;amplitude=.0 if number%3==0 else .45 if number%3==1 else .8
    for i in range(segments):
        t=math.tau*i/segments;c,s=math.cos(t),math.sin(t)
        center=radius+amplitude*math.cos(waves*t+index)
        derivative=-amplitude*waves*math.sin(waves*t+index)
        for j in range(sections):
            a=math.tau*j/sections
            # 표면 편미분의 외적으로 파형의 실제 월드 법선을 구합니다.
            radial=center+width*math.cos(a)
            dt=np.array([derivative*c-radial*s,derivative*s+radial*c,0.])
            da=np.array([-width*math.sin(a)*c,-width*math.sin(a)*s,depth*math.cos(a)])
            n=np.cross(dt,da);n/=np.linalg.norm(n)
            vertices.append((radial*c,radial*s,depth*math.sin(a),*n))
    for i in range(segments):
        for j in range(sections):
            a=i*sections+j;b=((i+1)%segments)*sections+j;c=((i+1)%segments)*sections+(j+1)%sections;d=i*sections+(j+1)%sections
            indices.extend((a,b,c,a,c,d))
    return finish(vertices,indices)


class ElementRenderer(atom.Renderer):
    def __init__(self,number,size=SIZE):
        self.number=number;self.parts=design(number)
        # 기존 도구 파일은 바꾸지 않고 이 제작 프로세스에서만 RGB 셰이더를 사용합니다.
        shader=atom.FRAGMENT;atom.FRAGMENT=rgb_shader()
        try:super().__init__(size,2,[orbit_mesh(number,i) for i in range(3)]+[mesh for mesh,*_ in self.parts]+[atom.sphere_mesh(3.25,32,16)])
        finally:atom.FRAGMENT=shader

    def render(self,elapsed):
        self.target.use();self.target.clear(0,0,0,0,depth=1)
        for i in range(3):
            matrix=np.eye(4);matrix[:3,:3]=atom.ring_rotation(i,elapsed)
            # 서로 다른 중심을 가리지 않도록 금속 링의 색은 절제합니다.
            color=tuple(.25+.45*v for v in rgb(self.number))
            self.draw(i,matrix,1,color,.2)
        # 중심은 느린 작은 요동만 사용해 고유 실루엣이 계속 읽히게 합니다.
        matrix=np.eye(4);matrix[:3,:3]=atom.rotation((0,1,0),.18*math.sin(math.tau*elapsed/PERIOD))
        for i,(_,color,metal,rough) in enumerate(self.parts):self.draw(i+3,matrix,metal,color,rough)
        for i in range(3):
            matrix=np.eye(4);matrix[:3,3]=atom.electron_position(i,elapsed)
            self.draw(len(self.meshes)-1,matrix,.9,rgb(self.number),.19)
        self.ctx.copy_framebuffer(self.resolved,self.target)
        raw=self.resolved.read(components=4,alignment=1)
        im=Image.frombytes('RGBa',(self.render_size,self.render_size),raw).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        im=im.resize((self.size,self.size),Image.Resampling.LANCZOS).convert('RGBA');pixels=np.asarray(im).copy();pixels[pixels[:,:,3]==0,:3]=0
        return Image.fromarray(pixels)


def geometry_hash(parts):
    digest=hashlib.sha256()
    for (v,ix),*_ in parts:digest.update(v.tobytes());digest.update(ix.tobytes())
    return digest.hexdigest()


def export_glb(path,renderer):
    """0초의 원본 기하·법선·RGB PBR 재질을 표준 바이너리로 보존합니다."""
    binary=bytearray();views=[];accessors=[];meshes=[];materials=[]
    def accessor(array,kind,component,target,bounds=False):
        array=np.ascontiguousarray(array);binary.extend(b'\0'*((-len(binary))%4));offset=len(binary);binary.extend(array.tobytes())
        views.append({'buffer':0,'byteOffset':offset,'byteLength':array.nbytes,'target':target})
        item={'bufferView':len(views)-1,'componentType':component,'count':len(array),'type':kind}
        if bounds:item.update(min=array.min(axis=0).tolist(),max=array.max(axis=0).tolist())
        accessors.append(item);return len(accessors)-1
    parts=[]
    for i in range(3):
        v,ix=renderer.meshes[i];v=v.copy();matrix=atom.ring_rotation(i,0);v[:,:3]=v[:,:3]@matrix.T;v[:,3:]=v[:,3:]@matrix.T
        parts.append(((v,ix),tuple(.25+.45*c for c in rgb(renderer.number)),1,.2))
    parts.extend(renderer.parts)
    for i in range(3):parts.append((transformed(renderer.meshes[-1],atom.electron_position(i,0)),rgb(renderer.number),.9,.19))
    for i,((v,ix),color,metal,rough) in enumerate(parts):
        position=accessor((v[:,:3]*.01).astype('<f4'),'VEC3',5126,34962,True);normal=accessor(v[:,3:].astype('<f4'),'VEC3',5126,34962);indices=accessor(ix.astype('<u4'),'SCALAR',5125,34963)
        materials.append({'pbrMetallicRoughness':{'baseColorFactor':[*color,1],'metallicFactor':metal,'roughnessFactor':rough}})
        meshes.append({'primitives':[{'attributes':{'POSITION':position,'NORMAL':normal},'indices':indices,'material':i}]})
    doc={'asset':{'version':'2.0','generator':'원소31종 실제RGB금속 메시'},'scene':0,'scenes':[{'nodes':list(range(len(meshes)))}],'nodes':[{'mesh':i} for i in range(len(meshes))],'meshes':meshes,'materials':materials,'buffers':[{'byteLength':len(binary)}],'bufferViews':views,'accessors':accessors,'extras':{'pose_seconds':0,'units':'meter; 제작1단위=0.01m','animation':'이 GLB는0초 원본형상입니다. 연속모션은 제작도구와18초PNG를 참조','lighting':'절차적스튜디오환경은GLB에미포함'}}
    encoded=json.dumps(doc,ensure_ascii=False,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4);binary.extend(b'\0'*((-len(binary))%4))
    path.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(encoded)+len(binary))+struct.pack('<I4s',len(encoded),b'JSON')+encoded+struct.pack('<I4s',len(binary),b'BIN\0')+binary)


def record(number,renderer):
    e=ELEMENTS[number-1]
    return {'number':number,'symbol':e.symbol,'name':e.name,'color':'#'+COLORS[number-1],'shape':FEATURES[number-1][0],
            'inspiration':FEATURES[number-1][1],'disclaimer':'특성·쓰임에서 착안한 디자인 조형. 실제 원자 모습·전자배치·불꽃색 재현 아님',
            'geometry_sha256':geometry_hash(renderer.parts),'ring_variation':{'section_width':4.0+(number%5)*.44,'section_depth':2.7+(number%3)*.3,'edge_waves':3+number%5,'edge_amplitude':0 if number%3==0 else .45 if number%3==1 else .8},'parts':len(renderer.parts),'triangles':sum(len(ix)//3 for (v,ix),*_ in renderer.parts),
            'renderer':renderer.ctx.info['GL_RENDERER'],'depth_buffer':True,'normal_mesh':True,'lighting':'RGB GGX 금속 /48표본 스튜디오 반사 /4xMSAA와2배초과표본',
            'source':'tools/render_elements3d.py','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def preview(output):
    output.mkdir(parents=True,exist_ok=True);records=[];start=time.perf_counter()
    sheet=Image.new('RGB',(6*224,6*252),(20,24,30));font=ImageFont.truetype(str(ROOT/'assets/SUIT-SemiBold.ttf'),16)
    for number in range(1,32):
        renderer=ElementRenderer(number,296)
        try:
            image=renderer.render(0);name=f'{number:02d}_{ELEMENTS[number-1].symbol}.png';image.save(output/name)
            small=image.resize((208,208),Image.Resampling.LANCZOS);x=(number-1)%6*224;y=(number-1)//6*252
            sheet.paste(atom.composite(small,22),(x+8,y));ImageDraw.Draw(sheet).text((x+12,y+210),f'{number:02d} {ELEMENTS[number-1].symbol} · {FEATURES[number-1][0]}',font=font,fill=(230,235,245))
            info=record(number,renderer);info['preview']=name;records.append(info)
        finally:renderer.close()
    sheet.save(output/'31개_형상_접촉시트.jpg',quality=95)
    (output/'manifest.json').write_text(json.dumps({'schema_version':1,'same_time_seconds':0,'elements':records,'elapsed_seconds':time.perf_counter()-start},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'preview':str(output),'elapsed_seconds':time.perf_counter()-start,'distinct_geometry':len({r['geometry_sha256'] for r in records})},ensure_ascii=False))


def bake(output,numbers):
    output.mkdir(parents=True,exist_ok=True)
    for number in numbers:
        folder=output/f'{number:02d}_{ELEMENTS[number-1].symbol}';folder.mkdir(exist_ok=True)
        if (folder/'manifest.json').exists():raise FileExistsError(str(folder/'manifest.json'))
        start=time.perf_counter();renderer=ElementRenderer(number);hashes={}
        try:
            first=renderer.render(0);assert first.tobytes()==renderer.render(PERIOD).tobytes(),'위치 루프 픽셀 불일치'
            export_glb(folder/'model.glb',renderer)
            with zipfile.ZipFile(folder/'frames.zip','w',compression=zipfile.ZIP_STORED) as archive:
                for i in range(COUNT):
                    image=first if i==0 else renderer.render(i/FPS);pixels=np.asarray(image)
                    assert not np.any(pixels[pixels[:,:,3]==0,:3]);assert not any(pixels[y,x,3] for x,y in ((0,0),(191,0),(0,191),(191,191)))
                    stream=io.BytesIO();image.save(stream,format='PNG');raw=stream.getvalue();name=f'frame_{i:04d}.png';archive.writestr(name,raw);hashes[name]=hashlib.sha256(raw).hexdigest()
            info=record(number,renderer);info.update(schema_version=1,width=SIZE,height=SIZE,fps=FPS,period_seconds=PERIOD,frame_count=COUNT,frame_pattern='frame_{:04d}.png',archive='frames.zip',archive_sha256=hashlib.sha256((folder/'frames.zip').read_bytes()).hexdigest(),glb='model.glb',glb_sha256=hashlib.sha256((folder/'model.glb').read_bytes()).hexdigest(),loop_pixels_equal=True,elapsed_seconds=time.perf_counter()-start)
            (folder/'manifest.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8');(folder/'frame_hashes.json').write_text(json.dumps(hashes),encoding='utf-8')
            print(json.dumps({'number':number,'seconds':info['elapsed_seconds'],'bytes':(folder/'frames.zip').stat().st_size}),flush=True)
        finally:renderer.close()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--bake',action='store_true');parser.add_argument('--output',type=Path,required=True);parser.add_argument('--numbers',default='1-31');args=parser.parse_args()
    if args.preview:preview(args.output)
    if args.bake:
        numbers=list(range(int(args.numbers.split('-')[0]),int(args.numbers.split('-')[1])+1)) if '-' in args.numbers else [int(v) for v in args.numbers.split(',')]
        bake(args.output,numbers)


if __name__=='__main__':
    try:main()
    except Exception:
        folder=ROOT/'work/elements21';folder.mkdir(parents=True,exist_ok=True)
        states=[json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'.codex/routing-state').glob('*.json')];state=next(s for s in states if s.get('task_id')=='orbit-monochrome-motion')
        report={'kst':datetime.now(timezone(timedelta(hours=9))).isoformat(),'session':state['session_id'],'task':state['task_id'],'argv':[sys.executable,*sys.orig_argv[1:]],'cwd':str(Path.cwd()),'exit_code':1,'error':traceback.format_exc(),'repair_used':state['repair_used'],'input_fix_used':state['input_fix_used'],'changed':'새 제작도구만 변경'}
        (folder/f'failure-{time.time_ns()}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');raise
