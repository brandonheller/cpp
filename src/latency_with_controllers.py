#!/usr/bin/env python
'''Compute latency for varying number of controllers and different algorithms.'''

from itertools import combinations
import time

import networkx as nx
import numpy

import cc
from topo.os3e import OS3EGraph
from file_libs import write_csv_file, write_json_file


COMPUTE_START = True
COMPUTE_END = True

NUM_FROM_START = 2
NUM_FROM_END = 1

FILENAME = ("data_out/os3e_latencies_with_controller_%s_%s" %
           (NUM_FROM_START, NUM_FROM_END))

BIG = 10000000

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

def get_total_path_len(g, controllers):
    '''Returns the total of path lengths from nodes to nearest controllers.
    
    @param g: NetworkX graph
    @param controllers: list of controller locations
    @return path_len_total: total of path lengths
    '''
    # path_lengths[node] = path from node to nearest item in combo
    path_lengths = {}
    for n in g.nodes():
        # closest_controller records controller w/shortest distance
        # to the currently-considered node.
        closest_controller = None
        shortest_path_len = BIG
        for c in combo:
            path_len = apsp[n][c]
            if path_len < shortest_path_len:
                closest_controller = c
                shortest_path_len = path_len
        #  pick the best value from that list
        path_lengths[n] = shortest_path_len
    path_len_total = sum(path_lengths.values())
    return path_len_total


for i in sorted(controllers):
    # compute best location(s) for i controllers.

    print "** combo size: %s" % i
    
    data[i] = {}

    best_combo_path_len_total = BIG
    best_combo = None
    worst_combo_path_len_total = -BIG
    worst_combo = None
    start_time = time.time()

    path_len_totals = []  # note all path lengths to compute stats later.

    combos = 0

    # for each combination of i controllers
    for combo in combinations(g.nodes(), i):
        combos += 1

        path_len_total = get_total_path_len(g, combo)

        if path_len_total < best_combo_path_len_total:
            best_combo_path_len_total = path_len_total
            best_combo = combo

        if path_len_total > worst_combo_path_len_total:
            worst_combo_path_len_total = path_len_total
            worst_combo = combo

        path_len_totals.append(path_len_total)

    duration = time.time() - start_time

    best_combo_path_len = best_combo_path_len_total / float(g.number_of_nodes())
    worst_combo_path_len = worst_combo_path_len_total / float(g.number_of_nodes())
    mean_combo_path_len = sum(path_len_totals) / float(combos) / float(g.number_of_nodes())
    median_combo_path_len = numpy.median(path_len_totals) / float(g.number_of_nodes())

    print "\topt"
    print "\t\tbest: %s %s" % (best_combo_path_len, best_combo)
    print "\t\tworst: %s %s" % (worst_combo_path_len, worst_combo)
    print "\t\tmean: %s" % (mean_combo_path_len)
    print "\t\tmedian: %s" % (median_combo_path_len)
    print "\t\tduration: %s" % duration

    data[i] = {
        'opt': {
            'latency': best_combo_path_len,
            'duration': duration,
            'combo': best_combo
        },
        'worst': {
            'latency': worst_combo_path_len,
            'combo': worst_combo
        },
        'random_mean': {
            'latency': mean_combo_path_len,
        },
        'random_median': {
            'latency': median_combo_path_len
        },
    }

print "*******************************************************************"
print data

write_json_file(FILENAME, data)
write_csv_file(FILENAME, data, exclude = ['combo'])
