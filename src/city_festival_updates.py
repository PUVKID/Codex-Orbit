"""명시적으로 요청한 국가의 안전한 JSON 자료만 비동기로 갱신합니다."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import zlib
from PySide6.QtCore import QObject, QTimer, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from city_festivals import (FILE_LIMIT, activate_country_cache, configure_city_cache,
                            get_city_catalog_revision, normalize_country, validate_country_file, validate_index)

BASE_URL='https://raw.githubusercontent.com/PUVKID/Codex-Orbit/main/assets/city-festivals/'


def allowed_url(url):
    if not isinstance(url,str) or not url.startswith(BASE_URL):return False
    relative=url[len(BASE_URL):]
    return relative=='index.json' or re.fullmatch(r'(catalog|announced|odbl)/[A-Z]{2}\.json(?:\.gz)?',relative) is not None


def validate_download(raw,meta,country):
    if not isinstance(raw,bytes) or len(raw)>FILE_LIMIT or len(raw)!=meta.get('bytes'):
        raise ValueError('다운로드 자료 크기가 다릅니다.')
    if hashlib.sha256(raw).hexdigest()!=meta.get('sha256'):raise ValueError('다운로드 자료 해시가 다릅니다.')
    path=meta.get('path','')
    if not allowed_url(BASE_URL+path) or not path.split('/')[-1].startswith(country+'.json'):
        raise ValueError('다운로드 국가·경로가 다릅니다.')
    decoded=raw
    if path.endswith('.gz'):
        decoder=zlib.decompressobj(16+zlib.MAX_WBITS);decoded=decoder.decompress(raw,FILE_LIMIT+1)
        if len(decoded)>FILE_LIMIT or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
            raise ValueError('다운로드 압축 자료 한도·형식')
    if 'expanded_bytes' in meta and len(decoded)!=meta['expanded_bytes']:raise ValueError('압축 해제 크기가 다릅니다.')
    try:value=json.loads(decoded.decode('utf-8'))
    except (UnicodeError,json.JSONDecodeError) as exc:raise ValueError('다운로드 JSON 형식') from exc
    return validate_country_file(value,country,path.split('/')[0])


class CityFestivalUpdater(QObject):
    changed=Signal(str)
    updated=Signal(dict)
    failed=Signal(str)

    def __init__(self,data_dir,parent=None):
        super().__init__(parent)
        self.directory=Path(data_dir).resolve()/'city-festivals'
        configure_city_cache(data_dir)
        self.manager=QNetworkAccessManager(self)
        self.reply=None;self.closed=False;self.busy=False;self.generation=0
        self.country=None;self.buffer=bytearray();self.queue=[];self.payloads={};self.remote_index=None;self.index_bytes=None
        self.deadline=QTimer(self);self.deadline.setSingleShot(True);self.deadline.timeout.connect(self._timeout)
        self.last_status=dict(status='not_requested')

    def refresh(self,country):
        if self.closed or self.busy:return False
        cc=normalize_country(country)
        self.country=cc
        attempt=self.directory/'attempts'/(cc+'.json')
        try:
            if attempt.is_file() and attempt.stat().st_size>4096:raise ValueError('갱신 기록 크기 한도')
            saved=json.loads(attempt.read_text(encoding='utf-8')) if attempt.is_file() else {}
            if saved.get('date')==datetime.now(timezone.utc).date().isoformat():
                self.last_status=dict(status='daily_limit',country_code=cc);self.updated.emit(dict(self.last_status));return False
            self.directory.mkdir(parents=True,exist_ok=True);attempt.parent.mkdir(exist_ok=True)
            stamp=dict(date=datetime.now(timezone.utc).date().isoformat(),status='attempted')
            temporary=attempt.with_suffix('.json.tmp');temporary.write_text(json.dumps(stamp),encoding='utf-8');temporary.replace(attempt)
        except (OSError,ValueError):
            self._fail('도시 행사 갱신 기록을 읽거나 저장하지 못했습니다. 이전 자료를 유지합니다.');return False
        self.country=cc;self.busy=True;self.generation+=1;self.payloads={};self.queue=[];self.remote_index=None;self.index_bytes=None
        self.last_status=dict(status='checking',country_code=cc);self._request('index.json',1024*1024)
        return True

    def _request(self,path,limit):
        url=BASE_URL+path
        if not allowed_url(url):self._fail('도시 행사 갱신 주소가 허용된 원천과 다릅니다.');return
        token=self.generation
        request=QNetworkRequest(QUrl(url))
        request.setRawHeader(b'Accept',b'application/json')
        request.setRawHeader(b'User-Agent',b'CodexOrbit-CityFestivals/1.0')
        request.setAttribute(QNetworkRequest.Attribute.RedirectPolicyAttribute,QNetworkRequest.RedirectPolicy.ManualRedirectPolicy)
        reply=self.manager.get(request);self.reply=reply;self.buffer=bytearray();self.current_path=path;self.current_limit=limit
        reply.readyRead.connect(lambda:self._read(reply,token))
        reply.finished.connect(lambda:self._finished(reply,token))
        self.deadline.start(8000)

    def _read(self,reply,token):
        if self.closed or token!=self.generation or reply is not self.reply:return
        self.buffer.extend(bytes(reply.readAll()))
        if len(self.buffer)>self.current_limit:self._fail('도시 행사 응답이 크기 한도를 넘었습니다.')

    def _finished(self,reply,token):
        if self.closed or token!=self.generation or reply is not self.reply:
            reply.deleteLater();return
        self.deadline.stop();self._read(reply,token)
        if reply is not self.reply:return
        status=reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        if reply.error()!=QNetworkReply.NetworkError.NoError or status!=200 or not allowed_url(reply.url().toString()):
            self._fail('도시 행사 갱신에 실패했습니다. 마지막 검증 자료를 유지합니다.');return
        payload=bytes(self.buffer);path=self.current_path;self.reply=None;reply.deleteLater()
        try:
            if path=='index.json':
                self.remote_index=validate_index(json.loads(payload.decode('utf-8')));self.index_bytes=payload
                country=next((row for row in self.remote_index['countries'] if row['code']==self.country),None)
                if country is None:raise ValueError('선택 국가 자료가 새 색인에 없습니다.')
                self.queue=list(country['files'])
            else:
                meta=next(item for item in self.remote_index['countries'] if item['code']==self.country)
                entry=next(item for item in meta['files'] if item['path']==path)
                validate_download(payload,entry,self.country);self.payloads[path]=payload
            if self.queue:
                entry=self.queue.pop(0);self._request(entry['path'],entry['bytes'])
            else:self._commit()
        except (OSError,ValueError,KeyError,StopIteration,zlib.error) as exc:
            self._fail('도시 행사 자료 검증 실패: '+str(exc))

    def _commit(self):
        # 검증된 파일을 새 세대에 모두 둔 뒤 한 국가의 활성 포인터만 교체합니다.
        ident=hashlib.sha256(self.index_bytes).hexdigest();root=self.directory/'generations'/ident
        root.mkdir(parents=True,exist_ok=True)
        for path,payload in self.payloads.items():
            target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
            temporary=target.with_suffix(target.suffix+'.tmp');temporary.write_bytes(payload);temporary.replace(target)
        index=root/'index.json';temporary=index.with_suffix('.json.tmp');temporary.write_bytes(self.index_bytes);temporary.replace(index)
        revision=activate_country_cache(self.country,root)
        self.busy=False;self.last_status=dict(status='updated',country_code=self.country,revision=revision,source='owner_github')
        self.changed.emit(revision);self.updated.emit(dict(self.last_status))

    def _timeout(self):
        self._fail('도시 행사 갱신 시간이 초과됐습니다. 이전 자료를 유지합니다.')

    def _fail(self,message):
        self.generation+=1;self.deadline.stop();reply=self.reply;self.reply=None;self.busy=False
        if reply is not None:reply.abort();reply.deleteLater()
        self.last_status=dict(status='failed',country_code=self.country,error=message)
        if not self.closed:self.failed.emit(message)

    def close(self):
        if self.closed:return
        self.closed=True;self.generation+=1;self.deadline.stop();reply=self.reply;self.reply=None;self.busy=False
        if reply is not None:reply.abort();reply.deleteLater()
