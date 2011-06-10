#!/usr/bin/env python
import logging
import unittest

from metrics_lib import fairness


lg = logging.getLogger("test_metrics")

class FairnessTest(unittest.TestCase):

    def test_best(self):
        '''Best case: equal items should have fairness of 1.'''
        cases = [[1, 1, 1], [3, 3, 3, 3]]
        for case in cases:
            self.assertEqual(1, fairness(case))

    def test_worst(self):
        '''Worst case: one nonzero item and the rest zero.'''
        cases = [[1, 0, 0], [3, 0, 0, 0]]
        for case in cases:
            self.assertAlmostEqual(1 / float(len(case)), fairness(case))
    
    def test_mix(self):
        '''Mixed case: should be k/n when k users equally share, 0 others.'''
        cases = [[2, 2, 0], [3, 0, 0, 0], [1, 1, 1, 0]]
        for case in cases:
            lg.debug("considering case: %s" % case)
            nonzeros = len([i for i in case if i != 0])
            exp_fairness = nonzeros / float(len(case))
            self.assertAlmostEqual(exp_fairness, fairness(case))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()