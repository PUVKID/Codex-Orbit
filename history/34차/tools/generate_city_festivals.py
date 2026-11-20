"""공식 Wikidata의 유한한 순차 조회와 체크포인트로 도시 축제를 생성합니다."""
import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import gzip
import json
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from city_festivals import validate_country_file, validate_index

SERIES_LIMIT = 100000
NORMALIZED_LIMIT = 100*1024*1024
FOLLOWUP_PREFIXES = ['city-direct-v3-', 'city-parent-v3-', 'paris-offset-']


def stamp():
    return datetime.now(timezone(timedelta(hours=9))).isoformat()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, separators=(',', ':'))+'\n').encode('utf-8')


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw=encode(value)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_bytes(raw); temp.replace(path)
    return raw


class Collector:
    def __init__(self, checkpoint, offline=False, followup_window=None):
        self.checkpoint=checkpoint
        self.checkpoint.mkdir(parents=True, exist_ok=True)
        self.started=time.monotonic()
        self.elapsed_before_start=0.0
        self.phase_id='original-45m'
        self.manifest_sha256=None
        # 재개해도 같은 수집 작업의 총45분 창을 초기화하지 않습니다.
        log_path=self.checkpoint/'requests.jsonl'
        first=None
        if log_path.is_file():
            first=json.loads(log_path.read_text(encoding='utf-8').split('\n',1)[0])
            if not isinstance(first,dict) or not isinstance(first.get('recorded_at_kst'),str):
                raise ValueError('원 요청 기록의 객체·필수 시각 문자열이 없습니다.')
            first_time=datetime.fromisoformat(first['recorded_at_kst'])
            if first_time.tzinfo is None:raise ValueError('원 요청 기록 시각의 UTC 차이가 없습니다.')
            self.elapsed_before_start=max(0,time.time()-first_time.timestamp())
        original_start=datetime.fromisoformat(first['recorded_at_kst']).timestamp() if first else time.time()
        self.original_deadline=datetime.fromtimestamp(original_start+2700,timezone.utc).isoformat()
        self.current_deadline=self.original_deadline
        self.deadline_monotonic=self.started+2700-self.elapsed_before_start
        if followup_window is not None:
            self._load_followup(followup_window,log_path,first)
        self.last_request=0.0
        self.offline=offline

    def _load_followup(self, path, log_path, first):
        path=Path(path).resolve()
        if not path.is_relative_to((ROOT/'evidence').resolve()) or path.stat().st_size>16384:
            raise ValueError('후속 단계 manifest는 현재 evidence의16KiB 이하 파일이어야 합니다.')
        raw=path.read_bytes();manifest=json.loads(raw.decode('utf-8'))
        required={'schema_version','phase_id','session','task','checkpoint','original_started_at','original_deadline',
                  'original_exit_code','original_requests_bytes','original_requests_sha256','started_at','deadline',
                  'duration_seconds','allowed_request_prefixes'}
        if not isinstance(manifest,dict) or not required<=manifest.keys():raise ValueError('후속 단계 필수 필드')
        if (type(manifest['schema_version']) is not int or manifest['schema_version']!=1 or
            manifest['phase_id']!='city-join-paris-1' or type(manifest['duration_seconds']) is not int or
            manifest['duration_seconds']!=1800 or manifest['allowed_request_prefixes']!=FOLLOWUP_PREFIXES):
            raise ValueError('후속 단계 고정 범위·30분 상한')
        if type(manifest['original_exit_code']) is not int or manifest['original_exit_code']!=1:
            raise ValueError('원 수집 단계의 실제 실패 종료 코드')
        if not first or manifest['session']!=first.get('session') or manifest['task']!=first.get('task'):
            raise ValueError('원 수집 session/task 불일치')
        checkpoint=(ROOT/manifest['checkpoint']).resolve()
        if checkpoint!=self.checkpoint.resolve() or not checkpoint.is_relative_to((ROOT/'evidence').resolve()):
            raise ValueError('후속 단계 체크포인트 불일치')
        moments={}
        for field in ('original_started_at','original_deadline','started_at','deadline'):
            moment=datetime.fromisoformat(manifest[field])
            if moment.tzinfo is None:raise ValueError('후속 단계 시각의 UTC 차이 누락')
            moments[field]=moment.timestamp()
        original_first=datetime.fromisoformat(first['recorded_at_kst']).timestamp()
        if (moments['original_started_at']!=original_first or
            moments['original_deadline']-moments['original_started_at']!=2700 or
            moments['deadline']-moments['started_at']!=1800 or
            moments['started_at']<moments['original_deadline'] or moments['started_at']>time.time()):
            raise ValueError('원45분·후속30분 절대 시각 불일치')
        size=manifest['original_requests_bytes'];digest=manifest['original_requests_sha256']
        if type(size) is not int or not 0<size<=log_path.stat().st_size or not re.fullmatch('[0-9a-f]{64}',digest):
            raise ValueError('원 요청 기록 바이트·해시 형식')
        with log_path.open('rb') as stream:previous=stream.read(size)
        if not previous.endswith(b'\n') or hashlib.sha256(previous).hexdigest()!=digest:
            raise ValueError('원 요청 기록 prefix 해시 불일치')
        manifest_sha=hashlib.sha256(raw).hexdigest();marker=self.checkpoint/'followup-window.json'
        if marker.is_file():
            prior=json.loads(marker.read_text(encoding='utf-8'))
            if prior.get('manifest_sha256')!=manifest_sha:raise ValueError('이미 고정된 후속 단계를 교체할 수 없습니다.')
        else:
            save(marker,dict(manifest_sha256=manifest_sha,manifest_path=str(path),manifest=manifest,first_loaded_at=stamp()))
        self.phase_id=manifest['phase_id'];self.manifest_sha256=manifest_sha
        self.original_deadline=manifest['original_deadline'];self.current_deadline=manifest['deadline']
        self.deadline_monotonic=self.started+(moments['deadline']-time.time())

    def remaining(self):
        return self.deadline_monotonic-time.monotonic()

    def _allow_network(self,name,url):
        if self.offline:raise ValueError('네트워크 없는 정규화에 필요한 체크포인트가 없습니다: '+name)
        if self.phase_id=='original-45m':return
        parsed=urlsplit(url)
        official=parsed.scheme=='https' and not parsed.username and not parsed.password and not parsed.fragment and parsed.port is None
        city=bool(re.fullmatch(r'city-(?:direct|parent)-v3-[0-9a-f]{20}',name))
        paris=bool(re.fullmatch(r'paris-offset-(?:0|[1-9][0-9]*)',name))
        if not official or not ((city and parsed.netloc=='query.wikidata.org' and parsed.path=='/sparql') or
                                (paris and parsed.netloc=='opendata.paris.fr' and parsed.path=='/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records')):
            raise ValueError('후속 단계는 미완료 도시·파리의 공식 요청만 허용합니다: '+name)

    def log(self, value):
        state_files=list((ROOT/'.codex/routing-state').glob('*.json'))
        state=json.loads(state_files[0].read_text(encoding='utf-8')) if len(state_files)==1 else {}
        value.update(recorded_at_kst=stamp(),cwd=str(ROOT),session=state.get('session_id'),task=state.get('task_id'),
                     repair_used=state.get('repair_used'),input_fix_used=state.get('input_fix_used'),
                     collection_phase_id=self.phase_id,followup_manifest_sha256=self.manifest_sha256,
                     original_deadline=self.original_deadline,current_deadline=self.current_deadline)
        with (self.checkpoint/'requests.jsonl').open('a',encoding='utf-8',newline='\n') as f:
            f.write(json.dumps(value,ensure_ascii=False)+'\n')

    def query(self, name, query):
        path=self.checkpoint/(name+'.json')
        if path.is_file(): return json.loads(path.read_text(encoding='utf-8'))
        if self.offline:raise ValueError('네트워크 없는 정규화에 필요한 체크포인트가 없습니다: '+name)
        url='https://query.wikidata.org/sparql?'+urlencode({'query':query,'format':'json'})
        return self.fetch(name,url)

    def fetch(self,name,url):
        path=self.checkpoint/(name+'.json')
        if path.is_file(): return json.loads(path.read_text(encoding='utf-8'))
        self._allow_network(name,url)
        headers={'User-Agent':'CodexOrbit-CityFestivals/1.0 (https://github.com/PUVKID/Codex-Orbit)',
                 'Accept':'application/json','Accept-Encoding':'identity'}
        while True:
            remaining=self.remaining()
            if remaining<=0: raise TimeoutError('도시 축제 수집 단계의 고정 종료시각입니다: '+self.phase_id)
            wait=max(0,1-(time.monotonic()-self.last_request))
            if wait>=remaining:raise TimeoutError('다음 요청 대기가 수집 단계 종료시각을 넘습니다.')
            if wait: time.sleep(wait)
            remaining=self.remaining()
            if remaining<=0:raise TimeoutError('도시 축제 수집 단계의 고정 종료시각입니다: '+self.phase_id)
            self.last_request=time.monotonic()
            request=dict(name=name,url=url,method='GET',headers=headers,timeout_seconds=min(55,remaining),max_raw_bytes=15*1024*1024)
            self.log(dict(request,phase='before_request'))
            try:
                with urlopen(Request(url,headers=headers),timeout=min(55,remaining)) as response:
                    raw=response.read(15*1024*1024+1)
                    if len(raw)>15*1024*1024: raise ValueError('공식 응답 원문15MiB 상한')
                    (self.checkpoint/(name+'.raw')).write_bytes(raw)
                    if raw.startswith(b'\x1f\x8b'):
                        decoder=zlib.decompressobj(16+zlib.MAX_WBITS)
                        text=decoder.decompress(raw,16*1024*1024+1)
                        if len(text)>16*1024*1024 or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
                            raise ValueError('공식 압축 응답16MiB·단일스트림 상한')
                    else: text=raw
                    value=json.loads(text.decode('utf-8'))
                    save(path,value)
                    self.log(dict(request,phase='success',http_status=response.status,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
                    return value
            except Exception as exc:
                details=dict(request,phase='failure',error_type=type(exc).__name__,error=str(exc))
                if isinstance(exc,HTTPError):
                    details.update(http_status=exc.code,error_body=exc.read(16384).decode('utf-8','replace'),retry_after=exc.headers.get('Retry-After'))
                self.log(details)
                if isinstance(exc,HTTPError) and exc.code==429:
                    retry=exc.headers.get('Retry-After','60')
                    try: delay=max(1,int(retry))
                    except ValueError: raise ValueError('429 Retry-After가 초 단위가 아닙니다.') from exc
                    if delay>=self.remaining(): raise TimeoutError('429 대기가 수집 단계의 고정 종료시각을 넘습니다.') from exc
                    print(json.dumps(dict(status='rate_limited',retry_after_seconds=delay)),flush=True)
                    time.sleep(delay)
                    continue
                raise


def list_ids(collector):
    # 단일 이름검색이나 임의 국가 표본 대신 축제 시리즈 분류의 전체 QID를 한정 조회합니다.
    query='SELECT DISTINCT ?item WHERE { ?item wdt:P31/wdt:P279* wd:Q132241. } LIMIT 100001'
    data=collector.query('classification-ids-limit100001',query)
    rows=data['results']['bindings']
    ids=sorted({row['item']['value'].rsplit('/',1)[-1] for row in rows},key=lambda x:int(x[1:]))
    if any(not re.fullmatch('Q[1-9][0-9]*',qid) for qid in ids): raise ValueError('공식 QID 형식')
    result=dict(checked_at=stamp(),query=query,returned_rows=len(rows),unique_ids=len(ids),
                cap=SERIES_LIMIT,truncated=len(ids)>SERIES_LIMIT,complete=len(ids)<=SERIES_LIMIT,ids=ids[:SERIES_LIMIT])
    save(collector.checkpoint/'series-ids.json',result)
    print(json.dumps({key:value for key,value in result.items() if key!='ids'},ensure_ascii=False),flush=True)
    return result


def scalar(row,key,default=''):
    return row.get(key,{}).get('value',default)


def clean(value,limit=320):
    return ''.join(c for c in value if c.isprintable()).strip()[:limit]


def kind_for(value):
    value=value.casefold()
    for words,kind in [(('film','cinema','ciném'),'film'),(('snow','ice festival','yuki'),'snow'),
                       (('balloon',),'balloon'),
                       (('light','lantern','illumin'),'lights'),(('carnival','carnaval','mardi gras'),'carnival'),
                       (('flower','cherry blossom','tulip','rose festival'),'flowers'),
                       (('music','jazz','rock','opera','song','folk music'),'music')]:
        if any(word in value for word in words): return kind
    return 'culture'


def normalize_metadata(rows):
    result={}
    for source in rows:
        qid=scalar(source,'item').rsplit('/',1)[-1]
        if not re.fullmatch('Q[1-9][0-9]*',qid): raise ValueError('메타 항목 QID')
        row=result.setdefault(qid,dict(id='wikidata:'+qid,title=qid,title_en=qid,kind='culture',country_codes=[],
                                      location_qids=[],type_qids=[],type_labels=[],parent_series=[],observed_dates=[],month_qids=[],
                                      source_url='https://www.wikidata.org/wiki/'+qid,license='CC0-1.0',status='catalog_only',item_role='unclassified'))
        en,ko=clean(scalar(source,'en')),clean(scalar(source,'ko'))
        if en: row['title_en']=en
        if ko or en: row['title']=ko or en
        for field,key in [('place','location_qids'),('admin','location_qids'),('type','type_qids'),('series','parent_series'),('month','month_qids')]:
            value=scalar(source,field).rsplit('/',1)[-1]
            if re.fullmatch('Q[1-9][0-9]*',value) and value not in row[key]: row[key].append(value)
        cc=scalar(source,'cc')
        if re.fullmatch('[A-Z]{2}',cc) and cc not in row['country_codes']: row['country_codes'].append(cc)
        label=clean(scalar(source,'typeLabel'))
        if label and label not in row['type_labels']: row['type_labels'].append(label)
        for key in ('start','end','point'):
            value=scalar(source,key)
            observed=dict(property=key,value=value,precision='unknown')
            if value and observed not in row['observed_dates']:
                row['observed_dates'].append(observed)
        if scalar(source,'dissolved'): row['status']='discontinued'
    return classify_metadata(result)


def classify_metadata(result):
    # 일반 축제 분류와 반복 시리즈의 구조적 근거를 구분합니다.
    referenced={qid for row in result.values() for qid in row['parent_series']}
    for qid,row in result.items():
        labels=' '.join(row['type_labels']).casefold()
        row['kind']=kind_for(labels+' '+row['title_en'])
        if 'edition' in labels or 'occurrence' in labels or (row['parent_series'] and row['observed_dates']):
            row.update(item_role='edition',role_evidence='P31 개최분 분류 또는 P179 시리즈 관계와 관측 시점')
        elif any(text.casefold() in ('recurring event','annual event','biennial event','periodic event') for text in row['type_labels']):
            row.update(item_role='series',role_evidence='P31에 명시된 반복 행사 분류')
        elif qid in referenced:
            row.update(item_role='series',role_evidence='수집한 전체 메타에서 P179 시리즈 참조의 대상')
        else:row.update(item_role='unclassified',role_evidence='최소 메타에서 반복 시리즈·개최분 구분 근거 부족')
    return result


def collect_metadata(collector, ids):
    all_rows={}
    history=(collector.checkpoint/'requests.jsonl').read_text(encoding='utf-8').split('\n')[:-1]
    timed_out={row['name'] for row in (json.loads(line) for line in history) if row.get('phase')=='failure' and row.get('error_type')=='TimeoutError'}
    for offset in range(0,len(ids),200):
        batch=ids[offset:offset+200]
        name='metadata-'+hashlib.sha256(' '.join(batch).encode()).hexdigest()[:20]
        # 성공한200개 원문은 보존하며 실제 시간 초과 묶음만100개 두 요청으로 나눕니다.
        parts=[batch]
        if name in timed_out and not (collector.checkpoint/(name+'.json')).is_file():parts=[batch[:100],batch[100:]]
        for part in parts:
            response=collector.query('metadata-'+hashlib.sha256(' '.join(part).encode()).hexdigest()[:20],metadata_query(part))
            normalized=normalize_metadata(response['results']['bindings'])
            if set(normalized)!=set(part):raise ValueError('요청 메타 QID와 응답 항목이 다릅니다.')
            all_rows.update(normalized)
        if offset%1000==0: print(json.dumps(dict(phase='metadata',completed=len(all_rows),total=len(ids))),flush=True)
    # 모든 묶음을 모은 뒤 다른 묶음의 P179 참조 대상도 재분류합니다.
    classify_metadata(all_rows)
    save(collector.checkpoint/'normalized-metadata.json',all_rows)
    return all_rows


def metadata_query(batch):
    return '''SELECT ?item ?en ?ko ?cc ?place ?admin ?type ?typeLabel ?series ?month ?start ?end ?point ?dissolved WHERE {
 VALUES ?item { %s }
 OPTIONAL { ?item rdfs:label ?en. FILTER(LANG(?en)="en") }
 OPTIONAL { ?item rdfs:label ?ko. FILTER(LANG(?ko)="ko") }
 OPTIONAL { ?item wdt:P17/wdt:P297 ?cc. }
 OPTIONAL { ?item wdt:P276 ?place. }
 OPTIONAL { ?item wdt:P131 ?admin. }
 OPTIONAL { ?item wdt:P31 ?type. OPTIONAL { ?type rdfs:label ?typeLabel. FILTER(LANG(?typeLabel)="en") } }
 OPTIONAL { ?item wdt:P179 ?series. }
 OPTIONAL { ?item wdt:P2922 ?month. }
 OPTIONAL { ?item wdt:P580 ?start. }
 OPTIONAL { ?item wdt:P582 ?end. }
 OPTIONAL { ?item wdt:P585 ?point. }
 OPTIONAL { ?item wdt:P576 ?dissolved. }
}''' % ' '.join('wd:'+qid for qid in batch)


def collect_cities(collector,places,priority_places=()):
    result={}
    type_query='''SELECT DISTINCT ?type ?root WHERE {
 VALUES ?root { wd:Q486972 wd:Q515 }
 ?type wdt:P279* ?root.
} LIMIT 20001'''
    response=collector.query('settlement-types-v2-limit20001',type_query)
    rows=response['results']['bindings']
    if len(rows)>=20001:raise ValueError('도시 분류 집합20000상한에서 잘림을 발견했습니다.')
    settlement_types={'Q486972'};city_types={'Q515'}
    for row in rows:
        target=scalar(row,'type').rsplit('/',1)[-1];root=scalar(row,'root').rsplit('/',1)[-1]
        if not re.fullmatch('Q[1-9][0-9]*',target):raise ValueError('도시 분류 QID')
        if root=='Q486972':settlement_types.add(target)
        elif root=='Q515':city_types.add(target)
        else:raise ValueError('도시 분류 기준 식별자')
    save(collector.checkpoint/'settlement-types-v2-proof.json',dict(settlement_types=len(settlement_types),city_types=len(city_types),truncated=False))
    priority=sorted(set(priority_places),key=lambda qid:int(qid[1:]))
    remaining=[qid for qid in places if qid not in priority]
    batches=([priority] if priority else [])+[remaining[offset:offset+200] for offset in range(0,len(remaining),200)]
    for number,batch in enumerate(batches):
        requests=[]
        for relation in ('direct','parent'):
            name='city-'+relation+'-v3-'+hashlib.sha256(' '.join(batch).encode()).hexdigest()[:20]
            # 성공한200개 캐시는 재사용하고 미확인 부모 후보는100개 이하로 조회합니다.
            parts=[batch]
            if relation=='parent' and len(batch)>100 and not (collector.checkpoint/(name+'.json')).is_file():
                parts=[batch[offset:offset+100] for offset in range(0,len(batch),100)]
            requests.extend((relation,part) for part in parts)
        for relation,part in requests:
            binding='VALUES ?city { %s } BIND(?city AS ?place)' if relation=='direct' else 'VALUES ?place { %s } ?place wdt:P131/wdt:P131?/wdt:P131? ?city.'
            if relation=='parent':binding='hint:Query hint:optimizer "None".\n '+binding
            query='''SELECT DISTINCT ?place ?city ?cc ?gid ?en ?ko ?type WHERE {
 %s
 ?city wdt:P31 ?type.
 ?city wdt:P17/wdt:P297 ?cc.
 OPTIONAL { ?city wdt:P1566 ?gid. }
 OPTIONAL { ?city rdfs:label ?en. FILTER(LANG(?en)="en") }
 OPTIONAL { ?city rdfs:label ?ko. FILTER(LANG(?ko)="ko") }
}''' % (binding % ' '.join('wd:'+qid for qid in part))
            response=collector.query('city-'+relation+'-v3-'+hashlib.sha256(' '.join(part).encode()).hexdigest()[:20],query)
            for source in response['results']['bindings']:
                place=scalar(source,'place').rsplit('/',1)[-1];city=scalar(source,'city').rsplit('/',1)[-1];cc=scalar(source,'cc')
                kind=scalar(source,'type').rsplit('/',1)[-1]
                if kind not in (settlement_types if relation=='direct' else city_types):continue
                if place not in part or not re.fullmatch('Q[1-9][0-9]*',city) or not re.fullmatch('[A-Z]{2}',cc):
                    raise ValueError('도시 응답 식별자·국가')
                ref=dict(wikidata_qid=city,country_code=cc,name=clean(scalar(source,'ko') or scalar(source,'en') or city),name_en=clean(scalar(source,'en') or city),
                         relation='direct_settlement' if relation=='direct' else 'administrative_parent')
                gid=scalar(source,'gid')
                if gid.isdigit() and 0<int(gid)<10**12:ref['geonames_id']=int(gid)
                if ref not in result.setdefault(place,[]):result[place].append(ref)
            if number==0 and priority:
                print(json.dumps(dict(phase='priority_cities',relation=relation,requested=len(priority),mapped=sum(qid in result for qid in priority))),flush=True)
        save(collector.checkpoint/'city-mapping-partial.json',result)
        if number%5==0: print(json.dumps(dict(phase='places',batches_completed=number+1,total_batches=len(batches),mapped_places=len(result))),flush=True)
    save(collector.checkpoint/'city-mapping.json',result)
    return result


PARIS_PAGE_DATES = {
    '126680': {'2026-11-11'},
    '105852': {'2026-11-18'},
}


def normalize_paris(source, checked_at, rejections=None):
    def reject(reason):
        if rejections is not None:rejections[reason]=rejections.get(reason,0)+1
        return None
    if source.get('address_city','').strip().casefold()!='paris':return reject('other_city')
    title=clean(source.get('title',''))
    url=source.get('url','')
    if not title or not isinstance(url,str) or not url.startswith('https://www.paris.fr/evenements/'):return reject('invalid_identity')
    ident=str(source.get('id',''))
    if not re.fullmatch('[1-9][0-9]*',ident):return reject('invalid_identity')
    try:
        raw_start=datetime.fromisoformat(source['date_start']);raw_end=datetime.fromisoformat(source['date_end'])
    except (KeyError,TypeError,ValueError):return reject('missing_or_invalid_bounds')
    if raw_start.tzinfo is None or raw_end.tzinfo is None or raw_end<raw_start:return reject('missing_or_invalid_bounds')
    occurrences=source.get('occurrences')
    if not isinstance(occurrences,str) or len(occurrences)>100000:return reject('missing_or_invalid_occurrences')
    matches=re.findall(r'(\d{4}-\d\d-\d\dT[^_\s;,]+)_(\d{4}-\d\d-\d\dT[^_\s;,]+)',occurrences)
    if not matches:return reject('missing_or_invalid_occurrences')
    days=set();conflict=False;date_conflict=False;parsed=[]
    for start,end in matches:
        try: a,b=datetime.fromisoformat(start),datetime.fromisoformat(end)
        except ValueError:return reject('invalid_occurrence_datetime')
        # 기간 사이를 보간하지 않고 명시된 동일 일자 개최만 수록합니다.
        if a.date()!=b.date() or not 2026<=a.year<=2099:continue
        if a.tzinfo is None or b.tzinfo is None or b<a:continue
        days.add(a.date().isoformat())
        parsed.append((a,b))
        if not raw_start.date()<=a.date()<=raw_end.date():date_conflict=True
    if not days:return reject('no_explicit_single_day_occurrence')
    for raw,value in [(raw_start,min(parsed,key=lambda pair:pair[0])[0]),(raw_end,max(parsed,key=lambda pair:pair[1])[1])]:
        if raw.date()==value.date() and (raw.utcoffset()!=value.utcoffset() or raw.time()!=value.time()):conflict=True
    evidence='official_api_consistent'
    if conflict or date_conflict:
        allowed=PARIS_PAGE_DATES.get(ident,set())
        days=days & allowed
        if not days:return reject('unverified_date_conflict' if date_conflict else 'unverified_time_conflict')
        evidence='official_page_crosschecked'
    return dict(id='paris:'+ident,series_id=None,title=title,title_en=title,kind=kind_for(title+' '+str(source.get('qfap_tags',''))),
                country_code='FR',city_refs=[dict(wikidata_qid='Q90',geonames_id=2988507)],dates=sorted(days),date_precision='day',
                status='announced',time_conflict=conflict,date_conflict=date_conflict,source_url=url,license='ODbL-1.0',checked_at=checked_at,
                source_updated_at=source.get('updated_at'),location_confidence='city_verified',
                date_evidence=evidence,independent_page_checked_on='2026-11-10' if evidence=='official_page_crosschecked' else None)


def collect_paris(collector):
    rows=[];total=None;offset=0;rejected=0;rejections={}
    while total is None or offset<total:
        url='https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records?'+urlencode({'limit':100,'offset':offset,'order_by':'id'})
        data=collector.fetch('paris-offset-'+str(offset),url)
        if type(data.get('total_count')) is not int or not isinstance(data.get('results'),list):raise ValueError('파리 API 페이지 형식')
        if total is None:total=data['total_count']
        if not 0<=total<=10000:raise ValueError('파리 API 전체페이지 한도10000')
        if not data['results'] and offset<total:raise ValueError('파리 API 중간 빈 페이지')
        for source in data['results']:
            row=normalize_paris(source,stamp(),rejections)
            if row:rows.append(row)
            else:rejected+=1
        offset+=len(data['results'])
    unique={row['id']:row for row in rows}
    proof=dict(source_total_at_first_page=total,downloaded_rows=offset,accepted_occurrences=len(unique),rejected_rows=rejected,
               snapshot_may_change_during_pagination=True,license='ODbL-1.0',rejections_by_reason=rejections,
               official_page_crosschecked_occurrences=sum(row['date_evidence']=='official_page_crosschecked' for row in unique.values()),
               official_api_consistent_occurrences=sum(row['date_evidence']=='official_api_consistent' for row in unique.values()))
    save(collector.checkpoint/'paris-proof.json',proof)
    return sorted(unique.values(),key=lambda row:row['id']),proof


def build_assets(collector,ids_info,metadata,cities,paris_rows,paris_proof):
    target=ROOT/'assets/city-festivals'
    generated=stamp();catalog={};announced={};odbl={'FR':paris_rows} if paris_rows else {}
    curated_path=target/'official-announcements.json'
    curated=json.loads(curated_path.read_text(encoding='utf-8')) if curated_path.is_file() else {'occurrences':[]}
    for row in curated['occurrences']:
        verified=[]
        for ref in row['city_refs']:
            options=[value for value in cities.get(ref['wikidata_qid'],[]) if value['wikidata_qid']==ref['wikidata_qid'] and value['country_code']==row['country_code']]
            if not options:raise ValueError('공식 발표 도시의 국가·정체성 연결 미확인: '+row['id'])
            for value in options:
                if value not in verified:verified.append(value)
        row=dict(row,city_refs=verified);announced.setdefault(row['country_code'],[]).append(row)
    for base in metadata.values():
        refs=[ref for qid in base['location_qids'] for ref in cities.get(qid,[])]
        codes=base['country_codes'] or sorted({ref['country_code'] for ref in refs}) or ['ZZ']
        for cc in codes:
            row=dict(base,country_code=cc,city_refs=[])
            for ref in refs:
                if ref['country_code']==cc and ref not in row['city_refs']:row['city_refs'].append(ref)
            row.pop('country_codes');catalog.setdefault(cc,[]).append(row)
    countries=[];total_bytes=0
    for cc in sorted(set(catalog)|set(announced)|set(odbl)):
        files=[]
        for folder,key,source,license_id in [('catalog','series',catalog,'CC0-1.0'),('announced','occurrences',announced,'factual-schedule'),('odbl','occurrences',odbl,'ODbL-1.0')]:
            if cc not in source:continue
            value=dict(schema_version=1,country_code=cc,license=license_id,generated_at=generated,**{key:sorted(source[cc],key=lambda row:row['id'])})
            validate_country_file(value,cc,folder)
            raw=encode(value);total_bytes+=len(raw)
            if len(raw)>8*1024*1024 or total_bytes>NORMALIZED_LIMIT:raise ValueError('정규화 국가8MiB·총100MiB 상한')
            path=folder+'/'+cc+('.json.gz' if folder=='catalog' else '.json')
            payload=gzip.compress(raw,mtime=0) if folder=='catalog' else raw
            output=target/path;output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(payload)
            files.append(dict(path=path,bytes=len(payload),expanded_bytes=len(raw),sha256=hashlib.sha256(payload).hexdigest(),license=license_id))
        countries.append(dict(code=cc,files=files))
    series_count=sum(row['item_role']=='series' for row in metadata.values())
    edition_count=sum(row['item_role']=='edition' for row in metadata.values())
    unclassified_count=sum(row['item_role']=='unclassified' for row in metadata.values())
    dates={cc+':'+ref['wikidata_qid']+':'+day for cc,rows in list(announced.items())+list(odbl.items()) for row in rows for ref in row['city_refs'] for day in row['dates']}
    catalog_cities={ref['wikidata_qid'] for rows in catalog.values() for row in rows for ref in row['city_refs']}
    announced_cities={ref['wikidata_qid'] for rows in list(announced.values())+list(odbl.values()) for row in rows for ref in row['city_refs']}
    occurrences=sum(len(rows) for rows in announced.values())+len(paris_rows)
    index=dict(schema_version=1,first_year=2026,last_year=2099,generated_at=generated,coverage_status='partial',countries=countries,
               collection=dict(classification='wd:Q132241 / P31/P279*',classification_ids_count=ids_info['unique_ids'],
                               classification_query_complete=ids_info['complete'],normalized_item_count=len(metadata),
                               catalog_items_count=len(metadata),series_count=series_count,edition_item_count=edition_count,
                               unclassified_count=unclassified_count,metadata_complete=len(metadata)==ids_info['unique_ids'],
                               city_count=len(catalog_cities|announced_cities),catalog_city_count=len(catalog_cities),announced_city_count=len(announced_cities),
                               normalized_country_count=len(set(catalog)-{'ZZ'}),country_bucket_count=len(catalog),
                               announced_country_count=len(set(announced)|set(odbl)),unassigned_country_items=len(catalog.get('ZZ',[])),
                               announced_occurrences_count=occurrences,announced_city_dates_count=len(dates),
                               normalized_bytes=total_bytes,all_world_city_events_complete=False,
                               snapshot_may_change_during_collection=True,paris=paris_proof),
               sources=[dict(provider='Wikidata',url='https://www.wikidata.org',license='CC0-1.0'),
                        dict(provider='Ville de Paris',url='https://opendata.paris.fr/explore/dataset/que-faire-a-paris-/',license='ODbL-1.0'),
                        dict(provider='공식 주최자·관광청의 발표 일정 사실',license='factual-schedule')])
    validate_index(index);save(target/'index.json',index)
    save(collector.checkpoint/'generation-result.json',index['collection'])
    print(json.dumps(index['collection'],ensure_ascii=False),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--ids-only',action='store_true')
    parser.add_argument('--catalog-only',action='store_true')
    parser.add_argument('--offline',action='store_true')
    parser.add_argument('--followup-window',type=Path)
    parser.add_argument('--checkpoint',type=Path,default=ROOT/'evidence/도시축제33_수집체크포인트_비공개')
    args=parser.parse_args()
    checkpoint=args.checkpoint.resolve()
    if not checkpoint.is_relative_to(ROOT/'evidence'): raise ValueError('현재 프로젝트 evidence 체크포인트만 허용합니다.')
    collector=Collector(checkpoint,offline=args.offline,followup_window=args.followup_window)
    result=list_ids(collector)
    if args.ids_only: return
    metadata=collect_metadata(collector,result['ids'])
    curated_path=ROOT/'assets/city-festivals/official-announcements.json'
    curated=json.loads(curated_path.read_text(encoding='utf-8')) if curated_path.is_file() else {'occurrences':[]}
    places=sorted({qid for row in metadata.values() for qid in row['location_qids']} |
                  {ref['wikidata_qid'] for row in curated['occurrences'] for ref in row['city_refs']},key=lambda qid:int(qid[1:]))
    priority=[ref['wikidata_qid'] for row in curated['occurrences'] for ref in row['city_refs']]
    cities=collect_cities(collector,places,priority)
    paris_rows,paris_proof=([],dict(not_requested=True)) if args.catalog_only else collect_paris(collector)
    build_assets(collector,result,metadata,cities,paris_rows,paris_proof)


if __name__=='__main__': main()
