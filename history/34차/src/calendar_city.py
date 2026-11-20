"""도시 식별 문맥을 좌표 추정 없이 작고 불변한 키로 전달합니다."""
import json
import re


def normalize_calendar_city(value):
    if value is None:
        return None
    if not isinstance(value,dict):
        raise ValueError('도시 식별 문맥 형식')
    code=value.get('country_code')
    confidence=value.get('confidence')
    if not isinstance(code,str) or not re.fullmatch('[A-Z]{2}',code) or confidence not in ('selected','estimated'):
        raise ValueError('도시 국가 또는 선택 출처')
    result=dict(country_code=code,confidence=confidence)
    identifier=value.get('geonames_id',value.get('id'))
    qid=value.get('wikidata_qid')
    if identifier is not None:
        if type(identifier) is not int or identifier <= 0:raise ValueError('GeoNames 식별자')
        result.update(provider='geonames',geonames_id=identifier)
    if qid is not None:
        if not isinstance(qid,str) or not re.fullmatch('Q[1-9][0-9]*',qid):raise ValueError('도시 Wikidata 식별자')
        result['wikidata_qid']=qid
    if identifier is None and qid is None:raise ValueError('검증된 도시 식별자가 없습니다.')
    provenance=value.get('provenance','')
    if not isinstance(provenance,str) or len(provenance)>200 or any(not c.isprintable() for c in provenance):raise ValueError('도시 출처 형식')
    result['provenance']=provenance
    return result


def city_key(value):
    value=normalize_calendar_city(value)
    return json.dumps(value,sort_keys=True,separators=(',',':')) if value is not None else ''
