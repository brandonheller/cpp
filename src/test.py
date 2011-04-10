#!/usr/bin/env python
'''Single-source shortest paths regression test.

For common topologies, verify uptime given a link failure probability.
'''
import logging
import networkx as nx
import unittest

import cc


def run_test(test, g, link_fail, node_fail, max_fail, alg, expected):
    output = cc.compute(g, link_fail, node_fail, max_fail, alg)
    test.assertAlmostEqual(output, expected)


class test_SSSP(unittest.TestCase):

    def testTriangle(self):
        g = nx.complete_graph(3)
        # Each line has: link_fail, node_fail, max_fail, expected
        # 3 links can fail.
        # 2/3 of the time it has an effect.
        # when it has an effect, connectivity is 2/3
        # For l = 0.1, that's 2 instances of 2/3 up and 1 of 1.0 up
        # 0.1 * (2 * 2/3 + 1 * 1.0) + 0.7 * 1.0 = 0.9333
        tests = [
            (0.1, 0, 1, 0.933333333333),
            (0.2, 0, 1, 0.866666666666),
        ]
        for link_fail, node_fail, max_fail, exp in tests:
            run_test(self, g, link_fail, node_fail, max_fail, 'sssp', exp)

    def testSquare(self):
        # Square mesh test
        g = nx.complete_graph(4)
        # Each line has: link_fail, node_fail, max_fail, expected
        # 6 links can fail.
        # 3/6 of the time it has an effect.
        # when it has an effect, connectivity is 3/4
        # For l = 0.1, that's 3 instances of 3/4 up and 3 of 1.0 up
        # 0.1 * (3 * 3/4 + 3 * 1.0) + 0.4 * 1.0 = 
        tests = [
            (0.1, 0, 1, 0.925),
            (0.2, 0, 1, 0.85)
        ]
        for link_fail, node_fail, max_fail, exp in tests:
            run_test(self, g, link_fail, node_fail, max_fail, 'sssp', exp)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()





