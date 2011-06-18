#!/usr/bin/env python
'''Validate shortest-paths algorithms.'''

import logging
import unittest

from lib.graph import vertex_disjoint, edge_disjoint, interlacing_edges


lg = logging.getLogger("test_graph")

class DisjointnessTest(unittest.TestCase):

    def test_vertex_disjoint(self):
        '''Test vertex disjointness function for correctness.'''
        a = [1, 2, 3, 4]
        b = [2, 3, 4]
        b2 = [1, 5, 6, 4]
        self.assertFalse(vertex_disjoint([a, a]))
        self.assertFalse(vertex_disjoint([a, b]))
        # Chop shared ends off.
        self.assertTrue(vertex_disjoint([a[1:-1], b2[1:-1]]))

    def test_edge_disjoint(self):
        '''Test edge disjointness function for correctness.'''
        a = [1, 2, 3, 4, 5]
        b = [1, 6, 3, 7, 5]
        b2 = [1, 6, 7, 8, 5]
        self.assertFalse(edge_disjoint([a, a]))
        self.assertTrue(edge_disjoint([a, b]))
        self.assertTrue(edge_disjoint([a, b2]))


class InterlacingTest(unittest.TestCase):

    def test_interlacing_edges(self):
        '''Test interlacing edge function for correctness.'''
        a = [i for i in 'ABCDEFZ']
        b = [i for i in 'AGCBIZ']
        a2 = [1, 2, 3]
        a3 = [1, 2]
        tuples = [
            (a, b, [('C', 'B')]),
            (a2, a2, [(1, 2), (2, 3)]),
            (a2, a3, [(1, 2)])
        ]
        for x, y, result in tuples:
            self.assertEqual(interlacing_edges(x, y), result)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
