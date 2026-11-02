"""제작 자산을 다시 읽어 프레임 계약·GLB 기하·루프를 자체 검사합니다."""
import ast
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
from datetime import datetime,timezone,timedelta
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'work/render-deps'))
import numpy as np
from PIL import Image


def validate(directory):
    count=0
    def check(condition,message):
        nonlocal count
        count+=1
        if not condition:raise AssertionError(message)
    manifest=json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
    expected={'schema_version':1,'width':296,'height':296,'fps':30,'period_seconds':18,'frame_count':540,'frame_pattern':'frame_{:04d}.png','archive':'frames.zip'}
    for key,value in expected.items():check(type(manifest[key]) is type(value) and manifest[key]==value,'계약:'+key)
    for key in ('geometry','lighting','source'):check(bool(manifest[key]),'제작 근거:'+key)
    archive=directory/'frames.zip'
    check(hashlib.sha256(archive.read_bytes()).hexdigest()==manifest['archive_sha256'],'ZIP 해시')
    hashes=json.loads((directory/'frame_hashes.json').read_text(encoding='utf-8'))
    names=[f'frame_{i:04d}.png' for i in range(540)]
    check(list(hashes)==names,'프레임 해시 목록')
    max_radius=0.;max_frame_bytes=0;pixel_hashes=set()
    with zipfile.ZipFile(archive) as package:
        check(package.namelist()==names,'정확한 ZIP 멤버와 순서')
        for name in names:
            raw=package.read(name)
            check(hashlib.sha256(raw).hexdigest()==hashes[name],name+' 해시')
            image=Image.open(io.BytesIO(raw));image.load();array=np.asarray(image)
            check(image.mode=='RGBA' and image.size==(296,296),name+' RGBA 치수')
            check(np.array_equal(array[:,:,0],array[:,:,1]) and np.array_equal(array[:,:,1],array[:,:,2]),name+' 무채색')
            check(not np.any(array[array[:,:,3]==0,:3]),name+' 투명 RGB')
            check(not any(array[y,x,3] for x,y in ((0,0),(295,0),(0,295),(295,295))),name+' 모서리')
            ys,xs=np.nonzero(array[:,:,3]>16)
            radius=float(np.max(np.hypot(xs-147.5,ys-147.5)))/2
            check(radius<=60.5,name+' 약60px 외곽')
            check(len(raw)<1024*1024,name+' 디코더 바이트 상한')
            max_radius=max(max_radius,radius);max_frame_bytes=max(max_frame_bytes,len(raw))
            pixel_hashes.add(hashlib.sha256(array.tobytes()).hexdigest())
    check(len(pixel_hashes)==540,'540개 프레임의 실제 변화')
    raw=(directory/'atom3d.glb').read_bytes()
    magic,version,length=struct.unpack_from('<4sII',raw)
    check(magic==b'glTF' and version==2 and length==len(raw),'GLB 헤더')
    json_length,json_kind=struct.unpack_from('<I4s',raw,12)
    check(json_kind==b'JSON','GLB JSON 청크')
    glb=json.loads(raw[20:20+json_length])
    bin_offset=20+json_length
    bin_length,bin_kind=struct.unpack_from('<I4s',raw,bin_offset)
    check(bin_kind==b'BIN\0' and bin_offset+8+bin_length==len(raw),'GLB 바이너리 청크')
    binary=raw[bin_offset+8:]
    def read_accessor(index):
        accessor=glb['accessors'][index];view=glb['bufferViews'][accessor['bufferView']]
        dtype={5126:'<f4',5125:'<u4',5123:'<u2'}[accessor['componentType']]
        width={'SCALAR':1,'VEC3':3,'VEC4':4}[accessor['type']]
        offset=view.get('byteOffset',0)+accessor.get('byteOffset',0)
        size=accessor['count']*width*np.dtype(dtype).itemsize
        check(offset%4==0 and offset+size<=len(binary),'GLB accessor 범위·정렬')
        array=np.frombuffer(binary,dtype=dtype,count=accessor['count']*width,offset=offset).reshape(-1,width)
        check(np.isfinite(array).all(),'GLB 유한 숫자')
        return array
    mesh_reports=[]
    for mesh in glb['meshes']:
        primitive=mesh['primitives'][0]
        positions=read_accessor(primitive['attributes']['POSITION'])
        normals=read_accessor(primitive['attributes']['NORMAL'])
        indices=read_accessor(primitive['indices']).reshape(-1)
        check(int(indices.max())<len(positions),'GLB 인덱스')
        check(np.max(np.abs(np.linalg.norm(normals,axis=1)-1))<1e-5,'GLB 단위 법선')
        triangles=positions[indices.reshape(-1,3)]
        area=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0])
        average_normal=normals[indices.reshape(-1,3)].mean(axis=1)
        dot=np.sum(area*average_normal,axis=1);nonzero=np.linalg.norm(area,axis=1)>1e-10
        check(np.all(dot[nonzero]>0),'GLB 외향 winding')
        mesh_reports.append({'name':mesh['name'],'triangles':len(dot),'nondegenerate':int(nonzero.sum()),'outward':int((dot[nonzero]>0).sum())})
    for animation in glb['animations']:
        for channel in animation['channels']:
            sampler=animation['samplers'][channel['sampler']]
            times=read_accessor(sampler['input']).reshape(-1);values=read_accessor(sampler['output'])
            check(times[0]==0 and times[-1]==18 and np.all(np.diff(times)>0),'GLB 모션 시간')
            if channel['target']['path']=='rotation':
                check(np.max(np.abs(np.linalg.norm(values,axis=1)-1))<1e-5,'GLB 단위 쿼터니언')
                check(abs(float(np.dot(values[0],values[-1])))>1-1e-5,'GLB 회전 루프')
            else:check(np.max(np.abs(values[0]-values[-1]))<1e-5,'GLB 위치 루프')
    motion=json.loads((directory/'motion.json').read_text(encoding='utf-8'))
    check(motion['loop_matrix_max_error']<1e-10 and motion['loop_electron_max_error']<1e-10,'기하 위치 루프')
    check(motion['loop_velocity_max_error']<1e-6,'기하 속도 루프')
    for pair in motion['relative_planes']:check(pair['normal_dot_max']-pair['normal_dot_min']>.5,'독립 회전 법선')
    source_hashes={}
    for relative in ('tools/render_atom3d.py','tools/atom3d_glb.py','tools/validate_atom3d.py','tools/requirements-3d.txt'):
        path=ROOT/relative;text=path.read_bytes().decode('utf-8-sig')
        check('\ufffd' not in text,'UTF8 대체 문자:'+relative)
        if path.suffix=='.py':ast.parse(text)
        source_hashes[relative]=hashlib.sha256(path.read_bytes()).hexdigest()
    check(source_hashes['tools/render_atom3d.py']==manifest['source']['tool_sha256'],'실제 제작 도구 해시')
    check(source_hashes['tools/atom3d_glb.py']==manifest['source']['export_tool_sha256'],'GLB 제작 도구 해시')
    return {'checks':count,'frames_checked':540,'unique_pixel_frames':len(pixel_hashes),'max_visible_radius_logical':max_radius,'max_frame_bytes':max_frame_bytes,'mesh_checks':mesh_reports,'source_hashes':source_hashes,'archive_sha256':manifest['archive_sha256'],'limits':['구현자 자체 검사이며 독립 verifier 영수증이 아님','외부 Khronos validator/glTF Transform 실행은 하지 않음','GLB 표준 PBR은 제작용 절차 조명 환경을 포함하지 않음','GPU 제작 결과이며 앱 실제 표시·종료·감지는 별도 검사']}


if __name__=='__main__':
    result=validate(ROOT/'assets/atom3d')
    result.update({'kst':datetime.now(timezone(timedelta(hours=9))).isoformat(),'argv':[sys.executable,*sys.orig_argv[1:]],'cwd':str(Path.cwd()),'exit_code':0,'session':'SESSION_ID','task':'orbit-monochrome-motion','repair_used':38,'input_fix_used':25})
    output=ROOT/'work/atom3d-preview/asset-validation.json'
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))
