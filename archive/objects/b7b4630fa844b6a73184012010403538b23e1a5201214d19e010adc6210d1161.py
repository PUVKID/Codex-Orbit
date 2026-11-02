"""금속 원자 메시를 제작 전용 OpenGL로 렌더하고 투명 프레임으로 저장합니다."""
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
from datetime import datetime, timezone, timedelta
import traceback
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'work' / 'render-deps'))
import moderngl
import numpy as np
from PIL import Image

PERIOD = 18.0
FPS = 30
COUNT = 540
SIZE = 296
RADII = (45.0, 51.0, 57.0)
TILTS = (50.0, 52.0, 54.0)
AZIMUTHS = (8.0, 70.0, 132.0)
AXES = ((.06, -.025, 1.), (-.04, .04, 1.), (.03, .06, 1.))
TURNS = (1, -2, 3)
ELECTRON_TURNS = (2, -3, 4)
HALF_WIDTH, HALF_DEPTH, BEVEL = 2.6, 1.4, .65
CORE_RADIUS = 22.7
CAMERA_Z = 700.0
FOV_EXTENT = 77.0

VERTEX = '''#version 330
in vec3 in_position;
in vec3 in_normal;
uniform mat4 model;
uniform mat4 view_projection;
out vec3 position;
out vec3 normal;
void main() {
    vec4 world = model * vec4(in_position, 1.0);
    position = world.xyz;
    normal = mat3(model) * in_normal;
    gl_Position = view_projection * world;
}
'''

FRAGMENT = '''#version 330
in vec3 position;
in vec3 normal;
uniform vec3 camera;
uniform float metallic;
uniform float base_color;
uniform float roughness;
out vec4 color;
const float PI = 3.14159265359;
// 실제 월드 반사 방향이 스튜디오의 긴 면광원을 바라보는 정도를 계산합니다.
float box_light(vec3 direction, vec3 center, vec3 up, vec2 bounds, float softness) {
    vec3 forward = normalize(center);
    vec3 side = normalize(cross(forward, up));
    vec3 vertical = cross(side, forward);
    float facing = dot(direction, forward);
    if (facing <= 0.0) return 0.0;
    vec2 uv = vec2(dot(direction, side), dot(direction, vertical)) / facing;
    vec2 edge = smoothstep(bounds, bounds + vec2(softness), abs(uv));
    return (1.0 - edge.x) * (1.0 - edge.y);
}
float studio(vec3 direction, float blur) {
    float value = .075 + .10 * (direction.y*.5+.5);
    value += 3.8 * box_light(direction, vec3(-.52, .72, .62), vec3(0,1,0), vec2(.27,.82), .055+blur);
    value += 2.4 * box_light(direction, vec3(.90, .05, .32), vec3(0,1,0), vec2(.105,.78), .035+blur);
    value += 2.8 * box_light(direction, vec3(.10, .90, -.48), vec3(0,0,1), vec2(.68,.12), .045+blur);
    value += .65 * box_light(direction, vec3(-.65, -.40, .35), vec3(0,1,0), vec2(.40,.62), .20+blur);
    value += .25 * box_light(direction, vec3(.2,-.4,.9), vec3(0,1,0), vec2(.8,.45), .35+blur);
    return value;
}
// 거칠기에 따른 반사 방향 원판을 고정 표본으로 적분하여 시간별 잡음을 만들지 않습니다.
float filtered_studio(vec3 reflected, float rough) {
    vec3 up = abs(reflected.y)<.95 ? vec3(0,1,0) : vec3(1,0,0);
    vec3 tangent = normalize(cross(up,reflected));
    vec3 bitangent = cross(reflected,tangent);
    float total=0.0;
    float weight_sum=0.0;
    for(int i=0;i<48;i++) {
        float radius=sqrt((float(i)+.5)/48.0);
        float theta=float(i)*2.39996323;
        float weight=exp(-2.2*radius*radius);
        vec3 sample_direction=normalize(reflected+rough*1.7*radius*(cos(theta)*tangent+sin(theta)*bitangent));
        total+=studio(sample_direction,rough*.30)*weight;
        weight_sum+=weight;
    }
    return total/weight_sum;
}
float distribution(float nh, float alpha) {
    float a2 = alpha * alpha;
    float d = nh * nh * (a2 - 1.0) + 1.0;
    return a2 / max(PI * d * d, .00001);
}
float visibility(float nv, float nl, float alpha) {
    float k = (alpha + 1.0) * (alpha + 1.0) / 8.0;
    return (nv / (nv * (1.0-k) + k)) * (nl / (nl * (1.0-k) + k));
}
float aces(float x) {
    return clamp((x*(2.51*x+.03))/(x*(2.43*x+.59)+.14),0.0,1.0);
}
void main() {
    vec3 n = normalize(normal);
    vec3 v = normalize(camera-position);
    float nv = max(dot(n,v),.001);
    vec3 r = reflect(-v,n);
    float f0 = mix(.04,base_color,metallic);
    float fresnel = f0 + (1.0-f0)*pow(1.0-nv,5.0);
    float environment = filtered_studio(r,roughness);
    float reflected = environment * fresnel * (1.0-.28*roughness);
    vec3 l = normalize(vec3(-.4,.7,.8));
    vec3 h = normalize(v+l);
    float nl = max(dot(n,l),0.0);
    float nh = max(dot(n,h),0.0);
    float vh = max(dot(v,h),0.0);
    float f = f0+(1.0-f0)*pow(1.0-vh,5.0);
    float alpha = max(.04,roughness*roughness);
    float specular = distribution(nh,alpha)*visibility(nv,nl,roughness)*f/max(4.0*nv*nl,.01);
    float diffuse = (1.0-metallic)*base_color*(.16+.48*nl);
    float radiance = reflected + diffuse + .25*specular*nl;
    float display = pow(aces(radiance),1.0/2.2);
    color = vec4(display,display,display,1.0);
}
'''


def rotation(axis, angle):
    """정규화된 실제 3D축을 중심으로 로드리게스 회전행렬을 만듭니다."""
    axis = np.asarray(axis, dtype=np.float64)
    axis /= np.linalg.norm(axis)
    x, y, z = axis
    c, s, t = math.cos(angle), math.sin(angle), 1-math.cos(angle)
    return np.array([[t*x*x+c,t*x*y-s*z,t*x*z+s*y],
                     [t*x*y+s*z,t*y*y+c,t*y*z-s*x],
                     [t*x*z-s*y,t*y*z+s*x,t*z*z+c]],dtype=np.float64)


def ring_rotation(index, elapsed):
    """링마다 다른 축·방향·속도를 사용하며 18초 후 위치와 속도가 이어집니다."""
    phase = math.tau * elapsed / PERIOD
    initial = rotation((0,0,1),math.radians(AZIMUTHS[index])) @ rotation((1,0,0),math.radians(TILTS[index]))
    return rotation(AXES[index],TURNS[index]*phase) @ initial


def electron_position(index, elapsed):
    phase = math.tau * ELECTRON_TURNS[index] * elapsed / PERIOD + index*2.1 + .65
    local = np.array([RADII[index]*math.cos(phase),RADII[index]*math.sin(phase),0.])
    return ring_rotation(index,elapsed) @ local


def ring_mesh(radius, segments=256, section_segments=48):
    """완만한 볼록 단면의 금속띠를 연속 법선으로 만들며 폭과 실제 깊이를 구분합니다."""
    section=[]
    for j in range(section_segments):
        angle=math.tau*j/section_segments
        x,z=HALF_WIDTH*math.cos(angle),HALF_DEPTH*math.sin(angle)
        nx,nz=math.cos(angle)/HALF_WIDTH,math.sin(angle)/HALF_DEPTH
        length=math.hypot(nx,nz)
        section.append((x,z,nx/length,nz/length))
    vertices=[];indices=[]
    width=len(section)
    for i in range(segments):
        theta=math.tau*i/segments
        c,s=math.cos(theta),math.sin(theta)
        for x,z,nx,nz in section:
            vertices.append(((radius+x)*c,(radius+x)*s,z,nx*c,nx*s,nz))
    for i in range(segments):
        for j in range(width):
            a=i*width+j;b=((i+1)%segments)*width+j
            c=((i+1)%segments)*width+(j+1)%width;d=i*width+(j+1)%width
            indices.extend((a,b,c,a,c,d))
    return np.asarray(vertices,dtype='f4'),np.asarray(indices,dtype='u4')


def sphere_mesh(radius, longitude=96, latitude=48):
    vertices=[];indices=[]
    for i in range(latitude+1):
        phi=math.pi*i/latitude
        for j in range(longitude+1):
            theta=math.tau*j/longitude
            n=(math.sin(phi)*math.cos(theta),math.cos(phi),math.sin(phi)*math.sin(theta))
            vertices.append((*[radius*v for v in n],*n))
    for i in range(latitude):
        for j in range(longitude):
            a=i*(longitude+1)+j;b=a+longitude+1
            indices.extend((a,a+1,b,a+1,b+1,b))
    return np.asarray(vertices,dtype='f4'),np.asarray(indices,dtype='u4')


class Renderer:
    """제작 때만 GPU를 사용하며 결과 이미지는 알파가 있는 직선 RGBA입니다."""
    def __init__(self, size=296, supersample=3):
        self.size=size;self.render_size=size*supersample
        self.ctx=moderngl.create_standalone_context(require=330)
        self.program=self.ctx.program(vertex_shader=VERTEX,fragment_shader=FRAGMENT)
        self.color_buffer=self.ctx.renderbuffer((self.render_size,self.render_size),components=4,samples=4)
        self.depth_buffer=self.ctx.depth_renderbuffer((self.render_size,self.render_size),samples=4)
        self.target=self.ctx.framebuffer([self.color_buffer],self.depth_buffer)
        self.resolved=self.ctx.simple_framebuffer((self.render_size,self.render_size),components=4,dtype='f1')
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.meshes=[ring_mesh(r) for r in RADII]+[sphere_mesh(CORE_RADIUS),sphere_mesh(3.25,48,24)]
        self.vaos=[];self.buffers=[]
        for vertices,indices in self.meshes:
            vertex_buffer=self.ctx.buffer(vertices.tobytes());index_buffer=self.ctx.buffer(indices.tobytes())
            self.buffers.extend((vertex_buffer,index_buffer))
            self.vaos.append(self.ctx.vertex_array(self.program,[(vertex_buffer,'3f 3f','in_position','in_normal')],index_buffer))
        near,far=1.,1200.
        scale=CAMERA_Z/FOV_EXTENT
        projection=np.array([[scale,0,0,0],[0,scale,0,0],[0,0,(far+near)/(near-far),2*far*near/(near-far)],[0,0,-1,0]],dtype='f4')
        view=np.eye(4,dtype='f4');view[2,3]=-CAMERA_Z
        self.program['view_projection'].write((projection@view).T.astype('f4').tobytes())
        self.program['camera'].value=(0.,0.,CAMERA_Z)

    def draw(self,index,matrix,metallic,base,roughness):
        self.program['model'].write(matrix.T.astype('f4').tobytes())
        self.program['metallic'].value=metallic
        self.program['base_color'].value=base
        self.program['roughness'].value=roughness
        self.vaos[index].render(moderngl.TRIANGLES)

    def render(self,elapsed):
        self.target.use();self.target.clear(0.,0.,0.,0.,depth=1.)
        for i in range(3):
            model=np.eye(4);model[:3,:3]=ring_rotation(i,elapsed)
            self.draw(i,model,1.,.72,.18)
        self.draw(3,np.eye(4),.30,.018,.39)
        for i in range(3):
            model=np.eye(4);model[:3,3]=electron_position(i,elapsed)
            self.draw(4,model,.95,.62,.20)
        self.ctx.copy_framebuffer(self.resolved,self.target)
        raw=self.resolved.read(components=4,alignment=1)
        image=Image.frombytes('RGBa',(self.render_size,self.render_size),raw).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        # MSAA resolve는 투명 배경과 평균되어 사전곱 색입니다. 재곱하지 않고 축소 뒤 한 번만 해제합니다.
        image=image.resize((self.size,self.size),Image.Resampling.LANCZOS).convert('RGBA')
        pixels=np.asarray(image).copy()
        pixels[pixels[:,:,3]==0,:3]=0
        image=Image.fromarray(pixels)
        return image

    def close(self):
        for vao in self.vaos:vao.release()
        for buffer in self.buffers:buffer.release()
        self.target.release();self.resolved.release();self.color_buffer.release();self.depth_buffer.release();self.program.release();self.ctx.release()


def metadata(renderer):
    return {
        'geometry':{'type':'실제 삼각형 메시와 정규화 표면 법선','ring_radii':list(RADII),'ring_width':2*HALF_WIDTH,'ring_depth':2*HALF_DEPTH,'cross_section':'폭5.2/깊이2.8의 완만한 볼록 타원 단면','core_radius':CORE_RADIUS,'electron_radius':3.25,'rings':3,'electrons':3,'units':'제작 1단위 = 논리 1px; GLB는 0.01m로 환산','pivots':[0,0,0],'initial_tilts_degrees':list(TILTS),'initial_azimuths_degrees':list(AZIMUTHS),'axes':[list(a) for a in AXES],'ring_turns_per_period':list(TURNS),'electron_turns_per_period':list(ELECTRON_TURNS),'triangles_per_mesh':[len(mesh[1])//3 for mesh in renderer.meshes],'camera':{'position':[0,0,CAMERA_Z],'half_extent_at_origin':FOV_EXTENT,'projection':'perspective'},'depth_buffer':True},
        'lighting':{'model':'GGX 직접광 + 월드 반사 방향 기반 절차적 스튜디오 환경반사','environment':'3개 긴 소프트박스와 낮은 보조광; 검은 환경의 음영','ring_metallic':1.0,'ring_roughness':.18,'core_metallic':.30,'core_roughness':.39,'color':'무채색','tone_mapping':'ACES 근사 + gamma 2.2','reflection_samples':48,'anti_aliasing':'4x MSAA + 296px의 3배 또는 600px의 2배 제작 후 축소','alpha_encoding':'MSAA 사전곱 RGBA → 사전곱 축소 → straight RGBA PNG; alpha0의 RGB0','transparent_background':True,'floor':False,'limitation':'경로추적·다중반사·물리기반 면광원 적분은 아님; GLB의 표준 PBR에는 절차 조명이 포함되지 않음'},
        'source':{'tool':'tools/render_atom3d.py','tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'renderer':renderer.ctx.info.get('GL_RENDERER'),'opengl_version':renderer.ctx.info.get('GL_VERSION'),'moderngl':moderngl.__version__,'numpy':np.__version__,'generated_geometry':True,'external_meshes':False,'external_textures':False,'runtime_gpu_required':False,'license':'이 프로젝트에서 직접 생성한 기하와 셰이더; 외부 모델·HDRI·텍스처 없음'}
    }


def composite(image,gray):
    background=Image.new('RGBA',image.size,(gray,gray,gray,255))
    return Image.alpha_composite(background,image).convert('RGB')


def preview(output):
    output.mkdir(parents=True,exist_ok=True)
    renderer=Renderer(296)
    try:
        image=renderer.render(0.)
        image.save(output/'atom3d_296.png')
        sheet=Image.new('RGB',(888,592),(20,20,20))
        for column,t in enumerate((0.,3.,7.)):
            frame=renderer.render(t)
            sheet.paste(composite(frame,20),(column*296,0))
            sheet.paste(composite(frame,242),(column*296,296))
        sheet.save(output/'dark_light_contact.png')
        report=metadata(renderer)
        report['preview_times']=[0,3,7]
        report['alpha_bbox']=image.getbbox()
        report['created_kst']=datetime.now(timezone(timedelta(hours=9))).isoformat()
        (output/'preview.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    finally:renderer.close()
    renderer=Renderer(600,2)
    try:renderer.render(0.).save(output/'atom3d_600.png')
    finally:renderer.close()
    print(json.dumps({'preview':str(output),'files':['atom3d_296.png','atom3d_600.png','dark_light_contact.png','preview.json']},ensure_ascii=False))


def motion_record():
    """실제 렌더에 쓰는 행렬·입자 좌표로 독립성 및 위치·속도 루프를 기록합니다."""
    samples=[]
    for frame in range(COUNT+1):
        elapsed=frame/FPS
        matrices=[ring_rotation(i,elapsed) for i in range(3)]
        samples.append({'frame':frame,'seconds':elapsed,'normals':[matrix[:,2].tolist() for matrix in matrices],
                        'electrons':[electron_position(i,elapsed).tolist() for i in range(3)]})
    epsilon=.0001
    position_error=max(float(np.max(np.abs(ring_rotation(i,0)-ring_rotation(i,PERIOD)))) for i in range(3))
    electron_error=max(float(np.max(np.abs(electron_position(i,0)-electron_position(i,PERIOD)))) for i in range(3))
    velocity_error=0.
    for function in (ring_rotation,electron_position):
        for i in range(3):
            first=(function(i,epsilon)-function(i,-epsilon))/(2*epsilon)
            last=(function(i,PERIOD+epsilon)-function(i,PERIOD-epsilon))/(2*epsilon)
            velocity_error=max(velocity_error,float(np.max(np.abs(first-last))))
    relations=[]
    for i,j in ((0,1),(1,2),(0,2)):
        values=[float(np.dot(sample['normals'][i],sample['normals'][j])) for sample in samples]
        relations.append({'rings':[i,j],'normal_dot_min':min(values),'normal_dot_max':max(values)})
    return {'period_seconds':int(PERIOD),'samples':samples,'loop_matrix_max_error':position_error,
            'loop_electron_max_error':electron_error,'loop_velocity_max_error':velocity_error,'relative_planes':relations}


def bake(output):
    """한 프레임만 순차 인코딩해 ZIP에 넣으며 전체 비압축 프레임을 적재하지 않습니다."""
    from atom3d_glb import export_glb
    output.mkdir(parents=True,exist_ok=True)
    archive=output/'frames.zip'
    if archive.exists() or (output/'manifest.json').exists():
        raise FileExistsError('기존 자산을 덮어쓰지 않습니다. 별도 출력 폴더를 지정하세요.')
    renderer=Renderer(SIZE)
    hashes={};bounds=[];start=time.perf_counter();first_bytes=None
    try:
        info=metadata(renderer)
        glb_report=export_glb(output/'atom3d.glb',renderer.meshes,ring_rotation,electron_position,PERIOD,CAMERA_Z,FOV_EXTENT)
        motion=motion_record()
        (output/'motion.json').write_text(json.dumps(motion,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
        with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_STORED) as package:
            for frame in range(COUNT):
                image=renderer.render(frame/FPS)
                pixels=np.asarray(image)
                if not np.array_equal(pixels[:,:,0],pixels[:,:,1]) or not np.array_equal(pixels[:,:,1],pixels[:,:,2]):
                    raise ValueError(f'무채색 검증 실패: {frame}')
                if np.any(pixels[pixels[:,:,3]==0,:3]):raise ValueError(f'알파0 색 검증 실패: {frame}')
                bounds.append(image.getbbox())
                stream=io.BytesIO();image.save(stream,format='PNG',compress_level=6);data=stream.getvalue()
                name=f'frame_{frame:04d}.png'
                package.writestr(name,data)
                hashes[name]=hashlib.sha256(data).hexdigest()
                if frame==0:first_bytes=image.tobytes()
                if frame%90==0:print(json.dumps({'frame':frame,'elapsed_seconds':round(time.perf_counter()-start,3)}),flush=True)
        loop_image_equal=renderer.render(PERIOD).tobytes()==first_bytes
        if not loop_image_equal:raise ValueError('0초와18초의 실제 RGBA 픽셀이 일치하지 않습니다.')
        manifest={'schema_version':1,'width':SIZE,'height':SIZE,'fps':FPS,'period_seconds':int(PERIOD),
                  'frame_count':COUNT,'frame_pattern':'frame_{:04d}.png','archive':'frames.zip',
                  'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),**info}
        manifest['source']['glb']='atom3d.glb'
        manifest['source']['glb_sha256']=hashlib.sha256((output/'atom3d.glb').read_bytes()).hexdigest()
        manifest['source']['export_tool']='tools/atom3d_glb.py'
        manifest['source']['export_tool_sha256']=hashlib.sha256((ROOT/'tools/atom3d_glb.py').read_bytes()).hexdigest()
        (output/'frame_hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
        (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        report={'created_kst':datetime.now(timezone(timedelta(hours=9))).isoformat(),'command':[sys.executable,*sys.orig_argv[1:]],
                'cwd':str(Path.cwd()),'exit_code':0,'repair_used':38,'input_fix_used':25,'frames':COUNT,
                'elapsed_seconds':time.perf_counter()-start,'archive_bytes':archive.stat().st_size,
                'glb':glb_report,'all_frames_grayscale':True,'zero_alpha_rgb_zero':True,
                'loop_rgba_exact_match':loop_image_equal,'bounds':bounds,'runtime_dependencies':'Qt PNG 디코딩만; 제작 라이브러리 런타임 미사용'}
        (output/'creation_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        (output/'LICENSE.txt').write_text('이 자산의 메시·절차적 조명·셰이더·모션은 이 프로젝트를 위해 직접 생성했습니다.\n외부 모델·사진·HDRI·텍스처를 사용하지 않았습니다.\n생성 자산은 프로젝트 소유자 곽윤석님의 사용·수정·재배포 용도입니다.\nModernGL·glcontext·NumPy·Pillow는 제작 전용 의존성이며 앱 프레임 재생에는 포함할 필요가 없습니다.\n',encoding='utf-8')
        print(json.dumps({'output':str(output),'frames':COUNT,'archive_bytes':report['archive_bytes'],'loop_exact':loop_image_equal},ensure_ascii=False))
    finally:renderer.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--preview',action='store_true')
    modes.add_argument('--bake',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.preview:preview(args.output or ROOT/'work/atom3d-preview/v2-alpha')
    else:bake(args.output or ROOT/'assets/atom3d')


if __name__=='__main__':
    try:main()
    except Exception:
        failure={'kst':datetime.now(timezone(timedelta(hours=9))).isoformat(),'session':'SESSION_ID','task':'orbit-monochrome-motion','argv':[sys.executable,*getattr(sys,'orig_argv',[])[1:]],'cwd':str(Path.cwd()),'exit_code':1,'error':traceback.format_exc(),'repair_used':38,'input_fix_used':25,'changed':'제작 도구와자산; 앱 src/tests 변경 없음'}
        folder=ROOT/'work/atom3d-preview';folder.mkdir(parents=True,exist_ok=True)
        (folder/('failure-'+str(time.time_ns())+'.json')).write_text(json.dumps(failure,ensure_ascii=False,indent=2),encoding='utf-8')
        raise
