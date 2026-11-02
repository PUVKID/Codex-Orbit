"""사용자 자료에 기록하지 않는 14차 Qt 화면과 독립 회전 근거를 캡처합니다."""
from pathlib import Path
import json, math, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont,QFontDatabase,QImage,QPainter,QColor
from PySide6.QtTest import QTest
from app import Controller,Settings,asset
from theme import apply_theme
from visuals import ring_normal,ring_points,project_point,MOTION_PERIOD,RING_AXES,RING_TURNS
from generate_visual_assets import orbit_image,write_motion

def main():
    app=QApplication([]);apply_theme()
    fid=QFontDatabase.addApplicationFont(str(asset('NanumGothic-Bold.ttf')))
    app.setFont(QFont(QFontDatabase.applicationFontFamilies(fid)[0],10,QFont.Weight.Bold))
    out=ROOT/'work/kinetic/final-captures';out.mkdir(parents=True,exist_ok=True)
    folder=tempfile.TemporaryDirectory()
    controller=Controller(Settings(folder.name),start_worker=False,start_usage=False)
    event={'id':'kinetic-fixture','target':'kinetic-fixture','chat_name':'시각 검토용 채팅 · 독립 회전과 두 화면',
           'before':{'model':'gpt-6.1-sol','effort':'medium'},'after':{'model':'gpt-6-astra','effort':'high'},
           'reason':'시각 검토를 위한 제어 입력입니다. 정확한 값과 두 화면 구성을 확인합니다.',
           'time':'2026-10-25T15:00:00Z','kind':'settings'}
    controller.window.add_event(event);controller.show()
    for width,height in ((1120,780),(740,540)):
        controller.window.resize(width,height)
        for tab in range(2):
            controller.window.tabs.setCurrentIndex(tab);QTest.qWait(25)
            controller.window.grab().save(str(out/f'qt-{width}-{tab}.png'))
    controller.display_notice(event);QTest.qWait(200)
    controller.notice.grab().save(str(out/'notice.png'))
    controller.status({'state':'오류 · 재시도','error':'제어 입력 · 원문 오류 표시 확인','time':'now'})
    controller.window.tabs.setCurrentIndex(0);QTest.qWait(20)
    controller.window.grab().save(str(out/'diagnostics.png'))
    controller.close();folder.cleanup()
    measurements=[]
    for moment in (0,2,4,6,8,12,18):
        normals=[ring_normal(i,moment) for i in range(3)]
        pairs=[sum(a*b for a,b in zip(normals[i],normals[j])) for i,j in ((0,1),(0,2),(1,2))]
        angles=[]
        for i in range(3):
            points=[project_point(p) for p in ring_points(i,moment)]
            x=sum(p[0] for p in points)/len(points);y=sum(p[1] for p in points)/len(points)
            xx=sum((p[0]-x)**2 for p in points);yy=sum((p[1]-y)**2 for p in points)
            xy=sum((p[0]-x)*(p[1]-y) for p in points)
            angles.append(math.degrees(.5*math.atan2(2*xy,xx-yy)))
        measurements.append({'seconds':moment,'normals':normals,'pairwise_dot':pairs,'projected_major_axis_degrees':angles,
                             'relative_axis_degrees':[(angles[i]-angles[j])%180 for i,j in ((0,1),(0,2),(1,2))]})
    (out/'independent-rotation.json').write_text(json.dumps({'period_seconds':MOTION_PERIOD,'turns_per_period':RING_TURNS,
        'axes':RING_AXES,'measurements':measurements,'scope':'법선내적변화는공통강체회전불가의근거.투영상대각도함께기록.실제시간18초루프/속도왜곡없음'},ensure_ascii=False,indent=2),encoding='utf-8')
    for moment in (0,2,4,6):
        for size in (148,360):orbit_image(size,moment).save(str(out/f'orbit-{size}-{moment}.png'))
    for name,color in (('dark','#101010'),('light','#f5f5f5')):
        image=QImage(660,190,QImage.Format.Format_RGB32);image.fill(QColor(color));p=QPainter(image)
        for index,moment in enumerate((0,2,4,6)):p.drawImage(12+index*162,18,orbit_image(148,moment))
        p.end();image.save(str(out/f'orbit-board-{name}.png'))
    write_motion(out/'kinetic-motion.apng')
    print(str(out))
if __name__=='__main__':main()
