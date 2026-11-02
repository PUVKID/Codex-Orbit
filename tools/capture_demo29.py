"""합성 데이터임을 표시한 실제 Qt 화면을 캡처합니다."""
import os,sys,time,json
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from PySide6.QtWidgets import QApplication,QLabel
from PySide6.QtCore import QTimer,Qt
from PySide6.QtTest import QTest
from app import Controller,Settings
from typography import app_font
from calendar_motion import calendar_motion_status,close_calendar_motion
app=QApplication([]);app.setFont(app_font());app.setQuitOnLastWindowClosed(False)
data=ROOT/'work/화면29';data.mkdir(exist_ok=True)
settings=Settings(data);settings.values.update(language='ko',broadcast_mode=False,scene_mode='observatory',motion_paused=False,text_scale=100);settings.save()
c=Controller(settings,start_worker=False,start_usage=False)
for i,(title,model,effort) in enumerate([('문서 화면 다듬기','gpt-6.1-sol','medium'),('관측소 입체감 검토','gpt-6-astra','high'),('배포 파일 검증','gpt-6.1-terra','high')]):
 event={'id':'capture-'+str(i),'target':'fixture-chat-'+str(i),'chat_name':title,'time':'2026-11-02T02:0'+str(i)+':00+00:00','kind':'observed','before':{'model':'gpt-6.1-sol','effort':'medium'},'after':{'model':model,'effort':effort},'reason':'이전 화면에서 글자가 겹쳐 보여, 배치와 글자 크기를 점검하도록 맡겼습니다.','task_summary':'합성 시연 · 글자 겹침과 이전/현재 값의 가독성을 검토합니다.'}
 c.receive(event)
 c.receive_lifecycle({**event,'id':'life-'+str(i),'kind':'lifecycle','status':['completed','running','waiting'][i]})
c.update_usage({'status':'합성 화면 예시 · 실제 계정 수치가 아닙니다.','rows':[{'remaining':72,'bucket':'codex','period':'주간','resets_at':None}],'checked_at':'2026-11-02T02:03:00+00:00','stale':False})
c.orbit29.panel.heading.setToolTip('합성 데이터로 캡처한 실제 Qt 화면입니다.')
c.window.resize(1320,1020);c.show('capture-1')
report={'fixture':True,'click_verified':False}
def capture():
 status=calendar_motion_status()
 if status.get('render_count',0)<2 and time.monotonic()-started<8:QTimer.singleShot(200,capture);return
 # 실제 위젯에 클릭 이벤트를 보내 상세창이 열리는 경로를 확인합니다.
 c.window.hide();QTest.mouseClick(c.orbit,Qt.MouseButton.LeftButton,pos=c.orbit.rect().center());app.processEvents()
 report['click_verified']=c.window.isVisible();c.show('capture-1');app.processEvents()
 out=ROOT/'evidence';out.mkdir(parents=True,exist_ok=True);c.window.grab().save(str(out/'29차_실제Qt_기록_합성.png'))
 c.orbit.grab().save(str(out/'29차_투명위젯_합성.png'))
 if c.notice:c.notice.grab().save(str(out/'29차_알림_합성.png'))
 c.orbit29.stack.setCurrentIndex(0);app.processEvents()
 deadline=time.monotonic()+3
 while time.monotonic()<deadline:
  app.processEvents();status=calendar_motion_status()
  if (status.get('delivery_dimensions') or [0])[0]>=min(c.orbit29.panel.canvas.width(),c.orbit29.panel.canvas.height()):break
  QTest.qWait(30)
 c.window.grab().save(str(out/'29차_실제Qt_관측소_합성.png'))
 c.orbit29.open_page(1);app.processEvents();c.window.grab().save(str(out/'29차_실제Qt_사용한도_합성.png'))
 c.set_language('en');app.processEvents();c.window.grab().save(str(out/'29차_실제Qt_영어_합성.png'))
 c.orbit29.option('broadcast_mode',True);app.processEvents();c.window.grab().save(str(out/'29차_실제Qt_방송_합성.png'))
 report.update(render=status,window_size=c.window.size().toTuple(),previous_model=c.window.model_previous.text(),current_model=c.window.model_current.text(),previous_effort=c.window.effort_previous.text(),current_effort=c.window.effort_current.text())
 (out/'29차_화면캡처_합성.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 c.close();app.quit()
started=time.monotonic();QTimer.singleShot(400,capture);app.exec();close_calendar_motion();print(json.dumps(report,ensure_ascii=False))
