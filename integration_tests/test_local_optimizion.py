#!/usr/bin/python
"""
Unittest of local optimization of a linac with different optimizers.

Author: Jun Zhu, zhujun981661@gmail.com
"""
import os
import glob
import unittest

from liso import Linac, NelderMead, LinacOptimization

SKIP_SDPEN_TEST = False
try:
    from liso import SDPEN
except ImportError:
    SKIP_SDPEN_TEST = True

test_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'local_optimizer'
))


class TestLocalOptimizer(unittest.TestCase):
    def setUp(self):
        linac = Linac()
        linac.add_beamline('astra',
                           name='gun',
                           fin=os.path.join(test_path, 'injector.in'),
                           template=os.path.join(test_path, 'injector.in.000'),
                           pout='injector.0150.001')

        print(linac)

        self.opt = LinacOptimization(linac)
        self.opt.printout = 1

        self.opt.add_obj('emitx_um', expr='gun.out.emitx', scale=1.e6)
        self.opt.add_var('laser_spot', value=0.1, lb=0.04, ub=0.3)
        self.opt.add_var('main_sole_b', value=0.1, lb=0.0, ub=0.4)

    def tearDown(self):
        for file in glob.glob(os.path.join(test_path, "injector.*.001")):
            os.remove(file)
        try:
            os.remove(os.path.join(test_path, "injector.in"))
        except FileNotFoundError:
            pass

    def test_nelderMead(self):
        optimizer = NelderMead()

        opt_f, opt_x = self.opt.solve(optimizer)
        self.assertAlmostEqual(opt_f, 0.03964, delta=0.0001)
        self.assertAlmostEqual(opt_x[0], 0.04000, delta=0.0001)
        self.assertAlmostEqual(opt_x[1], 0.23000, delta=0.01)

    @unittest.skipIf(SKIP_SDPEN_TEST is True, "Failed to import library")
    def test_sdpen(self):
        optimizer = SDPEN()

        opt_f, opt_x = self.opt.solve(optimizer)
        self.assertAlmostEqual(opt_f, 0.03964, delta=0.0001)
        self.assertAlmostEqual(opt_x[0], 0.04000, delta=0.0001)
        self.assertAlmostEqual(opt_x[1], 0.23000, delta=0.01)


if __name__ == "__main__":
    unittest.main()
