"""주소·장소 검색의 검증·속도·캐시·늦은 응답 경계를 실제 네트워크 없이 검사합니다."""
import os,sys,json,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs,urlparse
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtCore import QObject,Signal
from PySide6.QtWidgets import QApplication
from PySide6.QtNetwork import QNetworkReply
from weather import PlaceSearchClient,WeatherClient,parse_place_results,normalize_city
PAYLOAD={'features':[{'geometry':{'type':'Point','coordinates':[13.4,52.5]},'properties':{'name':'Example Museum','countrycode':'DE','country':'Germany','state':'Berlin','city':'Berlin','street':'Example Street','housenumber':'3','postcode':'10000'}}]}
class Reply(QObject):
 downloadProgress=Signal(int,int);finished=Signal()
 def __init__(self,raw=b'{}'):super().__init__();self.raw=raw;self.aborted=False
 def read(self,n):return self.raw[:n]
 def error(self):return QNetworkReply.NetworkError.NoError
 def setReadBufferSize(self,n):self.limit=n
 def abort(self):self.aborted=True
 def deleteLater(self):pass
class PlaceSearchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
 def setUp(self):
  old=PlaceSearchClient._last_request_at;PlaceSearchClient._last_request_at=0;self.addCleanup(setattr,PlaceSearchClient,'_last_request_at',old)
 def create(self):
  c=PlaceSearchClient();self.addCleanup(c.close);rows=[];failures=[];c.results.connect(rows.append);c.failed.connect(failures.append);return c,rows,failures
 def test_verified_point_address_and_country_are_not_guessed(self):
  rows=parse_place_results(PAYLOAD);self.assertEqual(rows[0]['latitude'],52.5);self.assertEqual(rows[0]['longitude'],13.4);self.assertEqual(rows[0]['country_code'],'DE');self.assertEqual(rows[0]['address']['house_number'],'3');self.assertIn('Example Street',rows[0]['display_name'])
 def test_invalid_points_country_missing_and_oversize_lists(self):
  for coordinates in ([True,52],[float('nan'),52],[181,52],['13',52]):
   value=json.loads(json.dumps(PAYLOAD));value['features'][0]['geometry']['coordinates']=coordinates;self.assertEqual(parse_place_results(value),[])
  value=json.loads(json.dumps(PAYLOAD));value['features'][0]['properties'].pop('countrycode');self.assertEqual(parse_place_results(value),[])
  with self.assertRaises(ValueError):parse_place_results({'features':PAYLOAD['features']*11})
 def test_explicit_search_url_encodes_input_and_country(self):
  c,_,_=self.create();c.set_country('KR');q=parse_qs(urlparse(c._search_url('수원 & 길')).query)
  self.assertEqual(q['q'],['수원 & 길']);self.assertEqual(q['countrycode'],['KR']);self.assertEqual(q['limit'],['5']);self.assertEqual(q['lang'],['ko'])
 def test_global_throttle_across_clients_and_no_automatic_search(self):
  c,rows,failures=self.create();d,_,other=self.create();reply=Reply()
  with patch.object(c.manager,'get',return_value=reply) as get,patch('weather.time.monotonic',side_effect=[100,100.1]):
   self.assertEqual(get.call_count,0);self.assertTrue(c.search('Berlin'));self.assertFalse(d.search('Paris'));self.assertEqual(get.call_count,1);self.assertEqual(len(other),1)
 def test_cached_rows_are_defensive_and_no_network_repeat(self):
  c,rows,_=self.create();key=('Berlin','ko',None);c._pending_key=key;result=c._parse_response(PAYLOAD);result[0]['address']['city']='changed'
  with patch.object(c.manager,'get') as get:self.assertTrue(c.search('Berlin'));self.assertEqual(get.call_count,0)
  self.assertEqual(rows[0][0]['address']['city'],'Berlin')
 def test_malformed_oversize_and_late_replies_do_not_publish(self):
  for raw in (b'{broken',b'x'*65537):
   c,rows,failed=self.create();reply=Reply(raw);c.reply=reply;c._finish(reply);self.assertEqual(rows,[]);self.assertEqual(len(failed),1)
  c,rows,_=self.create();reply=Reply(json.dumps(PAYLOAD).encode());c.reply=reply;c.close();c._finish(reply);self.assertEqual(rows,[]);self.assertTrue(reply.aborted)
 def test_only_selected_address_fields_are_stored(self):
  value=parse_place_results(PAYLOAD)[0];value['ip']='not public';value['address']['private']='not public';clean=normalize_city(value);self.assertNotIn('ip',clean);self.assertNotIn('private',clean['address'])
 def test_returned_locality_and_postcode_are_visible_without_invented_address(self):
  value=json.loads(json.dumps(PAYLOAD));value['features'][0]['properties']['locality']='Example District'
  row=parse_place_results(value)[0];self.assertIn('Example District',row['display_name']);self.assertIn('10000',row['display_name'])
  self.assertEqual(row['address']['neighbourhood'],'Example District')
 def test_place_without_address_fields_keeps_correct_provider(self):
  value={'features':[{'geometry':{'type':'Point','coordinates':[13.4,52.5]},'properties':{'name':'Example Place','countrycode':'DE'}}]}
  row=parse_place_results(value)[0];c=WeatherClient(location_override=row);self.addCleanup(c.close)
  self.assertIn('Photon',c.snapshot['region_source']);self.assertNotIn('GeoNames',c.snapshot['region_source'])
if __name__=='__main__':unittest.main()
