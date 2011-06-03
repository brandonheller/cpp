#!/usr/bin/env python
'''Compute latency for varying number of controllers and different algorithms.'''

import networkx as nx

import latency_lib as lat
from topo.os3e import OS3EGraph
from file_libs import write_csv_file, write_json_file


COMPUTE_START = True
COMPUTE_END = True

NUM_FROM_START = 4
NUM_FROM_END = 0

FILENAME = ("data_out/os3e_latencies_with_controller_%s_%s" %
           (NUM_FROM_START, NUM_FROM_END))

# Algorithms for computing best-latency controller positions.
# all: explore all possibilities.  exponential blowup in # controllers.
# sequential:  pick the best one, then given that choice, pick the next best.
# best-n: compute closeness centrality, then use that pick the best n node locations.
ALGS = ['all']
#ALGS = ['all', 'sequential', 'best-n']

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

apsp = nx.all_pairs_shortest_path_length(g)

lat.run_optimal_latencies(g, controllers, data, apsp)
lat.run_greedy_informed(data, g, apsp)
lat.run_greedy_alg_dict(data, g, 'greedy-cc', 'latency', nx.closeness_centrality(g), apsp)
lat.run_greedy_alg_dict(data, g, 'greedy-dc', 'latency', nx.degree_centrality(g), apsp)
lat.run_best_n(data, g, apsp, 10)
lat.run_best_n(data, g, apsp, 100)
lat.run_best_n(data, g, apsp, 1000)

print "*******************************************************************"

write_json_file(FILENAME, data)
write_csv_file(FILENAME, data, exclude = ['combo'])
