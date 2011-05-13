#!/usr/bin/env python
import logging
import networkx as nx
import unittest

from cc import compare_lists, permutations_total_diff

lg = logging.getLogger("test_compare")

class CompareListsTests(unittest.TestCase):

    def test_identity(self):
        '''Distance from list to itself should be 0'''
        a = [1, 2, 3]
        b = a
        self.assertEquals(compare_lists(a, b), 0)

    def test_flipped_many(self):
        # totals[i] = expected compare distance for list of that size
        totals = { 1: 0, 
                   2: 2,
                   3: 4,
                   4: 8,
                   5: 12
        }
        for size in range(2, 5):
            a = [i for i in range(size)]
            b = reversed(a)
            self.assertEquals(compare_lists(a, b), totals[size])

    def test_random(self):
        a = [1, 2, 3]
        sum = permutations_total_diff(a)
        lg.debug("sum: %s" % sum)
        self.assertEqual(sum, 16)

    def test_random_larger(self):
        a = [1, 2, 3, 4]
        sum = permutations_total_diff(a)
        lg.debug("sum: %s" % sum)
        self.assertEqual(sum, 120)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()