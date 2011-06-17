#!/usr/bin/env python

import networkx as nx

from topo.os3e import OS3EGraph
from os3e_weighted import OS3EWeightedGraph
from metrics_lib import availability_one_combo

g = OS3EGraph()
g_w = OS3EWeightedGraph()

link_fail_prob = 0.01

# Try to roughly match the failure probability of links.
distances = [g_w[src][dst]['weight'] for src, dst in g.edges()]
weighted_link_fail_prob = g_w.number_of_edges() / float(sum(distances)) * link_fail_prob

# A link of average length should have equivalent failure probability
# to the input prob.
avg_link_fail_prob = sum(distances) / float(g_w.number_of_edges()) * weighted_link_fail_prob
assert abs(link_fail_prob - avg_link_fail_prob) < 0.000001

apsp = nx.all_pairs_shortest_path_length(g)
apsp_paths = nx.all_pairs_shortest_path(g)

apsp_w = nx.all_pairs_dijkstra_path_length(g_w)
apsp_w_paths = nx.all_pairs_dijkstra_path(g_w)

combos = [["Portland"],
          ["Sunnyvale, CA", "Boston"],
          ["Sunnyvale, CA", "Salt Lake City"],
          ["Seattle", "Boston"],
          ["Seattle", "Portland"]]

# These should be roughly equal, given our construction of weighted link
# failure probability.
for combo in combos:
    print "combo: %s" % combo
    for max_failures in range(1, 4):
        print "\tfailures: %s" % max_failures
        a, c = availability_one_combo(g, combo, apsp, apsp_paths,
            False, link_fail_prob, max_failures)

        a_w, c_w = availability_one_combo(g_w, combo, apsp_w,
            apsp_w_paths, True, weighted_link_fail_prob, max_failures)
        print "\t\tunweighted availability, coverage: %0.6f, %0.6f" % (a, c)
        print "\t\t  weighted availability, coverage: %0.6f, %0.6f" % (a_w, c_w)