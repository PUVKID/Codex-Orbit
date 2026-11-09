"""카탈로그 ID와 검토된 표면 타일을 연결하며 원본 이미지는 수정하지 않습니다."""
import hashlib
import json
from pathlib import Path
from calendar_catalog import POOLS

CATEGORIES=('열매','잎','꽃')
TILE_ORDER={category:tuple(item.key for item in POOLS[category]) for category in CATEGORIES}


def tile_rectangle(width,height,index):
    if type(width) is not int or type(height) is not int or width<=0 or height<=0:
        raise ValueError('재질 지도 크기는 양의 정수여야 합니다.')
    if type(index) is not int or not 0<=index<31:
        raise ValueError('재질 번호는 검토된 31개 대상 안에 있어야 합니다.')
    col,row=index%8,index//8
    x0,x1=round(col*width/8),round((col+1)*width/8)
    y0,y1=round(row*height/4),round((row+1)*height/4)
    w,h=x1-x0,y1-y0
    if min(w,h)<128 or abs(w-h)>1:raise ValueError('재질 타일은 약 128픽셀 이상의 정사각형이어야 합니다.')
    return x0,y0,w,h


def load_catalog(material_root):
    root=Path(material_root)
    document=json.loads((root/'종별재질_매핑.json').read_text(encoding='utf-8'))
    if document.get('schema_version')!=1:raise ValueError('지원하지 않는 재질 매핑 형식입니다.')
    result={}
    for category in CATEGORIES:
        item=document['atlases'][category]
        if item['object_ids']!=list(TILE_ORDER[category]):raise ValueError('재질 순서가 원본 카탈로그와 다릅니다.')
        path=root/item['file']
        if path.parent.resolve()!=root.resolve():raise ValueError('재질 파일은 지정 폴더 안에 있어야 합니다.')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('재질 원본 해시가 다릅니다.')
        if item.get('reviewed') is not True:raise ValueError('직접 검토되지 않은 재질 지도입니다.')
        for index,key in enumerate(TILE_ORDER[category]):
            result[key]={'path':path,'index':index,'category':category,'projection':'triplanar' if category=='열매' else 'planar',
                         'enabled':key not in item.get('excluded',{}),'exclusion_reason':item.get('excluded',{}).get(key,'')}
    checked=set()
    for key,item in document.get('overrides',{}).items():
        if key not in result or result[key]['category']!='열매' or item['index']!=TILE_ORDER['열매'].index(key):
            raise ValueError('보강 재질의 대상과 타일 순서가 다릅니다.')
        path=root/item['file']
        if path.parent.resolve()!=root.resolve() or item.get('reviewed') is not True:
            raise ValueError('검토되지 않은 보강 재질입니다.')
        identity=(path,item['sha256'])
        if identity not in checked:
            if hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('보강 재질 원본 해시가 다릅니다.')
            checked.add(identity)
        result[key].update(path=path,index=item['index'],enabled=True,exclusion_reason='')
    return result


def extract_tile(image,index):
    """QImage 메모리에서만 자르며 생성 원본 파일을 덮어쓰지 않습니다."""
    if image.isNull():raise ValueError('재질 지도를 읽을 수 없습니다.')
    return image.copy(*tile_rectangle(image.width(),image.height(),index))
