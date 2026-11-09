"""실제 자연물 메시·표면 자산·GPU 투명 모션·자원 해제를 검사합니다."""
from datetime import date
from pathlib import Path
import hashlib
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from calendar_art import design_for_date
from calendar_catalog import OBJECTS
from calendar_renderer import CalendarRenderer, _object_geometry, build_geometry


class FruitSurfaceTests(unittest.TestCase):
    def test_today_and_other_fruit_mapping_is_preserved(self):
        for day,key in ((10,'coconut'),(13,'pear'),(25,'orange'),(27,'apple')):
            self.assertEqual(design_for_date(date(2026,11,day)).object_id,key)

    def test_coconut_has_fibrous_shell_and_three_dark_eyes(self):
        parts=_object_geometry(OBJECTS['coconut'],(.2,.1,.04))
        dark=[part for part in parts if part[1][0]<.02]
        self.assertEqual(len(dark),3)
        self.assertGreater(len(parts[0][0][0]),3000)
        self.assertGreater(len(parts[-1][0][0]),500)
        for part in parts:
            self.assertEqual(part[2],0.)
            self.assertGreaterEqual(part[3],.8)

    def test_daily_geometry_is_not_a_flat_picture(self):
        for day in (10,13,25,27):
            parts=build_geometry(design_for_date(date(2026,11,day)))
            points=np.concatenate([part[0][0][:,:3] for part in parts])
            self.assertGreater(float(np.ptp(points[:,2])),35)
            self.assertGreater(float(np.ptp(points[:,0])),35)

    def test_actual_generated_shell_asset_is_present(self):
        path=Path(__file__).resolve().parents[1]/'assets/materials/코코넛_껍질_섬유.png'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),'d1474f389e491f9e5cdbd21380aebaae1cd207b50b03ec91845c52b3ce4e8898')
        for name,digest in (
            ('과피_미세결_높이맵.png','01b12d11f1ded88158e5f12ff59884ac5c9758b440b1b5e95f16475cd9979701'),
            ('식물_미세결_높이맵.png','22720cba1371be521336c073949f27b9f135ee4f27a4f26c316c824b87fc4690'),
        ):
            self.assertEqual(hashlib.sha256(path.with_name(name).read_bytes()).hexdigest(),digest)

    def test_species_texture_switches_remain_bounded_and_close(self):
        from calendar_art import all_designs
        keys={'raspberry','blackberry','blueberry','apple','rose','maple'}
        dates={}
        for design in all_designs():
            if design.object_id in keys:dates.setdefault(design.object_id,design.date)
            if len(dates)==len(keys):break
        renderer=CalendarRenderer(128)
        try:
            baseline=len(renderer.resources)
            for _ in range(2):
                for key,value in dates.items():
                    frame=renderer.render(value,0)
                    self.assertFalse(frame.isNull())
                    self.assertEqual(renderer.species_key,key)
                    self.assertIsNotNone(renderer.species_texture)
                    self.assertEqual(len(renderer.resources),baseline+1)
                    self.assertEqual(renderer.resources.count(renderer.species_texture),1)
        finally:renderer.close()
        self.assertIsNone(renderer.ctx)
        self.assertIsNone(renderer.species_texture)
        self.assertIsNone(renderer.atlas_image)
        self.assertEqual(renderer.resources,[])

    def test_gpu_transparency_motion_resize_date_switch_and_close(self):
        renderer=CalendarRenderer(192)
        try:
            value=date(2026,11,10)
            first=renderer.render(value,0);later=renderer.render(value,2)
            self.assertEqual(first.pixelColor(0,0).alpha(),0)
            self.assertGreater(first.pixelColor(96,96).alpha(),240)
            self.assertNotEqual(bytes(first.constBits()),bytes(later.constBits()))
            repeat=renderer.render(value,0)
            self.assertEqual(bytes(first.constBits()),bytes(repeat.constBits()))
            renderer.set_output_size(256)
            switched=renderer.render(date(2026,11,27),0)
            self.assertEqual(switched.size().toTuple(),(256,256))
            self.assertEqual(renderer.design.object_id,'apple')
            self.assertEqual(len(renderer.vaos),len(renderer.parts))
            self.assertEqual(len(renderer.buffers),len(renderer.parts)*2)
            korean=renderer.render(date(2026,10,9),0,country='KR')
            self.assertEqual(renderer.design.object_id,'special_hangul')
            other=renderer.render(date(2026,10,9),0,country='US')
            self.assertIn(renderer.design.object_id,OBJECTS)
            self.assertNotEqual(bytes(korean.constBits()),bytes(other.constBits()))
        finally:renderer.close()
        self.assertIsNone(renderer.ctx)
        self.assertEqual(renderer.resources,[])
        self.assertEqual(renderer.buffers,[])


if __name__=='__main__':unittest.main()
