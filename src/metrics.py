#!/usr/bin/env python
'''Compute metrics for varying number of controllers w/ different algorithms.'''
import logging
import time

import networkx as nx

import metrics_lib as metrics
from topo.os3e import OS3EGraph
from file_libs import write_csv_file, write_json_file, read_json_file
from os3e_weighted import OS3EWeightedGraph

logging.basicConfig(level=logging.DEBUG)

COMPUTE_START = True
COMPUTE_END = True

NUM_FROM_START = 3
NUM_FROM_END = 0


WEIGHTED = False

# Write all combinations to the output, to be used for distribution for
#  creating CDFs or other vis's later.
WRITE_DIST = True

# Write stuff at all?
WRITE = False

# Write out only the full distribution?
DIST_ONLY = True

# Additional args to pass to metrics functions.
EXTRA_PARAMS = {
    'link_fail_prob': 0.01,
    'max_failures': 2
}

# Write out combinations?
WRITE_COMBOS = False


# Metrics to compute
#METRICS = metrics.METRICS
METRICS = ['availability', 'latency']

# Pull in previously computed data, rather than recompute?
USE_PRIOR_OPTS = False

FILENAME = "data_out/os3e_"
if WEIGHTED:
    FILENAME += "weighted"
else:
    FILENAME += "unweighted"
    PRIOR_OPTS_FILENAME = "data_out/os3e_unweighted_9_9.json"
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

# data['data'][num controllers] = [latency:latency, nodes:[best-pos node(s)]]
# data['metrics'] = [list of metrics included]
# latency is also equal to 1/closeness centrality.
data = {}

if WEIGHTED:
    apsp = nx.all_pairs_dijkstra_path_length(g)
    apsp_paths = nx.all_pairs_dijkstra_path(g)
else:
    apsp = nx.all_pairs_shortest_path_length(g)
    apsp_paths = nx.all_pairs_shortest_path(g)

if USE_PRIOR_OPTS:
    data = read_json_file(PRIOR_OPTS_FILENAME)
else:
    start = time.time()
    metrics.run_all_combos(METRICS, g, controllers, data, apsp,
                           apsp_paths, WEIGHTED, WRITE_DIST, WRITE_COMBOS, EXTRA_PARAMS)
    total_duration = time.time() - start
    print "%0.6f" % total_duration

if not DIST_ONLY:
    metrics.run_greedy_informed(data, g, apsp, WEIGHTED)
    metrics.run_greedy_alg_dict(data, g, 'greedy-cc', 'latency', nx.closeness_centrality(g, weighted_edges = WEIGHTED), apsp, WEIGHTED)
    metrics.run_greedy_alg_dict(data, g, 'greedy-dc', 'latency', nx.degree_centrality(g), apsp, WEIGHTED)
    for i in [10, 100, 1000]:
        metrics.run_best_n(data, g, apsp, i, WEIGHTED)
        metrics.run_worst_n(data, g, apsp, i, WEIGHTED)

print "*******************************************************************"

# Ignore the actual combinations in CSV outputs as well as single points.
exclude = ["combo", "distribution", "metric", "group"]

if WRITE:
    write_json_file(FILENAME + '.json', data)
    write_csv_file(FILENAME, data["data"], exclude = exclude)
