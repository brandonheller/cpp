#!/usr/bin/env python
'''Compute latency for varying number of controllers and different algorithms.'''

import networkx as nx

import latency_lib as lat
from topo.os3e import OS3EGraph
from file_libs import write_csv_file, write_json_file, read_json_file
from os3e_weighted import OS3EWeightedGraph

COMPUTE_START = True
COMPUTE_END = True

NUM_FROM_START = 5
NUM_FROM_END = 0

WEIGHTED = True

# Write all combinations to the output, to be used for distribution for
#  creating CDFs or other vis's later.
WRITE_DIST = True

# Write out only the full distribution?
DIST_ONLY = True

USE_PRIOR_OPTS = False

FILENAME = "data_out/os3e_latencies"
if WEIGHTED:
    FILENAME += "_weighted"
else:
    FILENAME += "_unweighted"
    PRIOR_OPTS_FILENAME = "data_out/os3e_latencies_unweighted_9_9.json"
FILENAME += "_%s_%s" % (NUM_FROM_START, NUM_FROM_END)

if WEIGHTED:
    g = OS3EWeightedGraph()
else:
    g = OS3EGraph()

# Controller numbers to compute data for.
controllers = []

# Eventually expand this to n.
if COMPUTE_START:
    controllers += range(1, NUM_FROM_START + 1)

if COMPUTE_END:
    controllers += (range(g.number_of_nodes() - NUM_FROM_END + 1, g.number_of_nodes() + 1))

# data[num controllers] = [latency:latency, nodes:[best-pos node(s)]]
# latency is also equal to 1/closeness centrality.
data = {}

if WEIGHTED:
    apsp = nx.all_pairs_dijkstra_path_length(g)
else:
    apsp = nx.all_pairs_shortest_path_length(g)

if USE_PRIOR_OPTS:
    data = read_json_file(PRIOR_OPTS_FILENAME)
else:
    lat.run_optimal_latencies(g, controllers, data, apsp, WEIGHTED, WRITE_DIST)

if not DIST_ONLY:
    lat.run_greedy_informed(data, g, apsp, WEIGHTED)
    lat.run_greedy_alg_dict(data, g, 'greedy-cc', 'latency', nx.closeness_centrality(g, weighted_edges = WEIGHTED), apsp, WEIGHTED)
    lat.run_greedy_alg_dict(data, g, 'greedy-dc', 'latency', nx.degree_centrality(g), apsp, WEIGHTED)
    for i in [10, 100, 1000]:
        lat.run_best_n(data, g, apsp, i, WEIGHTED)
        lat.run_worst_n(data, g, apsp, i, WEIGHTED)

print "*******************************************************************"

# Ignore the actual combinations in CSV outputs as well as single points.
exclude = ["combo", "distribution"]

write_json_file(FILENAME + '.json', data)
write_csv_file(FILENAME, data, exclude = exclude)
