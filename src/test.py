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
        g = nx.complete_graph(n)
        exp_uptime = self.calc_complete_uptime(n, link_fail)
        node_fail = 0
        # if hard-coded "test bootstrap uptime" defined, verify w/eqn.
        if hard_coded_uptime:
            self.assertAlmostEqual(exp_uptime, hard_coded_uptime)
        run_test(self, g, link_fail, node_fail, max_fail, 'sssp', exp_uptime)

    def test_link_complete_triangle_onefail(self):
        # 3 links can fail.
        # 2/3 of the time it has an effect.
        # when it has an effect, connectivity is 2/3
        # For l = 0.1, that's 2 instances of 2/3 up and 1 of 1.0 up
        # 0.1 * (2 * 2/3 + 1 * 1.0) + 0.7 * 1.0 = 0.9333
        hard_coded_uptimes = {
            0.1: 0.933333333333,
            0.2: 0.866666666666
        }
        for link_fail, uptime in hard_coded_uptimes.iteritems():
            self.run_complete_test(3, link_fail, 0, 1, uptime)

    def test_link_complete_quad_onefail(self):
        # 6 links can fail.
        # 3/6 of the time it has an effect.
        # when it has an effect, connectivity is 3/4
        # For l = 0.1, that's 3 instances of 3/4 up and 3 of 1.0 up
        # 0.1 * (3 * 3/4 + 3 * 1.0) + 0.4 * 1.0 = 
        hard_coded_uptimes = {
            0.1: 0.925,
            0.2: 0.85
        }
        for link_fail, uptime in hard_coded_uptimes.iteritems():
            self.run_complete_test(4, link_fail, 0, 1, uptime)

    def test_link_complete_various_onefail(self):
        for n in range(3, 10):
            for link_fail in (0.01, 0.02):
                self.run_complete_test(n, link_fail, 0, 1)

    def calc_star_uptime(self, n, link_fail):
        '''Calc star uptime.

        NOTE: n is the number of nodes.'''
        # Correct for NetworkX, which adds one to n.
        g = nx.star_graph(n - 1)
        # Node 0 is the center of the star.
        edges = g.number_of_edges()
        nodes = g.number_of_nodes()
        paths = nx.single_source_shortest_path(g, g.nodes()[1])
        used = flatten(paths)
        sssp_edges = used.number_of_edges()
        if sssp_edges != g.number_of_edges():
            raise Exception("edge not on sssp for star graph")

        # consider those times when a link failed:
        # first, consider failure on outside of graph
        exp_uptime_outer = link_fail * edges * ((float(edges - 1) / edges) * float(edges) / nodes + \
                                                (float(1) / edges) * float(1) / nodes)
        exp_uptime_outer += (1.0 - (link_fail * sssp_edges)) * 1.0

        # consider only the hub as a controller:
        exp_uptime_inner = link_fail * edges * ((float(edges) / edges) * float(edges) / nodes)
        exp_uptime_inner += (1.0 - (link_fail * edges)) * 1.0

        # merge:
        exp_uptime_weighted = float(edges * exp_uptime_outer + 1 * exp_uptime_inner) / nodes
        return exp_uptime_weighted

    def run_star_test(self, n, link_fail, node_fail, max_fail, hard_coded_uptime = None):
        # Return the Star graph with n nodes
        g = nx.star_graph(n - 1)
        exp_uptime = self.calc_star_uptime(n, link_fail)
        node_fail = 0
        # if hard-coded "test bootstrap uptime" defined, verify w/eqn.
        if hard_coded_uptime:
            self.assertAlmostEqual(exp_uptime, hard_coded_uptime)
        run_test(self, g, link_fail, node_fail, max_fail, 'sssp', exp_uptime)

    def test_link_star_4_onefail(self):
        # When controller is along edge (3/4 of the time):
        #     3 links can fail.
        #     3/3 of the time it has an effect.
        #     2/3 of the time the effect is to disconnect one switch (3/4 conn). 
        #     1/3 of the time the effect is to disconnect all but one (1/4 conn).
        # When controller is in center (1/4 of the time):
        #     3 links can fail.
        #     3/3 of the time it has an effect.
        #     3/3 of the time the effect is to disconnect one switch (3/4 conn).
        # For l = 0.1, get weight avg of both controller possibilities:
        # Along edge:
        #     (0.1 * 3 * (2.0/3 * 3.0/4 + 1.0/3 * 1.0/4)) + (1 - (0.1 * 3)) * 1.0 = 0.875
        # In center:
        #     0.1 * 3 * (3.0/3 * 3.0/4) + (1 - (0.1 * 3)) * 1.0 = 0.925
        # (3 * (along_edge) + 1 * (in_center)) / 4  = .8875
        hard_coded_uptimes = {
            0.1: .8875,
        }
        for link_fail, uptime in hard_coded_uptimes.iteritems():
            self.run_star_test(4, link_fail, 0, 1, uptime)

#    def test_link_star_various_onefail(self):
#        for n in range(3, 8):
#            for link_fail in (0.01, 0.02):
#                self.run_star_test(n, link_fail, 0, 1)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()





