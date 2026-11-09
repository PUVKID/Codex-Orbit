"""접촉시트에서 확인한 찌그러짐과 단면 급회전을 정점으로 재현합니다."""
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from calendar_renderer import _object_geometry
from calendar_catalog import OBJECTS
from calendar_specials import SPECIAL_OBJECTS


class SurfaceContinuityTests(unittest.TestCase):
    def test_heart_keeps_full_width_instead_of_coordinate_view_collapse(self):
        parts=_object_geometry(SPECIAL_OBJECTS['special_valentine'],(.4,.1,.1))
        points=parts[0][0][0][:,:3]
        width,height,depth=np.ptp(points,axis=0)
        self.assertGreater(width/height,.7)
        self.assertLess(width/height,1.4)
        self.assertGreater(depth,10)

    def test_banana_cross_sections_do_not_flip_between_adjacent_points(self):
        parts=_object_geometry(OBJECTS['banana'],(.5,.4,.1))
        vertices=parts[0][0][0]
        normals=vertices[:,3:].reshape(40,20,3)
        adjacent=np.einsum('ijk,ijk->ij',normals[1:],normals[:-1])
        self.assertGreater(float(adjacent.min()),.95)


if __name__=='__main__':unittest.main()
