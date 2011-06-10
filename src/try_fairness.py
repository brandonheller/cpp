#!/usr/bin/env python

import networkx as nx

import metrics_lib as metrics
from topo.os3e import OS3EGraph
from os3e_weighted import OS3EWeightedGraph
g = OS3EWeightedGraph()
apsp = nx.all_pairs_dijkstra_path_length(g)

combos = [["Sunnyvale, CA", "Boston"],
          ["Portland"],
          ["Sunnyvale, CA", "Salt Lake City"],
          ["Seattle", "Boston"],
          ["Seattle", "Portland"]]
for combo in combos:
    print combo, metrics.controller_split_fairness(g, combo, apsp, None), "\n"