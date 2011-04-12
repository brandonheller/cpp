#!/usr/bin/env python
'''Single-source shortest paths regression test.

For common topologies, verify uptime given a link failure probability.
'''
import logging
import networkx as nx
import unittest

from cc import flatten, compute

def run_test(test, g, link_fail, node_fail, max_fail, alg, expected):
    output = compute(g, link_fail, node_fail, max_fail, alg)
    test.assertAlmostEqual(output, expected)


class test_SSSP(unittest.TestCase):

    def calc_complete_uptime(self, n, link_fail):
        g = nx.complete_graph(n)
        # edges in a complete graph:
        edges = n * (n - 1) / 2
        if edges != g.number_of_edges():
            raise Exception("fix number of edges for complete graphs")
        paths = nx.single_source_shortest_path(g, g.nodes()[0])
        used = flatten(paths)
        sssp_edges = used.number_of_edges()
        nodes = g.number_of_nodes()
        # consider those times when a link failed
        exp_uptime = link_fail * (sssp_edges * (float(sssp_edges) / nodes) + (edges - sssp_edges) * 1.0)
        # consider no-failures case
        exp_uptime += (1.0 - (link_fail * edges)) * 1.0
        return exp_uptime

    def run_complete_test(self, n, link_fail, node_fail, max_fail, hard_coded_uptime = None):
        g = nx.complete_graph(3)
        exp_uptime = self.calc_complete_uptime(3, link_fail)
        node_fail = 0
        # if hard-coded "test bootstrap uptime" defined, verify w/eqn.
        if hard_coded_uptime:
            self.assertAlmostEqual(exp_uptime, hard_coded_uptime)
        run_test(self, g, link_fail, node_fail, max_fail, 'sssp', exp_uptime)

    def test_link_complete_triangle_onefail(self):
        # Each line has: link_fail, node_fail, max_fail, expected
        # 3 links can fail.
        # 2/3 of the time it has an effect.
        # when it has an effect, connectivity is 2/3
        # For l = 0.1, that's 2 instances of 2/3 up and 1 of 1.0 up
        # 0.1 * (2 * 2/3 + 1 * 1.0) + 0.7 * 1.0 = 0.9333
        hard_coded_uptimes = {
            0.1: 0.933333333333,
            0.2: 0.866666666666
        }
        for link_fail in (0.1, 0.2):
            self.run_complete_test(3, link_fail, 0, 1, hard_coded_uptimes[link_fail])

    def test_link_complete_quad_onefail(self):
        # Each line has: link_fail, node_fail, max_fail, expected
        # 6 links can fail.
        # 3/6 of the time it has an effect.
        # when it has an effect, connectivity is 3/4
        # For l = 0.1, that's 3 instances of 3/4 up and 3 of 1.0 up
        # 0.1 * (3 * 3/4 + 3 * 1.0) + 0.4 * 1.0 = 
        hard_coded_uptimes = {
            0.1: 0.933333333333,
            0.2: 0.866666666666
        }
        for link_fail in (0.1, 0.2):
            self.run_complete_test(4, link_fail, 0, 1, hard_coded_uptimes[link_fail])

    def test_link_complete_various_onefail(self):
        for n in range(3, 10):
            for link_fail in (0.01, 0.02):
                self.run_complete_test(n, link_fail, 0, 1)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()





