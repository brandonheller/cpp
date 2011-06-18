#!/usr/bin/env python
'''Validate shortest-paths algorithms.'''

import logging
import unittest

import networkx as nx

from lib.graph import set_unit_weights, nx_graph_from_tuples
from topo.os3e import OS3EGraph
from os3e_weighted import OS3EWeightedGraph
from paths import BFS


lg = logging.getLogger("test_paths")


# Figure 2.1, pg 23
graph_fig_2_1 = nx_graph_from_tuples([
    ('A', 'B', 1),
    ('A', 'C', 3),
    ('A', 'D', 5),
    ('B', 'C', 1),
    ('B', 'Z', 3),
    ('C', 'D', 2),
    ('C', 'Z', 1),
    ('D', 'E', 2),
    ('D', 'Z', 4),
    ('E', 'Z', 2)
])


# Figure 2.3, pg 27
graph_fig_2_3 = nx_graph_from_tuples([
    ('A', 'B', 5),
    ('A', 'D', 7),
    ('B', 'C', 1),
    ('B', 'Z', 8),
    ('D', 'E', 2),
    ('D', 'Z', 6)
],
[
    ('C', 'A', -1),
    ('E', 'C', -6),
    ('Z', 'E', -2)
])


class TestBFS(unittest.TestCase):

    def test_line(self):
        '''Check shortest path for line graph.'''
        # Return the line graph with n nodes, lowest-num node is 0
        for i in range(2, 4):
            g = nx.path_graph(i)
            set_unit_weights(g)
            path = BFS(g, 0, i - 1)
            self.assertTrue(path)
            self.assertEqual(path[0], 0)
            self.assertEqual(path[-1], i - 1)

    def test_example_2_5(self):
        '''Example 2.5 on pg. 34.'''
        path = BFS(graph_fig_2_1, 'A', 'Z')
        self.assertEqual(path, [i for i in 'ABCZ'])

    def test_example_2_6(self):
        '''Example 2.6 on pg. 35.'''
        def pathlen(g, path):
            pathlen = 0
            for i, n in enumerate(path):
                if i != len(path) - 1:
                    pathlen += g[n][path[i+1]]['weight']
            return pathlen

        g = graph_fig_2_3
        path = BFS(g, 'A', 'Z')
        self.assertEqual(path, [i for i in 'ADECBZ'])
        self.assertEqual(pathlen(g, path), 12)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
