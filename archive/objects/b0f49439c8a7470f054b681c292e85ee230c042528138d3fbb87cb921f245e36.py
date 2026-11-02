"""제작 메시와 회전을 표준 glTF 2.0 바이너리로 내보냅니다."""
from __future__ import annotations
import json
import math
from pathlib import Path
import struct
import numpy as np


def quaternion(matrix):
    """행렬을 x,y,z,w 순서의 단위 쿼터니언으로 변환합니다."""
    m=matrix
    trace=float(np.trace(m))
    if trace>0:
        s=math.sqrt(trace+1.0)*2
        q=np.array([(m[2,1]-m[1,2])/s,(m[0,2]-m[2,0])/s,(m[1,0]-m[0,1])/s,.25*s])
    else:
        i=int(np.argmax(np.diag(m)));j=(i+1)%3;k=(i+2)%3
        s=math.sqrt(1+m[i,i]-m[j,j]-m[k,k])*2
        q=np.zeros(4);q[i]=.25*s;q[j]=(m[j,i]+m[i,j])/s;q[k]=(m[k,i]+m[i,k])/s;q[3]=(m[k,j]-m[j,k])/s
    return q/np.linalg.norm(q)


def export_glb(path,meshes,ring_rotation,electron_position,period,camera_z,extent):
    """단위·법선·중심 원점과 재사용 재질을 보존합니다. 조명은 별도 메타입니다."""
    binary=bytearray();views=[];accessors=[]
    def accessor(array,kind,component,target=None,bounds=False):
        array=np.ascontiguousarray(array)
        while len(binary)%4:binary.append(0)
        offset=len(binary);binary.extend(array.tobytes())
        view={'buffer':0,'byteOffset':offset,'byteLength':array.nbytes}
        if target is not None:view['target']=target
        views.append(view)
        item={'bufferView':len(views)-1,'componentType':component,'count':len(array),'type':kind}
        if bounds:
            item['min']=np.min(array,axis=0).reshape(-1).tolist()
            item['max']=np.max(array,axis=0).reshape(-1).tolist()
        accessors.append(item)
        return len(accessors)-1
    names=['궤도_안쪽','궤도_중간','궤도_바깥','흑연_원자핵','전자_공유메시']
    gl_meshes=[]
    for index,(vertices,indices) in enumerate(meshes):
        p=accessor((vertices[:,:3]*.01).astype('<f4'),'VEC3',5126,34962,True)
        n=accessor(vertices[:,3:].astype('<f4'),'VEC3',5126,34962)
        ix=accessor(indices.astype('<u4'),'SCALAR',5125,34963)
        gl_meshes.append({'name':names[index],'primitives':[{'attributes':{'POSITION':p,'NORMAL':n},'indices':ix,'material':1 if index==3 else 2 if index==4 else 0,'mode':4}]})
    nodes=[]
    for i in range(3):nodes.append({'name':names[i],'mesh':i,'rotation':quaternion(ring_rotation(i,0)).tolist()})
    nodes.append({'name':names[3],'mesh':3})
    for i in range(3):nodes.append({'name':f'전자_{i+1}','mesh':4,'translation':(electron_position(i,0)*.01).tolist()})
    nodes.append({'name':'제작_카메라','camera':0,'translation':[0,0,camera_z*.01]})
    times=np.linspace(0,period,181,dtype='<f4')
    time_accessor=accessor(times,'SCALAR',5126,bounds=True)
    samplers=[];channels=[]
    for i in range(3):
        samples=[]
        for t in times:
            q=quaternion(ring_rotation(i,float(t)))
            if samples and np.dot(q,samples[-1])<0:q=-q
            samples.append(q)
        output=accessor(np.asarray(samples,dtype='<f4'),'VEC4',5126)
        samplers.append({'input':time_accessor,'output':output,'interpolation':'LINEAR'})
        channels.append({'sampler':len(samplers)-1,'target':{'node':i,'path':'rotation'}})
    for i in range(3):
        samples=np.asarray([electron_position(i,float(t))*.01 for t in times],dtype='<f4')
        output=accessor(samples,'VEC3',5126)
        samplers.append({'input':time_accessor,'output':output,'interpolation':'LINEAR'})
        channels.append({'sampler':len(samplers)-1,'target':{'node':4+i,'path':'translation'}})
    document={'asset':{'version':'2.0','generator':'Codex Orbit 실제 3D 자산 제작 도구'},'scene':0,'scenes':[{'nodes':list(range(8))}],'nodes':nodes,'meshes':gl_meshes,'materials':[{'name':'무채색_크롬','pbrMetallicRoughness':{'baseColorFactor':[.72,.72,.72,1],'metallicFactor':1.,'roughnessFactor':.18}},{'name':'흑연','pbrMetallicRoughness':{'baseColorFactor':[.018,.018,.018,1],'metallicFactor':.3,'roughnessFactor':.39}},{'name':'전자_은색','pbrMetallicRoughness':{'baseColorFactor':[.62,.62,.62,1],'metallicFactor':.95,'roughnessFactor':.20}}],'animations':[{'name':'독립_궤도_18초','samplers':samplers,'channels':channels}],'cameras':[{'type':'perspective','perspective':{'yfov':2*math.atan(extent/camera_z),'aspectRatio':1.,'znear':.01,'zfar':12.}}],'buffers':[{'byteLength':len(binary)}],'bufferViews':views,'accessors':accessors,'extras':{'unit':'미터; 제작 단위 1 = 0.01미터','lighting':'PNG 제작의 절차적 스튜디오 환경은 별도 lighting 메타와 셰이더를 참조','collision':'UI 조형물로 물리 충돌 없음','lod':'작은 단일 장식물; 텍스처 없음; 별도 LOD 불필요'}}
    encoded=json.dumps(document,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    encoded+=b' '*((-len(encoded))%4)
    binary.extend(b'\0'*((-len(binary))%4))
    total=12+8+len(encoded)+8+len(binary)
    output=struct.pack('<4sII',b'glTF',2,total)+struct.pack('<I4s',len(encoded),b'JSON')+encoded+struct.pack('<I4s',len(binary),b'BIN\0')+binary
    Path(path).write_bytes(output)
    return {'bytes':len(output),'mesh_count':len(gl_meshes),'node_count':len(nodes),'material_count':3,'animation_samples':181}
