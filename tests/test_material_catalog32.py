"""종별 재질의 원본 순서·실제 타일 경계·국소 좌표를 검사합니다."""
from datetime import date
from pathlib import Path
import sys
import unittest
import numpy as np
from PySide6.QtGui import QImage,QColor

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from material_catalog32 import TILE_ORDER,tile_rectangle,extract_tile,load_catalog
from calendar_art import design_for_date
from calendar_renderer import build_geometry


class MaterialCatalogTests(unittest.TestCase):
    def test_original_93_ids_and_actual_nondivisible_tile_edges(self):
        ids=[key for keys in TILE_ORDER.values() for key in keys]
        self.assertEqual(len(ids),93);self.assertEqual(len(set(ids)),93)
        for index in range(31):
            x,y,w,h=tile_rectangle(1774,887,index)
            self.assertGreaterEqual(min(w,h),221)
            self.assertLessEqual(x+w,1774);self.assertLessEqual(y+h,887)
            if index%8<7 and index<30:self.assertEqual(x+w,tile_rectangle(1774,887,index+1)[0])
            if index==30:self.assertEqual(x+w,round(7*1774/8))
        with self.assertRaises(ValueError):tile_rectangle(1774,887,31)

    def test_only_three_reviewed_berry_tiles_use_supplement(self):
        catalog=load_catalog(Path(__file__).resolve().parents[1]/'assets/materials')
        chosen={key for key,row in catalog.items() if row['path'].name=='열매_베리3종_과피_보강지도.png'}
        self.assertEqual(chosen,{'raspberry','blackberry','blueberry'})
        self.assertEqual([catalog[key]['index'] for key in ('raspberry','blackberry','blueberry')],[15,16,17])
        self.assertTrue(all(catalog[key]['enabled'] for key in chosen))
        self.assertEqual(sum(row['enabled'] for row in catalog.values()),88)
        for key in ('pineapple','melon','dragonfruit','coconut','fern'):
            self.assertFalse(catalog[key]['enabled'])

    def test_memory_crop_keeps_neighbor_colors_out(self):
        image=QImage(1774,887,QImage.Format.Format_RGBA8888);image.fill(QColor('blue'))
        x,y,w,h=tile_rectangle(1774,887,8)
        for row in range(y,y+h):
            for col in range(x,x+w):image.setPixelColor(col,row,QColor('red'))
        tile=extract_tile(image,8)
        self.assertEqual(tile.size().width(),w)
        for point in ((0,0),(w-1,0),(0,h-1),(w-1,h-1)):
            self.assertEqual(tile.pixelColor(*point),QColor('red'))
        self.assertEqual(image.pixelColor(x+w,y),QColor('blue'))

    def test_material_coordinates_follow_geometry_without_changing_normals(self):
        metadata=[];parts=build_geometry(design_for_date(date(2026,11,27)),metadata)
        self.assertEqual(len(parts),len(metadata))
        self.assertTrue(any(row['enabled'] for row in metadata))
        self.assertTrue(any(not row['enabled'] for row in metadata))
        for ((vertices,_),*_),row in zip(parts,metadata):
            local=np.c_[vertices[:,:3],np.ones(len(vertices))]@row['mapping'].T
            self.assertTrue(np.isfinite(local).all())
            self.assertGreaterEqual(float(local[:,:3].min()),-1e-4)
            self.assertLessEqual(float(local[:,:3].max()),1.0001)
            np.testing.assert_allclose(np.linalg.norm(vertices[:,3:],axis=1),1,atol=2e-5)


if __name__=='__main__':unittest.main()
