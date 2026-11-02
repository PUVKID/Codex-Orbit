"""23차 대상 카탈로그의 실제 GPU 이미지와 메시 검증 기록을 만듭니다."""
from datetime import date, datetime, timezone, timedelta
import hashlib
import io
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from calendar_art import design_for_date
from calendar_renderer import CalendarRenderer, np, matrices
from PySide6.QtCore import QBuffer, QIODevice
from PIL import Image, ImageDraw, ImageFont


def run():
    destination=ROOT/'evidence/달력3D23'
    destination.mkdir(parents=True,exist_ok=True)
    renderer=CalendarRenderer()
    font=ImageFont.truetype(str(ROOT/'assets/SUIT-SemiBold.ttf'),15)
    records=[];start=time.perf_counter()
    groups=(('2026-2028_36개월',[date(year,month,15) for year in range(2026,2029) for month in range(1,13)],6),
            ('2026-01_31일',[date(2026,1,day) for day in range(1,32)],7),
            ('2099_12개월',[date(2099,month,15) for month in range(1,13)],4),
            ('오늘과경계',[date(2026,10,28),date(2028,2,29),date(2099,12,31)],3))
    try:
        for name,dates,columns in groups:
            sheet=Image.new('RGB',(columns*200,((len(dates)+columns-1)//columns)*225),(15,25,38))
            for i,value in enumerate(dates):
                mark=time.perf_counter();image=renderer.render(value,0)
                buffer=QBuffer();buffer.open(QIODevice.OpenModeFlag.WriteOnly);image.save(buffer,'PNG')
                raw=Image.open(io.BytesIO(bytes(buffer.data()))).convert('RGBA');buffer.close()
                assert raw.getpixel((0,0))[3]==0
                image.save(str(destination/(value.isoformat()+'.png')))
                digest=hashlib.sha256();triangles=0
                for (vertices,indices),_,_,_ in renderer.parts[:-2]:
                    assert np.isfinite(vertices).all()
                    assert np.allclose(np.linalg.norm(vertices[:,3:],axis=1),1,atol=2e-5)
                    assert int(indices.max())<len(vertices)
                    digest.update(vertices[:,:3].tobytes());digest.update(indices.tobytes())
                    triangles+=len(indices)//3
                design=design_for_date(value)
                records.append({'date':str(value),'title':design.title,'theme':design.theme,'anchor_id':design.anchor_id,
                                'companion_id':design.companion_id,'accent':design.accent,'parts':len(renderer.parts),
                                'triangles':triangles,'geometry_sha256':digest.hexdigest(),'seconds':time.perf_counter()-mark})
                small=raw.convert('RGBa').resize((196,196),Image.Resampling.LANCZOS).convert('RGBA')
                bg=Image.new('RGBA',(196,196),(15,25,38,255));bg.alpha_composite(small)
                x=i%columns*200;y=i//columns*225
                sheet.paste(bg.convert('RGB'),(x+2,y))
                ImageDraw.Draw(sheet).text((x+5,y+198),f'{value:%y/%m/%d} {design.title}',font=font,fill=(230,239,244))
            sheet.save(destination/(name+'.jpg'),quality=94)
        jan=[r for r in records if r['date'].startswith('2026-01-')]
        assert len({r['geometry_sha256'] for r in jan})==31
        assert len({r['accent'] for r in jan})==31
        first=renderer.render(date(2026,10,28),0);loop=renderer.render(date(2026,10,28),12)
        assert hashlib.sha256(bytes(first.constBits())).digest()==hashlib.sha256(bytes(loop.constBits())).digest()
        for a,b in zip(matrices(0),matrices(12)):assert np.allclose(a,b)
        times=[]
        for i in range(20):
            mark=time.perf_counter();renderer.render(date(2026,10,28),i/30);times.append(time.perf_counter()-mark)
        report={'kst':datetime.now(timezone(timedelta(hours=9))).isoformat(),'renderer':renderer.ctx.info['GL_RENDERER'],
                'frames':len(records),'elapsed_seconds':time.perf_counter()-start,
                'same_date_render_mean_ms':sum(times)/len(times)*1000,'same_date_render_max_ms':max(times)*1000,
                'loop_exact':True,'records':records}
        (destination/'실측.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k!='records'},ensure_ascii=False))
    finally:renderer.close()


if __name__=='__main__':run()
