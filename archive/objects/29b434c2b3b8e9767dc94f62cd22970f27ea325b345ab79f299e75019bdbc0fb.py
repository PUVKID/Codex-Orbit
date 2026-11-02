"""일곱 기능 기호를 실제 둥근 모서리 메시로 제작합니다."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import traceback
from datetime import datetime, timezone, timedelta
import render_atom3d as atom
from render_atom3d import np, Image

ROOT=Path(__file__).resolve().parents[1]
KEYS=('model','reasoning','time','reason','usage','refresh','history')


def finish(vertices,indices):
    """표면 법선과 삼각형 winding을 일치시킵니다."""
    v=np.asarray(vertices,dtype='f4');ix=np.asarray(indices,dtype='u4').reshape(-1,3)
    p=v[ix,:3];n=v[ix,3:].mean(axis=1)
    reverse=np.einsum('ij,ij->i',np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]),n)<0
    ix[reverse]=ix[reverse][:,[0,2,1]]
    return v,ix.reshape(-1)


def box(size,bevel=3,steps=14):
    """육면체 면을 실제 둥근 모서리와 구면 꼭짓점으로 투영합니다."""
    half=np.asarray(size,dtype=float)/2;inner=half-bevel
    vertices=[];indices=[]
    for axis in range(3):
        other=[i for i in range(3) if i!=axis]
        for sign in (-1,1):
            start=len(vertices)
            for i in range(steps+1):
                for j in range(steps+1):
                    p=np.zeros(3);p[axis]=sign*half[axis]
                    p[other]=[(2*i/steps-1)*half[other[0]],(2*j/steps-1)*half[other[1]]]
                    q=np.clip(p,-inner,inner);n=p-q;n/=np.linalg.norm(n)
                    vertices.append((*list(q+bevel*n),*list(n)))
            for i in range(steps):
                for j in range(steps):
                    a=start+i*(steps+1)+j;b=a+steps+1
                    indices.extend((a,b,a+1,a+1,b,b+1))
    return finish(vertices,indices)


def arc(radius,start,end,width=7,depth=7):
    """가림과 단면이 있는 타원 단면 곡선 및 양 끝의 실제 마개입니다."""
    vertices=[];indices=[];segments=max(24,int(abs(end-start)*24));sections=20
    for i in range(segments+1):
        t=start+(end-start)*i/segments;c,s=math.cos(t),math.sin(t)
        for j in range(sections):
            a=math.tau*j/sections;x,z=width/2*math.cos(a),depth/2*math.sin(a)
            n=np.array([math.cos(a)*c/width,math.cos(a)*s/width,math.sin(a)/depth]);n/=np.linalg.norm(n)
            vertices.append(((radius+x)*c,(radius+x)*s,z,*n))
    for i in range(segments):
        for j in range(sections):
            a=i*sections+j;b=(i+1)*sections+j;c=(i+1)*sections+(j+1)%sections;d=i*sections+(j+1)%sections
            indices.extend((a,b,c,a,c,d))
    for end_index,angle,sign in ((0,start,-1),(segments,end,1)):
        normal=np.array([-math.sin(angle),math.cos(angle),0])*sign
        base=len(vertices);vertices.append((radius*math.cos(angle),radius*math.sin(angle),0,*normal))
        for j in range(sections):vertices.append((*vertices[end_index*sections+j][:3],*normal))
        for j in range(sections):indices.extend((base,base+1+j,base+1+(j+1)%sections))
    return finish(vertices,indices)


def triangle(points,depth=8):
    """화살촉의 앞뒤 면과 두께를 실제 삼각형으로 만듭니다."""
    vertices=[];indices=[]
    for z,sign in ((depth/2,1),(-depth/2,-1)):
        start=len(vertices)
        vertices.extend((x,y,z,0,0,sign) for x,y in points);indices.extend((start,start+1,start+2))
    for i in range(3):
        a=np.array(points[i]);b=np.array(points[(i+1)%3]);d=b-a;n=np.array([d[1],-d[0],0.]);n/=np.linalg.norm(n)
        start=len(vertices)
        vertices.extend((p[0],p[1],z,*n) for p,z in ((a,-depth/2),(b,-depth/2),(b,depth/2),(a,depth/2)))
        indices.extend((start,start+1,start+2,start,start+2,start+3))
    return finish(vertices,indices)


def scene(kind):
    parts=[]
    def add(mesh,pos=(0,0,0),angles=(0,0,0),dark=False):
        matrix=atom.rotation((0,0,1),math.radians(angles[2]))@atom.rotation((0,1,0),math.radians(angles[1]))@atom.rotation((1,0,0),math.radians(angles[0]))
        v,ix=mesh;v=v.copy();v[:,:3]=v[:,:3]@matrix.T+np.asarray(pos);v[:,3:]=v[:,3:]@matrix.T
        parts.append(((v,ix),dark))
    if kind=='model':add(box((62,62,62),6),angles=(22,-32,-8))
    elif kind=='reasoning':
        for i in range(3):add(box((65,36,9),3),pos=(0,(i-1)*23,(i-1)*7),angles=(30,-20,-8),dark=i==0)
    elif kind=='time':
        add(arc(41,0,math.tau,9,10));add(box((8,29,8),3),pos=(0,12,6));add(box((27,8,8),3),pos=(10,-1,7),angles=(0,0,-22))
    elif kind=='reason':
        add(box((64,83,10),3),angles=(7,-13,-7),dark=True)
        for y,w in ((22,37),(3,37),(-16,25)):add(box((w,7,6),2),pos=(-3,y,9),angles=(7,-13,-7))
    elif kind=='usage':
        add(arc(40,math.radians(-35),math.radians(215),10,9))
        add(box((8,42,8),3),pos=(9,12,5),angles=(0,0,-38));add(atom.sphere_mesh(8,32,16),pos=(0,-3,6),dark=True)
    elif kind=='refresh':
        for offset in (0,math.pi):
            add(arc(33,offset+.2,offset+2.5,9,10))
            t=offset+2.5;p=np.array([33*math.cos(t),33*math.sin(t)]);tangent=np.array([-math.sin(t),math.cos(t)]);radial=np.array([math.cos(t),math.sin(t)])
            add(triangle([p+15*tangent,p-9*tangent+12*radial,p-9*tangent-12*radial]))
    elif kind=='history':
        for i in range(3):add(box((61,65,8),3),pos=((i-1)*11,(1-i)*10,i*11),angles=(7,-17,-6),dark=i<2)
        add(box((32,7,5),2),pos=(10,3,28),angles=(7,-17,-6))
    return parts


def glb(path,parts):
    binary=bytearray();views=[];accessors=[];meshes=[]
    def accessor(a,typ,component,target,bounds=False):
        a=np.ascontiguousarray(a);binary.extend(b'\0'*((-len(binary))%4));offset=len(binary);binary.extend(a.tobytes());views.append({'buffer':0,'byteOffset':offset,'byteLength':a.nbytes,'target':target})
        d={'bufferView':len(views)-1,'componentType':component,'count':len(a),'type':typ}
        if bounds:d.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
        accessors.append(d);return len(accessors)-1
    for (v,ix),dark in parts:
        p=accessor((v[:,:3]*.01).astype('<f4'),'VEC3',5126,34962,True);n=accessor(v[:,3:].astype('<f4'),'VEC3',5126,34962);i=accessor(ix.astype('<u4'),'SCALAR',5125,34963)
        meshes.append({'primitives':[{'attributes':{'POSITION':p,'NORMAL':n},'indices':i,'material':int(dark)}]})
    materials=[{'pbrMetallicRoughness':{'baseColorFactor':[b,b,b,1],'metallicFactor':m,'roughnessFactor':r}} for m,b,r in ((.95,.64,.28),(.45,.035,.36))]
    doc={'asset':{'version':'2.0','generator':'Orbit 실제 메시 기능 기호'},'scene':0,'scenes':[{'nodes':list(range(len(parts)))}],'nodes':[{'mesh':i} for i in range(len(parts))],'meshes':meshes,'materials':materials,'buffers':[{'byteLength':len(binary)}],'bufferViews':views,'accessors':accessors,'extras':{'lighting':'원자와 동일한 절차적 스튜디오 환경; 표준 GLB에는 환경 셰이더 미포함'}}
    data=json.dumps(doc,ensure_ascii=False,separators=(',',':')).encode();data+=b' '*((-len(data))%4);binary.extend(b'\0'*((-len(binary))%4))
    path.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(data)+len(binary))+struct.pack('<I4s',len(data),b'JSON')+data+struct.pack('<I4s',len(binary),b'BIN\0')+binary)


def main():
    output=Path(sys.argv[1]);output.mkdir(parents=True,exist_ok=True)
    files={};reports={};sheet=Image.new('RGB',(7*144,240),(22,22,22))
    for column,kind in enumerate(KEYS):
        parts=scene(kind);renderer=atom.Renderer(96,4,[mesh for mesh,dark in parts])
        try:
            renderer.target.use();renderer.target.clear(0,0,0,0,depth=1)
            for i,(_,dark) in enumerate(parts):renderer.draw(i,np.eye(4),*( (.45,.035,.36) if dark else (.95,.64,.28)))
            renderer.ctx.copy_framebuffer(renderer.resolved,renderer.target)
            raw=renderer.resolved.read(components=4,alignment=1)
            image=Image.frombytes('RGBa',(384,384),raw).transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((96,96),Image.Resampling.LANCZOS).convert('RGBA')
            pixels=np.asarray(image).copy();pixels[pixels[:,:,3]==0,:3]=0;image=Image.fromarray(pixels)
            image.save(output/(kind+'.png'));glb(output/(kind+'.glb'),parts)
            assert np.array_equal(pixels[:,:,0],pixels[:,:,1]) and np.array_equal(pixels[:,:,1],pixels[:,:,2])
            assert not np.any(pixels[pixels[:,:,3]==0,:3])
            assert image.getbbox() and min(image.getbbox())>0 and max(image.getbbox())<96
            triangles=0;nondegenerate=0
            for (v,ix),dark in parts:
                assert np.isfinite(v).all() and ix.max()<len(v)
                assert np.max(np.abs(np.linalg.norm(v[:,3:],axis=1)-1))<1e-5
                p=v[ix.reshape(-1,3),:3];norm=v[ix.reshape(-1,3),3:].mean(axis=1);cross=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);valid=np.linalg.norm(cross,axis=1)>1e-7
                assert np.all(np.einsum('ij,ij->i',cross,norm)[valid]>0)
                triangles+=len(ix)//3;nondegenerate+=int(valid.sum())
            reports[kind]={'triangles':triangles,'nondegenerate':nondegenerate,'bounds':image.getbbox(),'rgba':True,'grayscale':True,'alpha_zero_rgb_zero':True,'normal_winding_checked':True}
            files[kind]={'filename':kind+'.png','sha256':hashlib.sha256((output/(kind+'.png')).read_bytes()).hexdigest(),'glb':kind+'.glb','glb_sha256':hashlib.sha256((output/(kind+'.glb')).read_bytes()).hexdigest()}
            sheet.paste(atom.composite(image,22),(column*144+24,0));sheet.paste(atom.composite(image,242),(column*144+24,96))
            for j,size in enumerate((18,20,24)):
                small=image.convert('RGBa').resize((size,size),Image.Resampling.LANCZOS).convert('RGBA');sheet.paste(atom.composite(small,22),(column*144+12+j*40,204))
        finally:renderer.close()
    manifest={'schema_version':1,'width':96,'height':96,'files':files,'geometry':'실제 둥근 모서리 육면체·타원 단면 곡선·두께 있는 화살촉, 정규화 법선과 깊이 버퍼','lighting':'원자와 동일한48표본 스튜디오 환경반사/GGX; 새틴 거칠기0.28','source':{'tool':'tools/render_symbols3d.py','sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'renderer_sha256':hashlib.sha256((ROOT/'tools/render_atom3d.py').read_bytes()).hexdigest(),'external_assets':False,'license':'프로젝트 소유자 곽윤석님 사용·수정·재배포용 직접 생성 자산'}}
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');sheet.save(output/'contact_sheet.png')
    (output/'direct_validation.json').write_text(json.dumps({'kst':datetime.now(timezone(timedelta(hours=9))).isoformat(),'argv':[sys.executable,*sys.orig_argv[1:]],'cwd':str(Path.cwd()),'exit_code':0,'symbols':reports,'limits':'구현자 직접 검사; 공식 Khronos 검증 및 독립 검증은 아님'},ensure_ascii=False,indent=2),encoding='utf-8')
    (output/'LICENSE.txt').write_text('프로젝트용으로 직접 생성한 메시와 렌더입니다. 외부 모델·사진·텍스처 없음. 곽윤석님 사용·수정·재배포용입니다.\n',encoding='utf-8')
    print(json.dumps({'output':str(output),'symbols':7},ensure_ascii=False))


if __name__=='__main__':
    try:main()
    except Exception:
        state=json.loads((ROOT/'.codex/routing-state/df07fc65fbd813b9b2f33268.json').read_text(encoding='utf-8'))
        report={'kst':datetime.now(timezone(timedelta(hours=9))).isoformat(),'session':state['session_id'],'task':state['task_id'],'argv':[sys.executable,*sys.orig_argv[1:]],'cwd':str(Path.cwd()),'exit_code':1,'error':traceback.format_exc(),'repair_used':state['repair_used'],'input_fix_used':state['input_fix_used'],'changed':'소유 제작 도구만 변경'}
        folder=ROOT/'work/atom3d-preview17';(folder/('symbols-failure-'+datetime.now().strftime('%H%M%S')+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        raise
