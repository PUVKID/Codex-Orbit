"""새 격리 폴더에서만 실행하는 고정 합성 화면 조작 검사입니다."""
from pathlib import Path
import json
import os
import sys
import time


def prepare_directory(value, argv):
    """기존 자료와 다른 검사 옵션에 접근하지 않도록 시작 경계를 검사합니다."""
    if not any(arg == '--data-dir' or arg.startswith('--data-dir=') for arg in argv):
        raise ValueError('--data-dir에 새 검사 전용 폴더를 명시해야 합니다.')
    if any(getattr(value, name, False) for name in ('sessions', 'smoke_test', 'usage_smoke_test', 'smoke_report', 'show_details', 'show_event')):
        raise ValueError('화면 검사에는 다른 시작 옵션을 함께 사용할 수 없습니다.')
    directory = Path(value.data_dir).absolute()
    if directory.exists() or directory.is_symlink():
        raise ValueError('기존 폴더는 화면 검사에 사용할 수 없습니다.')
    for parent in directory.parents:
        if parent.is_symlink() or (hasattr(parent, 'is_junction') and parent.is_junction()):
            raise ValueError('폴더 연결을 통한 화면 검사는 허용하지 않습니다.')
    directory.mkdir(parents=False, exist_ok=False)
    (directory / '합성검사전용.json').write_text('{"synthetic":true}\n', encoding='utf-8')
    return directory


def _run_ui_scenario(args, argv):
    """네트워크·감시·계정 조회 없이 실제 Qt 조작과 화면만 검사합니다."""
    try:
        directory = prepare_directory(args, argv)
    except (ValueError, OSError) as error:
        if sys.stderr:
            print(str(error), file=sys.stderr)
        return 1
    report = {'ok': False, 'synthetic': True, 'frozen': bool(getattr(sys, 'frozen', False)),
              'network_allowed': False, 'monitor_started': False, 'usage_started': False,
              'cases': [], 'error': ''}
    controller = None
    try:
        from unittest.mock import patch
        from PySide6.QtCore import Qt, QObject, Signal, QPoint
        from PySide6.QtWidgets import QApplication,QLabel
        from PySide6.QtTest import QTest
        from PySide6.QtGui import QFontInfo
        import app as product
        from calendar_motion import close_calendar_motion, calendar_motion_status, prepare_calendar_motion
        from typography import app_font
        sessions = directory / 'sessions'
        sessions.mkdir()
        codex = directory / 'synthetic-codex'
        codex.mkdir()
        os.environ['CODEX_HOME'] = str(codex)
        application = QApplication.instance() or QApplication(['Codex Orbit 합성 화면 검사'])
        application.setQuitOnLastWindowClosed(False)
        application.setFont(app_font())
        city = {'name': 'Synthetic City', 'admin1': 'Synthetic State', 'country': 'Synthetic Country',
                'country_code': 'KR', 'latitude': 37.2, 'longitude': 127.0, 'id': 123}

        class SyntheticSearch(QObject):
            results = Signal(list)
            failed = Signal(str)
            def __init__(self, parent=None, language='ko'):
                super().__init__(parent)
            def search(self, query):
                self.results.emit([dict(city)])
            def close(self):
                pass
            def set_language(self, value):
                pass
            def set_country(self, value):
                pass

        def blocked_network(*_args, **_kwargs):
            raise RuntimeError('합성 화면 검사에서 네트워크 접근이 차단되었습니다.')

        settings = product.Settings(directory)
        settings.values.update(sessions=str(sessions), codex_exe=str(codex / 'absent.exe'),
                               scene_mode='calendar', weather_location=None)
        settings.save()
        # 검색 결과는 합성 자료이며 검색 서비스의 실제 응답을 검증하지 않습니다.
        with patch.object(product, 'CitySearchClient', SyntheticSearch), patch.object(product, 'PlaceSearchClient', SyntheticSearch), \
             patch('socket.socket.connect', blocked_network), patch('socket.create_connection', blocked_network):
            report['calendar_preparation']=prepare_calendar_motion(timeout_seconds=5.0)
            assert report['calendar_preparation']['ready'], report['calendar_preparation']['error']
            controller = product.Controller(settings, start_worker=False, start_usage=False, start_weather=False)
            with patch.object(controller.weather, 'refresh', return_value=True) as synthetic_refresh, patch.object(controller.weather, '_request_weather', blocked_network), patch.object(controller.weather, '_lookup_region', blocked_network):
                controller.window.show()
                event = {'id': 'synthetic-ui32', 'target': 'synthetic-target', 'chat_name': '합성 화면 조작 검사',
                         'before': {'model': 'gpt-6.1-sol', 'effort': 'medium'},
                         'after': {'model': 'gpt-6.1-terra', 'effort': 'high'},
                         'reason': '선택 이유: 화면의 글자가 겹쳐 배치를 고칩니다. 같은 화면을 다시 확인합니다.'}
                controller.receive(event)
                controller.notice.timer.stop()
                for number, (theme, language, scale) in enumerate((('light','ko',100), ('dark','en',100), ('light','ko',150), ('dark','en',150))):
                    controller.orbit29.option('ui_theme', theme)
                    controller.set_language(language)
                    controller.orbit29.option('text_scale', scale)
                    controller.window.resize(800, 600)
                    from ui_appearance_smoke35 import check_appearance
                    appearance_checks=check_appearance(controller,directory,number)
                    rain, interval, stale = ((0.,900,False),(.4,900,False),(None,None,False),(2.,3600,True))[number]
                    humidity=(100.,99.99,55.55,None)[number]
                    remaining=(100.,99.99,0.,98.765)[number]
                    region=('합성 긴 도시 이름 · 가독성 확인을 위한 동쪽 지역' if language=='ko'
                            else 'Synthetic City with a Long District Name for Readability')
                    controller.usage.snapshot.update(rows=[{'remaining':remaining,'bucket':'synthetic','period':'주간','resets_at':None}],
                                                     checked_at=time.time(),stale=False,busy=False,status='조회 완료')
                    controller.update_usage(controller.usage.snapshot)
                    assert controller.orbit.usage_fraction==remaining/100
                    controller.weather.snapshot.update(temperature=22.5, humidity=humidity, precipitation=rain, precipitation_interval_seconds=interval, weather_code=0,
                        sunrise=79800, sunset=117000, utc_offset_seconds=32400, timezone='Asia/Seoul',
                        country_code='KR', region=region, location_mode='automatic', stale=stale)
                    controller.update_weather(controller.weather.snapshot)
                    forbidden_location_labels=('네트워크 추정','IP 추정','추정 지역','network estimate','IP estimate','estimated city')
                    assert controller.orbit.location_text==region
                    assert not any(label in controller.orbit.weather_tooltip for label in forbidden_location_labels)
                    QTest.qWait(150)
                    assert controller.orbit.grab().save(str(directory / f'{number}-widget.png'))
                    controller.orbit.resize(180,250)
                    QTest.qWait(100)
                    small_widget_size=list(controller.orbit.size().toTuple())
                    controller.orbit.grab()
                    visible_layout=controller.orbit._desktop_overlay_cache.layout
                    from PySide6.QtGui import QFontMetricsF
                    assert visible_layout['art'].width()>=96*scale/100
                    assert visible_layout['usage_label']==product.t('잔량 ')+controller.orbit.usage_badge
                    assert visible_layout['usage'].bottom()<=controller.orbit.height()
                    for field in ('clock_lines','primary_weather_lines','usage_lines'):
                        for line in visible_layout[field]:
                            assert QFontMetricsF(visible_layout['date_font']).horizontalAdvance(line)<=controller.orbit.width()-32+.1
                    assert visible_layout['art'].bottom()<visible_layout['dock'].top()
                    assert visible_layout['dock'].bottom()<visible_layout['location'].top()
                    assert visible_layout['weather'].bottom()<visible_layout['usage'].top()
                    assert visible_layout['date_font'].pixelSize()==round(14*scale/100)

                    assert controller.orbit.grab().save(str(directory / f'{number}-widget-small.png'))
                    controller.orbit.resize(220,432)
                    combo = controller.orbit29.text_size
                    before = combo.currentData()
                    QTest.mouseMove(combo, combo.rect().center())
                    combo.setFocus()
                    QTest.keyClick(combo, Qt.Key.Key_Tab)
                    combo.setFocus()
                    controller.window.raise_()
                    controller.window.activateWindow()
                    QTest.qWait(50)
                    arrow_point = QPoint(combo.width()-16,combo.height()//2)
                    QTest.mouseMove(combo, arrow_point)
                    QTest.qWait(30)
                    QTest.mousePress(combo, Qt.MouseButton.LeftButton, pos=arrow_point)
                    application.processEvents()
                    QTest.qWait(30)
                    QTest.mouseRelease(combo, Qt.MouseButton.LeftButton, pos=arrow_point)
                    started_popup = time.monotonic()
                    # Windows의 콤보 펼침 애니메이션을 실제 표시 조건으로 기다립니다.
                    while not combo.view().isVisible() and time.monotonic()-started_popup < .75:
                        QTest.qWait(10)
                    assert combo.view().isVisible(), '콤보 팝업이 열리지 않았습니다.'
                    popup_ready_ms=round((time.monotonic()-started_popup)*1000)
                    assert combo.view().window().grab().save(str(directory / f'{number}-popup.png'))
                    QTest.keyClick(combo.view(), Qt.Key.Key_Return)
                    assert not combo.view().isVisible()
                    assert combo.currentData() == before
                    QTest.keyClick(combo, Qt.Key.Key_Down, Qt.KeyboardModifier.AltModifier)
                    keyboard_started=time.monotonic()
                    while not combo.view().isVisible() and time.monotonic()-keyboard_started<.75:
                        QTest.qWait(10)
                    assert combo.view().isVisible(), '키보드로 콤보가 열리지 않았습니다.'
                    QTest.keyClick(combo.view(), Qt.Key.Key_Escape)
                    assert not combo.view().isVisible()
                    combo.setEnabled(False)
                    QTest.keyClick(combo, Qt.Key.Key_Home)
                    assert combo.currentData() == before
                    combo.setEnabled(True)
                    notice = controller.notice
                    QTest.mouseClick(notice.reason_disclosure, Qt.MouseButton.LeftButton)
                    assert notice.reason_original.isVisible()
                    assert event['reason'] in notice.reason_original.toPlainText()
                    QTest.mouseClick(notice.reason_disclosure, Qt.MouseButton.LeftButton)
                    controller.show_weather_location()
                    dialog = controller.location_dialog
                    assert dialog.mode_selector.currentData() == 'automatic'
                    assert [dialog.mode_selector.itemText(i) for i in range(2)]==[product.t('자동'),product.t('수동')]
                    assert not any(label in widget.text() or label in widget.toolTip()
                                   for widget in dialog.findChildren(QLabel) for label in forbidden_location_labels)
                    assert dialog.grab().save(str(directory / f'{number}-region-auto.png'))
                    dialog.mode_selector.setFocus()
                    QTest.keyClick(dialog.mode_selector, Qt.Key.Key_End)
                    application.processEvents()
                    assert dialog.mode_selector.currentData() == 'manual'
                    assert controller.settings.values['weather_location'] is None
                    QTest.keyClick(dialog.mode_selector, Qt.Key.Key_Home)
                    application.processEvents()
                    assert controller.settings.values['weather_location'] is None
                    assert controller.settings.values['theme_country_mode'] == 'auto'
                    assert synthetic_refresh.called
                    controller.show_weather_location()
                    dialog = controller.location_dialog
                    dialog.mode_selector.setFocus()
                    QTest.keyClick(dialog.mode_selector, Qt.Key.Key_End)
                    application.processEvents()
                    assert dialog.mode_selector.currentData() == 'manual'
                    dialog.search_kind.setCurrentIndex(dialog.search_kind.findData('place'))
                    QTest.keyClicks(dialog.query, 'Synthetic Place')
                    QTest.mouseClick(dialog.search_button, Qt.MouseButton.LeftButton)
                    assert dialog.cities.count() == 1
                    assert not dialog.apply_button.isEnabled(), '검색 첫 결과를 자동 선택하면 안 됩니다.'
                    dialog.cities.setFocus()
                    QTest.keyClick(dialog.cities, Qt.Key.Key_Down)
                    assert dialog.apply_button.isEnabled()
                    assert dialog.grab().save(str(directory / f'{number}-region.png'))
                    # 목록 화면만 합성 자료로 검사하며 실제 도시 수록 범위를 가장하지 않습니다.
                    synthetic_ref = {'provider':'geonames','geonames_id':123,'country_code':'KR',
                                     'confidence':'estimated','provenance':'synthetic UI fixture'}
                    synthetic_coverage = {'catalog_items_count':3,'series_count':1,'edition_count':1,
                                          'unclassified_count':1,'announced_occurrences_count':1,
                                          'announced_dates_count':2,'coverage_status':'partial'}
                    synthetic_event = {'id':'synthetic-announced','title':'합성 음악 행사 · 긴 한글 이름과 발표 날짜의 읽기 확인',
                                       'title_en':'Synthetic music event with a long title for readability checks','kind':'music','status':'announced',
                                       'date_precision':'day','date_evidence':'official_page_crosschecked','time_conflict':True,
                                       'dates':['2027-06-10','2027-06-11'],'license':'CC0-1.0',
                                       'source_url':'https://example.org/synthetic-event'}
                    synthetic_catalog = [dict(synthetic_event,id='synthetic-'+role,dates=[],item_role=role,
                                              display_title='Synthetic '+role) for role in ('series','edition','unclassified')]
                    with patch('city_festivals.city_coverage',return_value=synthetic_coverage), \
                         patch('city_festivals.series_for_city',return_value=synthetic_catalog), \
                         patch('city_festivals.announced_events_for_year',return_value=[synthetic_event]):
                        dialog.city_ref=synthetic_ref
                        QTest.mouseMove(dialog.city_button,dialog.city_button.rect().center())
                        dialog.city_button.setFocus()
                        QTest.mouseClick(dialog.city_button,Qt.MouseButton.LeftButton)
                        application.processEvents()
                        city_dialog=dialog.city_dialog
                        city_dialog.year.setCurrentIndex(city_dialog.year.findData(2027))
                        assert city_dialog.isVisible() and city_dialog.rows.count()==4
                        assert '2027-06-11' in city_dialog.details.toPlainText()
                        assert 'CC0-1.0' in city_dialog.details.toPlainText()
                        assert product.t('공식 페이지에서 날짜 확인 · 시간은 미확인') in city_dialog.details.toPlainText()
                        city_dialog.rows.setFocus()
                        QTest.keyClick(city_dialog.rows,Qt.Key.Key_End)
                        assert city_dialog.rows.currentRow()==3
                        assert product.t('행사 목록입니다. 개별 발표 일정은 위에서 확인합니다.') in city_dialog.details.toPlainText()
                        QTest.keyClick(city_dialog.rows,Qt.Key.Key_Home)
                        QTest.mouseMove(city_dialog.refresh_button,city_dialog.refresh_button.rect().center())
                        city_dialog.refresh_button.setFocus()
                        with patch.object(controller.city_updater,'refresh',return_value=True) as synthetic_update:
                            QTest.keyClick(city_dialog.refresh_button,Qt.Key.Key_Space)
                            assert synthetic_update.call_count==1
                        assert city_dialog.rows.horizontalScrollBar().maximum()==0
                        assert city_dialog.details.horizontalScrollBar().maximum()==0
                        assert city_dialog.grab().save(str(directory / f'{number}-city-events.png'))
                        QTest.keyClick(city_dialog,Qt.Key.Key_Escape)
                        application.processEvents()
                    QTest.keyClick(dialog, Qt.Key.Key_Escape)
                    application.processEvents()
                    from shiboken6 import isValid
                    assert not isValid(dialog) or not dialog.isVisible()
                    controller.orbit29.option('broadcast_mode', True)
                    assert event['chat_name'] not in notice.title.text()
                    controller.orbit29.option('broadcast_mode', False)
                    assert controller.window.grab().save(str(directory / f'{number}-window.png'))
                    assert notice.grab().save(str(directory / f'{number}-notice.png'))
                    notice.model_current.ensurePolished()
                    pixels = QFontInfo(notice.model_current.font()).pixelSize()
                    assert pixels == round(16 * scale / 100), (pixels, scale)
                    report['cases'].append({'theme': theme, 'language': language, 'scale': scale, 'appearance':appearance_checks,
                                            'size': list(controller.window.size().toTuple()), 'notice_model_pixels': pixels,
                                            'hover': True, 'keyboard': True, 'popup': True, 'popup_ready_ms':popup_ready_ms, 'disabled': True,
                                            'region_results': 'synthetic', 'privacy': True,
                                            'rain':rain,'interval_seconds':interval,'stale':stale,
                                            'humidity':humidity,'remaining':remaining,'usage_badge':controller.orbit.usage_badge,
                                            'region':region,'small_widget_size':small_widget_size,'usage_drawn':visible_layout['usage_label'],'minimum_art_pixels':visible_layout['art'].width(),
                                            'weather_extras':list(controller.orbit.weather_extras),
                                            'automatic_manual_keyboard':True,'city_catalog_synthetic':True,
                                            'city_catalog_roles':['series','edition','unclassified'],
                                            'city_hover_focus_keyboard':True,'city_update_synthetic':True,
                                            'city_time_warning':True,'city_missing_dates_accessible':True,
                                            'plain_location_labels':True})
        report['ok'] = True
    except Exception as error:
        report['error'] = f'{type(error).__name__}: {error}'
    finally:
        try:
            if controller is not None:
                controller.close()
            from calendar_motion import close_calendar_motion, calendar_motion_status
            close_calendar_motion()
            report['cleanup'] = calendar_motion_status()
            import calendar_motion
            report['cleanup_service_none']=calendar_motion._service is None
            report['cleanup_retiring_none']=calendar_motion._retiring is None
            if report['cleanup'].get('running') or not report['cleanup_service_none'] or not report['cleanup_retiring_none']:
                report['ok'] = False
                report['cleanup_error'] = '화면'+' 검사 작업자가 종료되지 않았습니다.'
        except Exception as error:
            report['ok'] = False
            report['cleanup_error'] = str(error)
        (directory / '화면검사.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return 0 if report['ok'] else 1


def run_ui_smoke(args, argv):
    """실제 앱 이벤트 루프 안에서만 조작 시나리오를 실행합니다."""
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    application = QApplication.instance() or QApplication(['Codex Orbit 합성 화면 검사'])
    application.setQuitOnLastWindowClosed(False)
    result = {'code': 1}
    def execute():
        result['code'] = _run_ui_scenario(args, argv)
        application.exit(result['code'])
    QTimer.singleShot(0, execute)
    application.exec()
    return result['code']
