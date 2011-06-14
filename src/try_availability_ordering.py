#!/usr/bin/env python
'''Check if node ordering depends on the depth of failure analysis.

This program tries to answer a specific question:

Is the best node for availability when only considering one maximum failure
necessarily the best node for availability when considering multiple failures?

And is the ordering the same for all nodes?
'''
from itertools import combinations
from operator import itemgetter
import logging

import networkx as nx

from lib.list import compare_lists
import metrics_lib as metrics
from topo.os3e import OS3EGraph
from file_libs import write_csv_file, write_json_file, read_json_file
from os3e_weighted import OS3EWeightedGraph


logging.basicConfig(level=logging.DEBUG)

COMPUTE_START = True
COMPUTE_END = True

NUM_FROM_START = 1
NUM_FROM_END = 0


WEIGHTED = False

# Write all combinations to the output, to be used for distribution for
#  creating CDFs or other vis's later.
WRITE_DIST = True

# Write out only the full distribution?
DIST_ONLY = True

# Additional args to pass to metrics functions.
extra_params = {
    'link_fail_prob': 0.01,
    'max_failures': 2
}

# Write out combinations?
WRITE_COMBOS = True

# Max #  Failures to consider.
MAX_FAILURES = 3

# Metrics to compute
METRICS = ['availability']

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

if WEIGHTED:
    apsp = nx.all_pairs_dijkstra_path_length(g)
    apsp_paths = nx.all_pairs_dijkstra_path(g)
else:
    apsp = nx.all_pairs_shortest_path_length(g)
    apsp_paths = nx.all_pairs_shortest_path(g)

if USE_PRIOR_OPTS:
    data = read_json_file(PRIOR_OPTS_FILENAME)
else:
    all_data = {}  # data, keyed by # failures
    for failures in range(1, MAX_FAILURES + 1):
        # data['data'][num controllers] = [latency:latency, nodes:[best-pos node(s)]]
        # data['metrics'] = [list of metrics included]
        # latency is also equal to 1/closeness centrality.
        all_data[failures] = {}
        extra_params['max_failures'] = failures
        metrics.run_all_combos(METRICS, g, controllers, all_data[failures], apsp,
                           apsp_paths, WEIGHTED, WRITE_DIST, WRITE_COMBOS, extra_params)
    # extract ordering of availability
    extract = {}  # extract[1] = data for 1 failure
    failures = range(1, MAX_FAILURES + 1)
    for j in failures:
        extract[j] = []
        print "getting data for %i failure" % j
        for i, point in enumerate(all_data[j]['data'][str(1)]['distribution']):
            id = point['id']
            combo = point['combo']
            a = point['availability']
            extract[j].append([id, a, combo])
        extract[j] =  sorted(extract[j], key = itemgetter(1), reverse = True)
    for combo in combinations(failures, 2):
        print "comparing %s and %s:" % (combo[0], combo[1])
        left = combo[0]
        right = combo[1]
        for i in range(len(extract[left])):
            print "\t%s %s:%0.6f %s:%0.6f" % (extract[left][i][0], extract[left][i][2], extract[left][i][1], extract[right][i][2], extract[right][i][1])
        print "list similarity: %f" % compare_lists([i[0] for i in extract[left]], [i[0] for i in extract[right]])


