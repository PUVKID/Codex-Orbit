"""잎의 종별 외곽·천공과 꽃잎의 실제 깊이를 검사합니다."""
import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from botanical_surface import leaf_surface
from fruit_surface import petal_mesh


class BotanicalSurfaceTests(unittest.TestCase):
    def test_monstera_holes_are_open_through_both_surfaces(self):
        vertices,indices=leaf_surface('monstera',23,31)
        triangles=vertices[indices.reshape(-1,3),:2]
        for side in (-1,1):
            for y in (-10.,1.,12.):
                point=np.array((side*23*.44,y))
                a=triangles[:,0];u=triangles[:,1]-a;v=triangles[:,2]-a;q=point-a
                determinant=u[:,0]*v[:,1]-u[:,1]*v[:,0]
                valid=np.abs(determinant)>1e-7
                determinant=np.where(valid,determinant,1)
                b=(q[:,0]*v[:,1]-q[:,1]*v[:,0])/determinant
                c=(u[:,0]*q[:,1]-u[:,1]*q[:,0])/determinant
                self.assertFalse(np.any(valid&(b>=0)&(c>=0)&(b+c<=1)))

    def test_maple_tips_and_ginkgo_center_split_have_distinct_outline(self):
        maple,_=leaf_surface('maple',9,25)
        edge=maple[32*160:33*160,:2]
        radii=np.linalg.norm(edge,axis=1)
        self.assertGreater(float(radii.max()/radii.min()),2.5)
        ginkgo,_=leaf_surface('ginkgo',22,25)
        edge=ginkgo[32*160:33*160,:2]
        self.assertGreater(float(edge[:,0].ptp()) if hasattr(edge[:,0],'ptp') else float(np.ptp(edge[:,0])),40)
        self.assertLess(float(edge[80,1]),float(edge[65,1])-2)

    def test_petals_have_curved_front_and_back_with_finite_unit_normals(self):
        vertices,indices=petal_mesh(9,13)
        self.assertGreater(float(np.ptp(vertices[:,2])),3)
        self.assertTrue(np.isfinite(vertices).all())
        np.testing.assert_allclose(np.linalg.norm(vertices[:,3:],axis=1),1,atol=2e-5)
        self.assertGreater(len(indices),5000)


if __name__=='__main__':unittest.main()
