"""선택한 국가·지역의 검토된 행사 자료를 제한된 메모리로 조회합니다."""
from datetime import date
from functools import lru_cache
from pathlib import Path
import hashlib,json,re,sys,unicodedata

FIRST_YEAR=2026
LAST_YEAR=2099

def _root():
    return Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parents[1]))/'assets/holiday-calendar'

def _read(path,limit):
    if not path.is_file() or path.stat().st_size>limit:raise ValueError('국가 행사 자료가 없거나 크기 한도를 넘었습니다.')
    raw=path.read_bytes();return raw,json.loads(raw.decode('utf-8'))

@lru_cache(maxsize=1)
def _index():
    _,value=_read(_root()/'index.json',1024*1024)
    if value.get('schema_version')!=1 or value.get('first_year')!=2026 or value.get('last_year')!=2099:
        raise ValueError('행사 자료 형식 또는 지원 연도가 다릅니다.')
    rows=value.get('countries')
    if not isinstance(rows,list) or not 1<=len(rows)<=300:raise ValueError('국가 목록 형식')
    result={}
    for row in rows:
        cc=row.get('code')
        if not isinstance(cc,str) or not re.fullmatch('[A-Z]{2}',cc) or cc in result or row.get('file')!=cc+'.json':
            raise ValueError('국가 코드 또는 경로 형식')
        result[cc]=row
    return value,result

def normalize_country(value):
    if not isinstance(value,str):raise ValueError('국가 코드 형식')
    cc={'UK':'GB'}.get(value.strip().upper(),value.strip().upper())
    if not re.fullmatch('[A-Z]{2}',cc):raise ValueError('국가 코드 형식')
    return cc

def available_countries(language='ko'):
    if language not in ('ko','en'):raise ValueError('지원 언어')
    return [dict(code=cc,name=row['name_'+language],name_ko=row['name_ko'],name_en=row['name_en'])
            for cc,row in sorted(_index()[1].items(),key=lambda item:item[1]['name_'+language])]

def find_countries(query,language='ko'):
    if not isinstance(query,str) or len(query)>160:return []
    key=unicodedata.normalize('NFKC',query).strip().casefold()
    if not key:return available_countries(language)
    aliases={'KR':('한국','남한','South Korea','Republic of Korea'),'KP':('북한','North Korea'),'US':('USA','미합중국'),'GB':('UK','United Kingdom'),'TW':('대만','타이완'),'AE':('UAE',)}
    return [row for row in available_countries(language) if any(key in str(text).casefold() for text in
            [row[field] for field in ('code','name_ko','name_en')]+list(aliases.get(row['code'],())))]

@lru_cache(maxsize=6)
def _country(cc):
    metadata=_index()[1].get(cc)
    if metadata is None:return None
    raw,value=_read(_root()/metadata['file'],8*1024*1024)
    if len(raw)!=metadata['bytes'] or hashlib.sha256(raw).hexdigest()!=metadata['sha256']:
        raise ValueError('국가 행사 자료가 검증한 원문과 다릅니다.')
    if value.get('country_code')!=cc or value.get('schema_version')!=1:raise ValueError('국가 자료 식별자')
    return value

def country_status(country='KR',year=2026):
    cc=normalize_country(country);data=_country(cc)
    if type(year) is not int or not FIRST_YEAR<=year<=LAST_YEAR:raise ValueError('지원 연도는 2026~2099년입니다.')
    if data is None:return dict(country_code=cc,supported=False,status='unsupported',warnings=['이 국가·지역의 행사 자료가 없습니다.'])
    entry=data['years'][str(year)]
    return dict(country_code=cc,supported=True,status=entry['status'],warnings=list(entry['warnings']),
                source='holidays 0.108',future_rules_may_change=True,scope='국가 단위 공휴일·지원되는 기념일')

def _kind(text):
    key=text.casefold()
    for word,kind in (('christmas eve','christmas_eve'),('christmas','christmas'),('korean new year','lunar_new_year'),
                      ('chinese new year','lunar_new_year'),('lunar new year','lunar_new_year'),('chuseok','harvest'),
                      ('mid-autumn','harvest'),('thanksgiving','harvest'),('new year','new_year'),
                      ('valentine','valentine'),('children','children'),('hangul','hangul'),('hangeul','hangul'),
                      ('halloween','halloween'),('diwali','lights'),('deepavali','lights'),('hanukkah','lights'),
                      ('eid','crescent'),('ramadan','crescent'),('independence','national_day'),('national day','national_day')):
        if word in key:return kind
    return 'public_holiday'

def event_for_date(value,country='KR'):
    if type(value) is not date or not FIRST_YEAR<=value.year<=LAST_YEAR:raise ValueError('행사 날짜 범위')
    cc=normalize_country(country);data=_country(cc)
    if data is None:return None
    year=data['years'][str(value.year)];event=year['events'].get(value.isoformat())
    if event is None:return None
    names=event.get('names',[]);english=event.get('english_names',[])
    if not isinstance(names,list) or not names or any(not isinstance(x,str) for x in names):raise ValueError('행사명 형식')
    title=' · '.join(names)
    return dict(key=cc+':'+value.isoformat(),title=title,kind=_kind(' '.join(english+names)),country_code=cc,
                source='holidays 0.108',status=year['status'],categories=tuple(event['categories']),
                warnings=tuple(year['warnings']),country_name=_index()[1][cc]['name_ko'])
