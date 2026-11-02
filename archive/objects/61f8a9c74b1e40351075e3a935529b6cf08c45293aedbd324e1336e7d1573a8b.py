"""유효 날짜 카탈로그와 월별·1월 매일의 실제 GPU 검토 시트를 만듭니다."""
import argparse
from dataclasses import asdict
from datetime import date, datetime, timezone, timedelta
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT.parent/'17차/work/render-deps')]
from calendar_art import all_designs, design_for_date
from calendar_renderer import CalendarRenderer, matrices, np
from PIL import Image, ImageDraw, ImageFont
from PySide6.QtCore import QBuffer, QIODevice


def pil_image(image):
    buffer=QBuffer(); buffer.open(QIODevice.OpenModeFlag.WriteOnly); image.save(buffer,'PNG')
    result=Image.open(io.BytesIO(bytes(buffer.data()))).convert('RGBA'); buffer.close(); return result


def catalog(folder):
    # 23차 단일 생성기를 통해 최신 연월·대상 스키마를 보존합니다.
    from generate_calendar_catalog import generate
    generate()
    source=ROOT/'assets/calendar-art/catalog.json'
    content=source.read_bytes()
    (folder/'2026-2099_날짜카탈로그.json').write_bytes(content)
    return json.loads(content)['count']


def previews(folder):
    renderer=CalendarRenderer(); records=[]; start=time.perf_counter()
    font=ImageFont.truetype(str(ROOT/'assets/SUIT-SemiBold.ttf'),17)
    try:
        groups=(('12개월',[date(2026,m,15) for m in range(1,13)],4),('1월31일',[date(2026,1,d) for d in range(1,32)],7),
                ('경계날짜',[date(2028,2,29),date(2099,12,31)],2))
        for group,dates,columns in groups:
            sheet=Image.new('RGB',(columns*220,((len(dates)+columns-1)//columns)*246),(15,22,38))
            for index,value in enumerate(dates):
                t=time.perf_counter(); image=renderer.render(value,0); raw=pil_image(image)
                assert raw.getpixel((0,0))[3]==0
                name=value.isoformat()+'.png'; image.save(str(folder/name))
                digest=hashlib.sha256()
                for (v,ix),_,_,_ in renderer.parts[:-2]:
                    assert np.isfinite(v).all() and int(ix.max())<len(v)
                    assert np.abs(np.linalg.norm(v[:,3:],axis=1)-1).max()<1e-5
                    digest.update(v.tobytes()); digest.update(ix.tobytes())
                records.append({'date':value.isoformat(),'title':design_for_date(value).title,'parts':len(renderer.parts),
                                'geometry_sha256':digest.hexdigest(),'seconds':time.perf_counter()-t,'bbox':raw.getbbox()})
                small=raw.convert('RGBa').resize((216,216),Image.Resampling.LANCZOS).convert('RGBA')
                x=index%columns*220; y=index//columns*246; background=Image.new('RGBA',(216,216),(15,22,38,255)); background.alpha_composite(small)
                sheet.paste(background.convert('RGB'),(x+2,y)); ImageDraw.Draw(sheet).text((x+8,y+219),f'{value.month:02d}/{value.day:02d}  {design_for_date(value).title}',font=font,fill=(228,234,246))
            sheet.save(folder/(group+'_접촉시트.jpg'),quality=95)
        january=[r for r in records if r['date'].startswith('2026-01-')]
        assert len({r['geometry_sha256'] for r in january})==31
        for first,second in ((date(2027,8,29),date(2036,8,29)),(date(2055,3,24),date(2068,3,24))):
            hashes=[]
            for value in (first,second):
                renderer.set_date(value); digest=hashlib.sha256()
                for (v,ix),_,_,_ in renderer.parts[:-2]:digest.update(v.tobytes()); digest.update(ix.tobytes())
                hashes.append(digest.hexdigest())
            assert hashes[0]!=hashes[1], '기존 충돌 날짜의 실제 메시가 같습니다.'
            records.append({'year_pair':[first.isoformat(),second.isoformat()],'geometry_hashes':hashes})
        timings=[]
        for index in range(60):
            t=time.perf_counter(); renderer.render(date(2026,1,15),index/30); timings.append(time.perf_counter()-t)
        epsilon=.0001
        loop_position=max(float(np.max(np.abs(a-b))) for a,b in zip(matrices(0),matrices(12)))
        loop_velocity=max(float(np.max(np.abs((a-b)/(2*epsilon)-(c-d)/(2*epsilon)))) for a,b,c,d in zip(matrices(epsilon),matrices(-epsilon),matrices(12+epsilon),matrices(12-epsilon)))
        report={'renderer':renderer.ctx.info['GL_RENDERER'],'opengl':renderer.ctx.info['GL_VERSION'],'frames':records,
                'seconds':time.perf_counter()-start,'steady_render_ms_mean':sum(timings[1:])/59*1000,'steady_render_ms_max':max(timings[1:])*1000,
                'loop_matrix_max_error':loop_position,'loop_velocity_max_error':loop_velocity,'catalog_video_count':0,
                'external_meshes':False,'external_hdri':False,'runtime':'현재날짜1모델/1GPU컨텍스트/384RGBA'}
        (folder/'렌더_결과.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k!='frames'},ensure_ascii=False))
    finally:renderer.close()


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,required=True); args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    print(json.dumps({'catalog':catalog(args.output)}),flush=True); previews(args.output)


if __name__=='__main__':
    try:main()
    except Exception:
        state=json.loads((ROOT/'.codex/routing-state/df07fc65fbd813b9b2f33268.json').read_text(encoding='utf-8'))
        folder=ROOT/'evidence/달력3D22'; folder.mkdir(parents=True,exist_ok=True)
        failure={'kst':datetime.now(timezone(timedelta(hours=9))).isoformat(),'session':state['session_id'],'task':state['task_id'],
                 'argv':sys.orig_argv,'cwd':str(Path.cwd()),'exit_code':1,'error':traceback.format_exc(),'changed':'새 달력3D 파일만',
                 'repair_used':state['repair_used'],'input_fix_used':state['input_fix_used']}
        (folder/f'failure-{time.time_ns()}.json').write_text(json.dumps(failure,ensure_ascii=False,indent=2),encoding='utf-8');raise
