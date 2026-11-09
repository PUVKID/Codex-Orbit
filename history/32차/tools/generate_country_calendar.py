"""검토한 holidays·CLDR 자료로 공개 가능한 국가별 행사 자료만 생성합니다."""
from pathlib import Path
import argparse,datetime,hashlib,json,sys,warnings

def main():
    p=argparse.ArgumentParser();p.add_argument('--dependency-dir',required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];dep=Path(a.dependency_dir).resolve()
    if not dep.is_dir() or not dep.is_relative_to(root/'work'):
        raise ValueError('현재 차수의 생성용 의존성 폴더만 허용합니다.')
    sys.path.insert(0,str(dep))
    import holidays
    from babel import Locale
    from babel import __version__ as babel_version
    if holidays.__version__!='0.108':raise ValueError('검토한 공휴일 자료 버전과 다릅니다.')
    target=root/'assets/holiday-calendar';target.mkdir(parents=True,exist_ok=True)
    ko,en=Locale.parse('ko'),Locale.parse('en');countries=[];limitations={};total=0
    sources=['https://github.com/vacanza/holidays','https://holidays.readthedocs.io/en/latest/','https://cldr.unicode.org/']
    generated=datetime.datetime.now(datetime.timezone.utc).isoformat()
    for number,cc in enumerate(sorted(holidays.list_supported_countries(include_aliases=False)),1):
        years={};country_warnings={}
        for year in range(2026,2100):
            with warnings.catch_warnings(record=True) as recorded:
                warnings.simplefilter('always')
                # 비공식 기념일은 지원되는 나라에서만 공휴일과 구별해 포함합니다.
                sample=holidays.country_holidays(cc,years=[],language='en_US')
                supported=set(sample.supported_categories)
                categories=[x for x in ('public','unofficial') if x in supported]
                if not categories:categories=[sample.default_category]
                all_days={};kind_by_date={}
                for category in categories:
                    english=holidays.country_holidays(cc,years=[year],language='en_US',categories=[category],expand=False)
                    local=holidays.country_holidays(cc,years=[year],language='ko' if cc=='KR' else 'en_US',categories=[category],expand=False)
                    for day in sorted(local):
                        if day.year!=year:continue
                        key=day.isoformat();row=all_days.setdefault(key,{'names':[],'english_names':[],'categories':[]})
                        row['names']=list(dict.fromkeys(row['names']+local.get_list(day)))
                        row['english_names']=list(dict.fromkeys(row['english_names']+english.get_list(day)))
                        row['categories']=list(dict.fromkeys(row['categories']+[category]))
                texts=list(dict.fromkeys(str(item.message) for item in recorded))
                # 동적으로 계산된 미래 날짜는 법적 확정 자료로 표시하지 않습니다.
                years[str(year)]={'events':all_days,'warnings':texts,'status':'limited' if texts else 'computed'}
                if texts:country_warnings[str(year)]=texts
                total+=len(all_days)
        document={'schema_version':1,'country_code':cc,'source':'holidays 0.108','generated_at':generated,'years':years}
        path=target/(cc+'.json');raw=(json.dumps(document,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8');path.write_bytes(raw)
        countries.append({'code':cc,'name_ko':ko.territories.get(cc,cc),'name_en':en.territories.get(cc,cc),'file':path.name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        if country_warnings:limitations[cc]=country_warnings
        if number%25==0:print(json.dumps({'countries_generated':number,'event_dates':total}),flush=True)
    metadata={'schema_version':1,'first_year':2026,'last_year':2099,'source_version':holidays.__version__,'country_name_source':'Babel '+babel_version+' / Unicode CLDR','generated_at':generated,'sources':sources,'scope':'국가 단위 공휴일과 자료가 지원하는 비공식 기념일. 모든 도시 축제·미래 법적 확정 일정 보장이 아님.','countries':countries,'event_dates':total}
    (target/'index.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for package in ('holidays','babel'):
        found=[]
        for info in dep.glob(package+'-*.dist-info'):
            found += [x for x in info.rglob('*') if x.is_file() and ('LICENSE' in x.name.upper() or 'COPYING' in x.name.upper())]
        if not found:raise ValueError('자료 라이선스를 찾지 못했습니다: '+package)
        (root/'assets'/(package+'-LICENSE.txt')).write_text('\n\n'.join(x.read_text(encoding='utf-8') for x in found),encoding='utf-8')
    # 국가 이름에 사용하는 CLDR 데이터의 별도 Unicode 고지를 함께 보존합니다.
    unicode_license=dep/'babel/locale-data/LICENSE.unicode'
    if not unicode_license.is_file():raise ValueError('Unicode CLDR 라이선스를 찾지 못했습니다.')
    (root/'assets/Unicode-CLDR-LICENSE.txt').write_bytes(unicode_license.read_bytes())
    proof={'generated_at':generated,'country_count':len(countries),'event_dates':total,'limited_countries':limitations,'versions':{'holidays':holidays.__version__,'Babel':babel_version},'future_dates_are_not_legally_confirmed':True,'source_urls':sources}
    (root/'evidence/국가행사32_생성결과_비공개.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'passed':True,'country_count':len(countries),'event_dates':total,'countries_with_limitations':len(limitations)},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
