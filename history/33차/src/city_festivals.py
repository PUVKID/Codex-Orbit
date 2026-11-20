"""검증된 도시 신원과 발표된 개최일만 날짜별 행사에 연결합니다."""
from copy import deepcopy
from datetime import date
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import sys
import zlib

FIRST_YEAR = 2026
LAST_YEAR = 2099
FILE_LIMIT = 8 * 1024 * 1024
KINDS = frozenset(('music', 'film', 'snow', 'lights', 'carnival', 'flowers', 'culture', 'balloon'))
_LICENSES = {'catalog': 'CC0-1.0', 'announced': 'factual-schedule', 'odbl': 'ODbL-1.0'}
_cache_directory = None
_cache_errors = {}
_revision = None


def _root():
    return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1])) / 'assets/city-festivals'


def normalize_country(value):
    if not isinstance(value, str): raise ValueError('국가 코드 형식')
    code = value.strip().upper()
    code = {'UK': 'GB'}.get(code, code)
    if not re.fullmatch('[A-Z]{2}', code): raise ValueError('국가 코드 형식')
    return code


def _text(value, limit=320):
    if not isinstance(value, str) or not value.strip() or len(value) > limit or any(not c.isprintable() for c in value):
        raise ValueError('행사 문자열 형식')
    return value.strip()


def _qid(value):
    return isinstance(value, str) and re.fullmatch('Q[1-9][0-9]{0,11}', value) is not None


def _read(path, limit=FILE_LIMIT):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
        raise ValueError('도시 행사 파일이 없거나 크기·경로 한도를 넘었습니다.')
    raw = path.read_bytes()
    if len(raw) > limit: raise ValueError('도시 행사 자료 크기')
    decoded = raw
    if path.name.endswith('.json.gz'):
        decoder = zlib.decompressobj(16+zlib.MAX_WBITS)
        decoded = decoder.decompress(raw, FILE_LIMIT+1)
        if len(decoded)>FILE_LIMIT or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
            raise ValueError('도시 행사 압축 자료의 해제 한도·스트림 형식')
    try: value = json.loads(decoded.decode('utf-8'))
    except (UnicodeError, json.JSONDecodeError) as exc: raise ValueError('도시 행사 JSON 형식') from exc
    if not isinstance(value, dict): raise ValueError('도시 행사 최상위 형식')
    return raw, value


def validate_index(value):
    """네트워크 자료도 같은 국가별 경로·크기·해시 계약을 따릅니다."""
    if not isinstance(value, dict) or type(value.get('schema_version')) is not int or value['schema_version'] != 1:
        raise ValueError('도시 행사 색인 버전')
    if value.get('first_year') != FIRST_YEAR or value.get('last_year') != LAST_YEAR:
        raise ValueError('도시 행사 지원 연도')
    if value.get('coverage_status') not in ('complete', 'partial'):
        raise ValueError('도시 행사 수집 상태')
    countries = value.get('countries')
    if not isinstance(countries, list) or len(countries) > 300: raise ValueError('국가 목록 형식')
    seen = set()
    for row in countries:
        if not isinstance(row, dict): raise ValueError('국가 메타 형식')
        cc = normalize_country(row.get('code'))
        if cc != row['code'] or cc in seen: raise ValueError('중복 국가 코드')
        seen.add(cc)
        files = row.get('files')
        if not isinstance(files, list) or not 1 <= len(files) <= 3: raise ValueError('국가별 자료 목록')
        used = set()
        for item in files:
            if not isinstance(item, dict): raise ValueError('자료 메타 형식')
            path = item.get('path', '')
            match = re.fullmatch(r'(catalog|announced|odbl)/([A-Z]{2})\.json(?:\.gz)?', path) if isinstance(path, str) else None
            if not match or match[2] != cc or path in used: raise ValueError('국가 자료 경로')
            used.add(path)
            if type(item.get('bytes')) is not int or not 0 < item['bytes'] <= FILE_LIMIT: raise ValueError('자료 크기 메타')
            if not isinstance(item.get('sha256'), str) or not re.fullmatch('[0-9a-f]{64}', item['sha256']): raise ValueError('자료 해시 메타')
            if item.get('license') != _LICENSES[match[1]]: raise ValueError('자료 라이선스 분류')
    return value


def validate_country_file(value, cc, category):
    """동봉·다운로드 자료의 도시 귀속·날짜 정밀도와 출처를 검사합니다."""
    if category not in _LICENSES or not isinstance(value, dict): raise ValueError('행사 자료 분류')
    if type(value.get('schema_version')) is not int or value['schema_version'] != 1 or value.get('country_code') != cc:
        raise ValueError('국가 자료 식별자')
    if value.get('license') != _LICENSES[category]: raise ValueError('국가 자료 라이선스')
    key = 'series' if category == 'catalog' else 'occurrences'
    rows = value.get(key)
    if not isinstance(rows, list) or len(rows) > 100000: raise ValueError('도시 행사 목록 개수')
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or row.get('country_code') != cc: raise ValueError('행사 국가 불일치')
        ident = _text(row.get('id'), 200)
        if ident in seen: raise ValueError('행사 식별자 중복')
        seen.add(ident)
        _text(row.get('title')); _text(row.get('title_en'))
        if row.get('kind') not in KINDS or row.get('license') != _LICENSES[category]: raise ValueError('행사 분류·라이선스')
        source = _text(row.get('source_url'), 1200)
        if not source.startswith('https://') or any(c in source for c in ('\r', '\n', '\\')): raise ValueError('행사 출처 URL')
        refs = row.get('city_refs')
        if not isinstance(refs, list) or len(refs) > 100: raise ValueError('행사 도시 목록')
        for ref in refs:
            if not isinstance(ref, dict) or not _qid(ref.get('wikidata_qid')): raise ValueError('도시 식별자')
            gid = ref.get('geonames_id')
            if gid is not None and (type(gid) is not int or not 0 < gid < 10**12): raise ValueError('도시 GeoNames 식별자')
        if category == 'catalog':
            if row.get('status') not in ('catalog_only', 'discontinued'): raise ValueError('시리즈 상태')
        else:
            if row.get('date_precision') != 'day' or row.get('status') not in ('announced', 'cancelled', 'postponed'):
                raise ValueError('발표 일정 정밀도·상태')
            if not refs or row.get('location_confidence') != 'city_verified': raise ValueError('일정 도시 귀속 미검증')
            days = row.get('dates')
            if not isinstance(days, list) or not 1 <= len(days) <= 3660 or len(set(days)) != len(days): raise ValueError('일정 날짜 집합')
            for day in days:
                if not isinstance(day, str): raise ValueError('일정 날짜 형식')
                try: actual = date.fromisoformat(day)
                except ValueError as exc: raise ValueError('일정 날짜 형식') from exc
                if actual.isoformat() != day or not FIRST_YEAR <= actual.year <= LAST_YEAR: raise ValueError('일정 날짜 범위')
            if type(row.get('time_conflict')) is not bool: raise ValueError('시각 충돌 표식')
            _text(row.get('checked_at'), 80)
    return value


@lru_cache(maxsize=1)
def _index():
    return validate_index(_read(_root()/'index.json', 1024*1024)[1])


@lru_cache(maxsize=6)
def _country(cc):
    cached = _cached_country(cc)
    if cached is not None: return cached
    return _load_country(_root(), _index(), cc)


def _load_country(root, index, cc):
    meta = next((r for r in index['countries'] if r['code'] == cc), None)
    result = {'series': [], 'occurrences': [], 'source_checked_at':index.get('generated_at'),
              'coverage_status':index['coverage_status']}
    if meta is None:return result
    for item in meta['files']:
        raw, value = _read(root/item['path'])
        if len(raw) != item['bytes'] or hashlib.sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('도시 행사 자료의 크기·해시가 색인과 다릅니다.')
        category = item['path'].split('/')[0]
        validate_country_file(value, cc, category)
        key = 'series' if category == 'catalog' else 'occurrences'
        result[key].extend(value[key])
    return result


def clear_cache():
    """검증된 자료 갱신 뒤 이전 국가 자료 캐시를 비웁니다."""
    global _revision
    _index.cache_clear(); _country.cache_clear(); _revision = None


def configure_city_cache(data_dir):
    """호출 앱의 데이터 폴더 안에서만 읽기 전용 캐시 선택을 준비합니다."""
    global _cache_directory
    _cache_directory = Path(data_dir).resolve()/'city-festivals' if data_dir is not None else None
    _cache_errors.clear(); clear_cache()


def _cached_country(cc):
    if _cache_directory is None: return None
    pointer = _cache_directory/'active'/(cc+'.json')
    if not pointer.is_file(): return None
    try:
        _, value = _read(pointer, 4096)
        generation = value.get('generation')
        if not isinstance(generation,str) or not re.fullmatch('[0-9a-f]{64}',generation): raise ValueError('캐시 세대 식별자')
        root = _cache_directory/'generations'/generation
        if root.is_symlink() or not root.resolve().is_relative_to(_cache_directory.resolve()): raise ValueError('캐시 경로 범위')
        raw, index = _read(root/'index.json',1024*1024)
        if hashlib.sha256(raw).hexdigest()!=value.get('index_sha256'): raise ValueError('캐시 색인 무결성')
        validate_index(index)
        result = _load_country(root,index,cc)
        if not any(row['code']==cc for row in index['countries']): raise ValueError('캐시 국가 누락')
        _cache_errors.pop(cc,None)
        return result
    except (OSError,ValueError,zlib.error) as exc:
        _cache_errors[cc]=str(exc)
        return None


def activate_country_cache(country, generation_root):
    """새 국가 자료를 전부 검증한 뒤 그 국가의 단일 포인터만 교체합니다."""
    if _cache_directory is None: raise ValueError('도시 행사 캐시 위치가 설정되지 않았습니다.')
    cc=normalize_country(country);root=Path(generation_root).resolve()
    expected=_cache_directory/'generations'
    if root.parent!=expected.resolve() or not re.fullmatch('[0-9a-f]{64}',root.name): raise ValueError('검증 캐시 세대 경로')
    raw,index=_read(root/'index.json',1024*1024);validate_index(index)
    if not any(row['code']==cc for row in index['countries']): raise ValueError('갱신 국가가 색인에 없습니다.')
    _load_country(root,index,cc)
    pointer=_cache_directory/'active'/(cc+'.json');pointer.parent.mkdir(parents=True,exist_ok=True)
    temp=pointer.with_suffix('.json.tmp')
    temp.write_text(json.dumps(dict(generation=root.name,index_sha256=hashlib.sha256(raw).hexdigest())),encoding='utf-8')
    temp.replace(pointer);clear_cache()
    return get_city_catalog_revision()


def get_city_catalog_revision():
    """동일 날짜·도시에서도 자료가 바뀌면 렌더 캐시키를 바꿉니다."""
    global _revision
    if _revision is None:
        digest=hashlib.sha256()
        index=_root()/'index.json'
        digest.update(index.read_bytes() if index.is_file() else b'unavailable')
        if _cache_directory is not None and (_cache_directory/'active').is_dir():
            for pointer in sorted((_cache_directory/'active').glob('??.json')):
                if pointer.is_file() and not pointer.is_symlink() and pointer.stat().st_size<=4096:
                    digest.update(pointer.name.encode('ascii'));digest.update(pointer.read_bytes())
        _revision=digest.hexdigest()
    return _revision


def _city_context(city_ref, country):
    cc = normalize_country(country)
    if city_ref is None: return cc, None
    if not isinstance(city_ref, dict): raise ValueError('도시 참조 형식')
    if normalize_country(city_ref.get('country_code')) != cc: raise ValueError('선택 도시와 국가가 다릅니다.')
    qid = city_ref.get('wikidata_qid')
    if qid is not None and not _qid(qid): raise ValueError('선택 도시 Wikidata 식별자')
    gid = city_ref.get('geonames_id')
    if gid is None and city_ref.get('provider') in ('geonames', 'open-meteo'):
        gid = city_ref.get('id')
    if gid is not None and (type(gid) is not int or not 0 < gid < 10**12): raise ValueError('선택 도시 GeoNames 식별자')
    confidence = city_ref.get('confidence', 'unknown')
    if confidence not in ('selected', 'estimated', 'unknown'): raise ValueError('도시 선택 확인 수준')
    return cc, dict(wikidata_qid=qid, geonames_id=gid, confidence=confidence)


def _matches(row, city):
    if city is None or (city['wikidata_qid'] is None and city['geonames_id'] is None): return False
    for ref in row['city_refs']:
        if city['wikidata_qid'] is not None and ref.get('wikidata_qid') != city['wikidata_qid']: continue
        if city['geonames_id'] is not None and ref.get('geonames_id') != city['geonames_id']: continue
        return True
    return False


def series_for_city(city_ref, country, language='ko'):
    if language not in ('ko', 'en'): raise ValueError('도시 행사 지원 언어')
    cc, city = _city_context(city_ref, country)
    # 함수 이름의 호환을 유지하며 개최분·미분류 항목도 목록에서 보존합니다.
    rows = [deepcopy(row) for row in _country(cc)['series'] if _matches(row, city)]
    for row in rows:
        row['display_title'] = row['title_en'] if language == 'en' else row['title']
    return sorted(rows, key=lambda row: row['id'])


def city_events_for_date(local_date, city_ref, country):
    if type(local_date) is not date or not FIRST_YEAR <= local_date.year <= LAST_YEAR:
        raise ValueError('도시 행사 지원 날짜는 2026~2099년입니다.')
    cc, city = _city_context(city_ref, country)
    target = local_date.isoformat()
    rows = []
    for row in _country(cc)['occurrences']:
        if row['status'] != 'announced' or target not in row['dates'] or not _matches(row, city): continue
        event = deepcopy(row)
        event.update(local_date=target, start_date=min(row['dates']), end_date=max(row['dates']),
                     selection_confidence=city['confidence'], date_precision='day')
        ref = next(ref for ref in row['city_refs'] if _matches({'city_refs': [ref]}, city))
        event.update(city_qid=ref['wikidata_qid'], geonames_id=ref.get('geonames_id'))
        rows.append(event)
    return sorted(rows, key=lambda row: row['id'])


def city_coverage(city_ref, country, year=FIRST_YEAR):
    if type(year) is not int or not FIRST_YEAR <= year <= LAST_YEAR: raise ValueError('도시 행사 지원 연도')
    cc, city = _city_context(city_ref, country)
    bundle = _country(cc)
    items = [row for row in bundle['series'] if _matches(row, city)]
    series = [row for row in items if row.get('item_role','unclassified')=='series']
    edition_count = sum(row.get('item_role')=='edition' for row in items)
    events = [row for row in bundle['occurrences'] if row['status'] == 'announced' and _matches(row, city)
              and any(day.startswith(str(year)+'-') for day in row['dates'])]
    days = {day for row in events for day in row['dates'] if day.startswith(str(year)+'-')}
    return dict(country_code=cc, year=year, catalog_items_count=len(items), series_count=len(series),
                edition_count=edition_count, unclassified_count=len(items)-len(series)-edition_count,
                catalog_series_count=len(series), announced_occurrences_count=len(events),
                announced_dates_count=len(days), catalog_only=bool(items) and not events,
                coverage_status=bundle['coverage_status'], first_year=FIRST_YEAR, last_year=LAST_YEAR,
                source_checked_at=bundle['source_checked_at'],
                selection_confidence=city['confidence'] if city else 'unknown',
                supported=bool(series or events), all_city_events_included=False,
                future_schedules_confirmed=False, update_status='cache_invalid_fallback' if cc in _cache_errors else 'available',
                update_error=_cache_errors.get(cc))


def announced_events_for_year(city_ref,country,year=FIRST_YEAR):
    """공식 발표분의 날짜 집합을 연도로 한정하되 원본 날짜와 출처를 보존합니다."""
    if type(year) is not int or not FIRST_YEAR<=year<=LAST_YEAR: raise ValueError('도시 행사 지원 연도')
    cc,city=_city_context(city_ref,country);rows=[]
    for row in _country(cc)['occurrences']:
        days=[day for day in row['dates'] if day.startswith(str(year)+'-')]
        if row['status']!='announced' or not days or not _matches(row,city): continue
        result=deepcopy(row);result.update(all_dates=list(row['dates']),dates=days,selection_confidence=city['confidence'])
        rows.append(result)
    return sorted(rows,key=lambda row:row['id'])
