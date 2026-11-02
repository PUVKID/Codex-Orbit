"""888개 연월 주제표와 27,028일의 명시적인 대상·형상 배정을 함께 저장합니다."""
from dataclasses import asdict
from pathlib import Path
import calendar
import csv
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from calendar_catalog import OBJECTS, ANCHORS, COMPANIONS, COMPOSITION_NAMES, all_collections
from calendar_art import all_designs


def generate():
    destination=ROOT/'assets/calendar-art'
    destination.mkdir(parents=True,exist_ok=True)
    months=[]
    for collection in all_collections():
        row=asdict(collection)
        year,month=map(int,collection.key.split('-'))
        days=calendar.monthrange(year,month)[1]
        row['subjects']=row['subjects'][:days]
        row['daily_subjects']=[{'day':day,'object_id':key,'name':OBJECTS[key].name,
                               'shape_recipe':OBJECTS[key].recipe} for day,key in enumerate(row['subjects'],1)]
        months.append(row)
    dates=[]
    for design in all_designs():
        row=asdict(design);row['date']=design.date.isoformat()
        dates.append(row)
    common={'schema_version':4,'geometry_rule_version':4,'first_date':'2026-01-01','last_date':'2099-12-31',
            'date_timezone':'Asia/Seoul (UTC+09:00)'}
    data={**common,'collection_count':888,'object_count':len(OBJECTS),'count':len(dates),
          'method':'37개 실제 주제 모티프와 24개 실제 동반 모티프의 역할 있는 조합. 날짜별 주연은 해당 분류의 실제 대상 31종입니다.',
          'collections':months,'designs':dates}
    (destination/'catalog.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    objects={**common,'objects':[asdict(value) for value in OBJECTS.values()],
             'anchors':[value.key for value in ANCHORS],'companions':[value.key for value in COMPANIONS],
             'reference_examples':['https://www.rhs.org.uk/plants/tulip',
                                   'https://www.rhs.org.uk/shows-events/pdf/horticultural-competitions/daffodil-schedule-2026.pdf',
                                   'https://www.kew.org/plants/roses'],
             'reference_scope':'위 자료는 대표 꽃의 주요 형태 확인에 사용했습니다. 모든 대상의 도감 검수나 정확한 실물 복제 인증을 뜻하지 않습니다.'}
    (destination/'objects.json').write_text(json.dumps(objects,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (destination/'themes.json').write_text(json.dumps({**common,'collections':months},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (destination/'themes.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.writer(stream)
        writer.writerow(('연월','월 주제','왼쪽 주제 대상','오른쪽 동반 대상','구성','날짜순 주연과 형상 규칙'))
        for row in months:
            writer.writerow((row['key'],row['title'],OBJECTS[row['anchor_id']].name,OBJECTS[row['companion_id']].name,
                             COMPOSITION_NAMES[row['composition']],' / '.join(f"{x['day']}일 {x['name']} [{x['shape_recipe']}]" for x in row['daily_subjects'])))
    lines=['# 2026~2099년 월별 조형 주제표','',
           '총 888개 연월 컬렉션과 27,028일을 지원합니다. 화면의 큰 이름은 그날의 실제 주연 대상이며 월 주제는 별도로 표시합니다.',
           '', '## 제작 방식과 범위','',
           '- 꽃·열매·잎·악기 각각 31종, 총 124종의 이름과 주요 구조를 편집한 사전을 사용합니다.',
           '- 37개 주제 대상과 24개 동반 대상의 서로 다른 888쌍을 조합합니다. 두 목록은 겹치지 않으므로 역순 쌍을 중복 계산하지 않습니다.',
           '- 주연은 중앙, 월 주제 대상은 왼쪽, 동반 대상은 오른쪽에 실제 메시로 나타납니다. 같은 대상이 다른 달에 다시 등장할 수 있습니다.',
           '- 매달 주제 대상의 분류에 속하는 주연이 날짜별로 바뀝니다. 28·29·30·31일의 실제 달력 길이를 따릅니다.',
           '- 공통 메시 생성 규칙을 재사용한 장식용 해석입니다. 888개 독립 수작업 모델이나 정밀 식물·악기 도감, 27,028개의 서로 다른 생물 종을 만들었다는 뜻은 아닙니다.',
           '- 월 구분은 숫자·색·seed에만 의존하지 않습니다. 실제로 그리는 주제·동반 대상의 조합이 다르며 그에 맞는 배치를 사용합니다.',
           '- 전체 날짜의 프레임 영상을 저장하지 않고 현재 날짜의 메시만 렌더합니다. 색조와 세 대상의 기울기·깊이도 날짜별로 결정됩니다.',
           '', '## 74년 × 12개월 요약','',
           '| 연도 | '+' | '.join(f'{month}월' for month in range(1,13))+' |',
           '|---|'+'---|'*12]
    for year in range(2026,2100):
        subset=months[(year-2026)*12:(year-2025)*12]
        lines.append('| '+str(year)+' | '+' | '.join(row['title'] for row in subset)+' |')
    lines+=['','## 888개 연월의 날짜별 대상','',
            '| 연월 | 월 주제 | 구성 | 날짜순 주연 대상 |','|---|---|---|---|']
    for row in months:
        names=' / '.join(f"{x['day']}일 {x['name']}" for x in row['daily_subjects'])
        lines.append(f"| {row['key']} | {row['title']} | {COMPOSITION_NAMES[row['composition']]} | {names} |")
    lines+=['','## 형태 자료와 검증 범위','',
            '대상별 이름·형상 규칙·특징은 objects.json, 모든 날짜의 실제 배정은 catalog.json, 날짜별 형상 규칙까지 포함한 표는 themes.csv에 있습니다.',
            '대표 꽃의 자료: [RHS 튤립](https://www.rhs.org.uk/plants/tulip), [RHS 수선화 형태](https://www.rhs.org.uk/shows-events/pdf/horticultural-competitions/daffodil-schedule-2026.pdf), [Kew 장미](https://www.kew.org/plants/roses). 모든 대상의 전문 도감 검수는 수행하지 않았습니다.','']
    (destination/'themes.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'collections':len(months),'dates':len(dates),'objects':len(OBJECTS),
                      'destination':str(destination),'first_36':[{'month':x['key'],'theme':x['title'],'first':x['daily_subjects'][0]['name']} for x in months[:36]]},ensure_ascii=False,indent=2))


if __name__=='__main__':generate()
