"""내부 대시보드의 진주와 유선형 금속 조형을 실제 GPU 메시로 제작합니다."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone, timedelta
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / '17차/work/render-deps'))
import render_atom3d as atom
from render_elements3d import rgb_shader
from render_atom3d import np, Image

SIZE, FPS, PERIOD, COUNT = 384, 30, 12, 360
AXES = ((.7, 1., .3), (-.8, .25, 1.))
MATERIALS = (((.75,.82,.84),1.,.22), ((.74,.70,.83),1.,.24),
             ((.88,.91,.92),.18,.28), ((.63,.85,.79),.9,.19), ((.80,.75,.91),.9,.20))
NAMES = ('outer_silver_ribbon', 'inner_lilac_ribbon', 'pearl_core', 'mint_satellite', 'lilac_satellite')


def ribbon_mesh(radius, width, depth, warp, phase):
    """비평면 중심선과 한 번 비튼 둥근 타원 단면으로 닫힌 리본을 만듭니다."""
    segments, sections = 288, 48
    ts = np.arange(segments, dtype=float) * math.tau / segments
    aa = np.arange(sections, dtype=float) * math.tau / sections
    vertices = np.zeros((segments, sections, 3), dtype=float)
    for i,t in enumerate(ts):
        radial = np.array([math.cos(t), math.sin(t), 0.], dtype=float)
        center = radial * (radius + 2.8*math.cos(2*t+phase))
        center[1] *= .86
        center[2] = warp*math.sin(2*t+phase)
        twist = t + .35*math.sin(t+phase)
        side = radial*math.cos(twist) + np.array([0.,0.,1.])*math.sin(twist)
        up = -radial*math.sin(twist) + np.array([0.,0.,1.])*math.cos(twist)
        vertices[i] = center + width*np.cos(aa)[:,None]*side + depth*np.sin(aa)[:,None]*up
    dt = np.roll(vertices,-1,axis=0)-np.roll(vertices,1,axis=0)
    da = np.roll(vertices,-1,axis=1)-np.roll(vertices,1,axis=1)
    normals = np.cross(dt,da)
    normals /= np.linalg.norm(normals,axis=2)[:,:,None]
    indices=[]
    for i in range(segments):
        for j in range(sections):
            a=i*sections+j; b=((i+1)%segments)*sections+j
            c=((i+1)%segments)*sections+(j+1)%sections; d=i*sections+(j+1)%sections
            indices.extend((a,b,c,a,c,d))
    return np.concatenate((vertices,normals),axis=2).reshape(-1,6).astype('f4'), np.asarray(indices,dtype='u4')


def model_matrix(index, elapsed):
    """독립 축의 완만한 요동과 부유를 12초의 정확한 주기로 연결합니다."""
    phase = math.tau*(elapsed % PERIOD)/PERIOD
    matrix = np.eye(4)
    if index < 2:
        initial = atom.rotation((0,0,1),(-.40,.65)[index]) @ atom.rotation((1,0,0),(.57,-.58)[index])
        angle = (.31,-.39)[index]*math.sin(phase+index*.7)
        matrix[:3,:3] = atom.rotation(AXES[index], angle) @ initial
        matrix[1,3] = (1.3,-1.8)[index]*math.sin(phase+index)
    elif index == 2:
        matrix[:3,:3] *= 1+.022*math.sin(phase)
        matrix[:3,3] = (0,1.6*math.sin(phase+.3),3.)
    else:
        offset = index-3
        matrix[:3,3] = ((-45,41)[offset]+2*math.cos(phase+offset),
                       (36,-34)[offset]+3*math.sin(phase+offset), (15,23)[offset]+4*math.sin(phase+.5+offset))
    return matrix


class UsageRenderer(atom.Renderer):
    def __init__(self):
        meshes = [ribbon_mesh(51,7.2,3.6,7,.3), ribbon_mesh(36,5.5,3.4,5,1.2),
                  atom.sphere_mesh(20.5,128,64), atom.sphere_mesh(6,64,32), atom.sphere_mesh(4.2,64,32)]
        shader = atom.FRAGMENT
        atom.FRAGMENT = rgb_shader().replace('vec3 reflected = environment * fresnel',
            'vec3 reflected = mix(vec3(.94,1.0,.98),vec3(1.0,.94,1.0),clamp(r.x*.5+.5,0.0,1.0)) * environment * fresnel')
        try: super().__init__(SIZE,2,meshes)
        finally: atom.FRAGMENT=shader

    def render(self, elapsed):
        self.target.use(); self.target.clear(0,0,0,0,depth=1)
        for i,(color,metal,rough) in enumerate(MATERIALS):
            self.draw(i,model_matrix(i,elapsed),metal,color,rough)
        self.ctx.copy_framebuffer(self.resolved,self.target)
        raw = self.resolved.read(components=4,alignment=1)
        # MSAA가 만든 사전곱 RGBA를 그 상태로 축소한 뒤 직선 알파 PNG로 바꿉니다.
        image = Image.frombytes('RGBa',(self.render_size,self.render_size),raw).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        image = image.resize((SIZE,SIZE),Image.Resampling.LANCZOS).convert('RGBA')
        pixels=np.asarray(image).copy(); pixels[pixels[:,:,3]==0,:3]=0
        return Image.fromarray(pixels)


def motion_record():
    epsilon=.0001
    position=max(float(np.max(np.abs(model_matrix(i,0)-model_matrix(i,PERIOD)))) for i in range(5))
    velocity=max(float(np.max(np.abs((model_matrix(i,epsilon)-model_matrix(i,-epsilon))/(2*epsilon)-
                 (model_matrix(i,PERIOD+epsilon)-model_matrix(i,PERIOD-epsilon))/(2*epsilon)))) for i in range(5))
    samples=[{'seconds':j/FPS,'matrices':[model_matrix(i,j/FPS).tolist() for i in range(5)]} for j in range(COUNT+1)]
    dots=[float(np.dot(model_matrix(0,j/FPS)[:3,2],model_matrix(1,j/FPS)[:3,2])) for j in range(COUNT)]
    assert position<1e-10 and velocity<1e-7
    assert max(dots)-min(dots)>.1, '독립 축의 상대 기울기 변화가 부족합니다.'
    return {'period_seconds':PERIOD,'axes':AXES,'loop_matrix_max_error':position,'loop_velocity_max_error':velocity,
            'relative_normal_dot_span':max(dots)-min(dots),'samples':samples}


def export_glb(path, renderer):
    """렌더와 같은 0초 변환·법선·재질을 적용한 GLB2를 보존합니다."""
    binary=bytearray(); views=[]; accessors=[]; meshes=[]; materials=[]
    def accessor(array,kind,component,target,bounds=False):
        array=np.ascontiguousarray(array); binary.extend(b'\0'*((-len(binary))%4)); offset=len(binary); binary.extend(array.tobytes())
        views.append({'buffer':0,'byteOffset':offset,'byteLength':array.nbytes,'target':target})
        item={'bufferView':len(views)-1,'componentType':component,'count':len(array),'type':kind}
        if bounds:item.update(min=array.min(axis=0).tolist(),max=array.max(axis=0).tolist())
        accessors.append(item); return len(accessors)-1
    for i,(vertices,indices) in enumerate(renderer.meshes):
        matrix=model_matrix(i,0); transform=matrix[:3,:3]
        xyz=vertices[:,:3]@transform.T+matrix[:3,3]
        normals=vertices[:,3:]@np.linalg.inv(transform); normals/=np.linalg.norm(normals,axis=1)[:,None]
        pos=accessor((xyz*.01).astype('<f4'),'VEC3',5126,34962,True)
        normal=accessor(normals.astype('<f4'),'VEC3',5126,34962)
        ix=accessor(indices.astype('<u4'),'SCALAR',5125,34963)
        color,metal,rough=MATERIALS[i]
        materials.append({'name':NAMES[i],'pbrMetallicRoughness':{'baseColorFactor':[*color,1],'metallicFactor':metal,'roughnessFactor':rough}})
        meshes.append({'name':NAMES[i],'primitives':[{'attributes':{'POSITION':pos,'NORMAL':normal},'indices':ix,'material':i}]})
    doc={'asset':{'version':'2.0','generator':'Codex Orbit 내부 조형 제작기'},'scene':0,'scenes':[{'nodes':list(range(5))}],
         'nodes':[{'name':NAMES[i],'mesh':i} for i in range(5)],'meshes':meshes,'materials':materials,
         'buffers':[{'byteLength':len(binary)}],'bufferViews':views,'accessors':accessors,
         'extras':{'pose_seconds':0,'units':'meter; 제작1단위=0.01m','animation':'0초 정적 원본;12초 모션은 제작기와motion.json에 보존','lighting':'절차 조명은 GLB에 포함하지 않음'}}
    encoded=json.dumps(doc,ensure_ascii=False,separators=(',',':')).encode(); encoded+=b' '*((-len(encoded))%4); binary.extend(b'\0'*((-len(binary))%4))
    path.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(encoded)+len(binary))+struct.pack('<I4s',len(encoded),b'JSON')+encoded+struct.pack('<I4s',len(binary),b'BIN\0')+binary)


def metadata(renderer):
    return {'geometry':{'names':NAMES,'triangles':[len(ix)//3 for _,ix in renderer.meshes],'depth_buffer':True,'normals':True,'decoration_only':True},
            'lighting':{'model':'RGB GGX +48표본 절차적 스튜디오 반사','alpha':'MSAA premultiplied → premultiplied 축소 → straight RGBA PNG','antialiasing':'4x MSAA 및2배 초과표본','floor':False},
            'source':{'tool':'tools/render_usage3d.py','sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      'renderer':renderer.ctx.info['GL_RENDERER'],'opengl':renderer.ctx.info['GL_VERSION'],'external_meshes':False,'external_hdri':False,'runtime':'Qt PNG만 사용'}}


def preview(output):
    output.mkdir(parents=True,exist_ok=True); start=time.perf_counter(); renderer=UsageRenderer()
    try:
        sheet=Image.new('RGBA',(SIZE*3,SIZE*2),(15,22,38,255)); sizes=[]
        for column,t in enumerate((0,4,8)):
            image=renderer.render(t); image.save(output/f'pose_{column}.png'); sizes.append((output/f'pose_{column}.png').stat().st_size)
            sheet.alpha_composite(image,(column*SIZE,0))
            light=Image.new('RGBA',(SIZE,SIZE),(238,241,248,255)); light.alpha_composite(image); sheet.paste(light,(column*SIZE,SIZE))
        sheet.convert('RGB').save(output/'contact.png')
        report=metadata(renderer); report.update(seconds=time.perf_counter()-start,png_bytes=sizes,estimated_archive_bytes=max(sizes)*COUNT,
            motion={k:v for k,v in motion_record().items() if k!='samples'})
        (output/'preview.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(report,ensure_ascii=False))
    finally:renderer.close()


def bake(output):
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()):raise FileExistsError('새 자산 폴더에만 제작할 수 있습니다.')
    start=time.perf_counter(); renderer=UsageRenderer(); hashes={}; bounds=[]
    try:
        export_glb(output/'model.glb',renderer)
        motion=motion_record(); (output/'motion.json').write_text(json.dumps(motion,separators=(',',':')),encoding='utf-8')
        first=renderer.render(0); assert first.tobytes()==renderer.render(PERIOD).tobytes()
        with zipfile.ZipFile(output/'frames.zip','w',compression=zipfile.ZIP_STORED) as archive:
            for index in range(COUNT):
                image=first if index==0 else renderer.render(index/FPS); pixels=np.asarray(image)
                assert not np.any(pixels[pixels[:,:,3]==0,:3])
                assert not np.any(pixels[[0,-1],:,3]) and not np.any(pixels[:,[0,-1],3]), '외곽 잘림'
                bounds.append(image.getbbox()); stream=io.BytesIO(); image.save(stream,format='PNG'); raw=stream.getvalue()
                name=f'frame_{index:04d}.png'; archive.writestr(name,raw); hashes[name]=hashlib.sha256(raw).hexdigest()
                if index%90==0:print(json.dumps({'frame':index,'seconds':time.perf_counter()-start}),flush=True)
        info=metadata(renderer); info.update(schema_version=1,width=SIZE,height=SIZE,fps=FPS,period_seconds=PERIOD,frame_count=COUNT,
            frame_pattern='frame_{:04d}.png',archive='frames.zip',archive_sha256=hashlib.sha256((output/'frames.zip').read_bytes()).hexdigest(),
            glb='model.glb',glb_sha256=hashlib.sha256((output/'model.glb').read_bytes()).hexdigest())
        (output/'manifest.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
        (output/'frame_hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
        (output/'creation_report.json').write_text(json.dumps({'seconds':time.perf_counter()-start,'frames':COUNT,'bounds':bounds,
            'archive_bytes':(output/'frames.zip').stat().st_size,'loop_rgba_equal':True,'all_edges_transparent':True,'alpha_zero_rgb_zero':True},indent=2),encoding='utf-8')
        (output/'제작_출처.txt').write_text('프로젝트에서 직접 생성한 기하·모션·절차 조명입니다. 외부 메시·사진·HDRI·텍스처를 사용하지 않았습니다.\nGLB는 0초 정적 원본이며 앱은 PNG 프레임을 재생합니다. 제작 라이브러리는 앱 런타임에 필요하지 않습니다.\n공식 근거: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html\nhttps://pillow.readthedocs.io/en/stable/handbook/concepts.html\n',encoding='utf-8')
        print(json.dumps({'frames':COUNT,'seconds':time.perf_counter()-start,'archive_bytes':(output/'frames.zip').stat().st_size}))
    finally:renderer.close()


if __name__=='__main__':
    try:
        parser=argparse.ArgumentParser(); modes=parser.add_mutually_exclusive_group(required=True)
        modes.add_argument('--preview',action='store_true'); modes.add_argument('--bake',action='store_true'); parser.add_argument('--output',type=Path,required=True)
        args=parser.parse_args(); (preview if args.preview else bake)(args.output)
    except Exception:
        state=json.loads((ROOT/'.codex/routing-state/df07fc65fbd813b9b2f33268.json').read_text(encoding='utf-8'))
        failure={'kst':datetime.now(timezone(timedelta(hours=9))).isoformat(),'session':state['session_id'],'task':state['task_id'],
                 'argv':[sys.executable,*sys.orig_argv[1:]],'cwd':str(Path.cwd()),'exit_code':1,'error':traceback.format_exc(),
                 'repair_used':state['repair_used'],'input_fix_used':state['input_fix_used'],'changed':'새 usage 제작 파일만; 기존 자산 불변'}
        folder=ROOT/'evidence/3D시안22'; folder.mkdir(parents=True,exist_ok=True)
        (folder/f'failure-{time.time_ns()}.json').write_text(json.dumps(failure,ensure_ascii=False,indent=2),encoding='utf-8'); raise
