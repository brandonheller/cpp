#!/usr/bin/env python
'''Compute metrics for varying number of controllers w/ different algorithms.

The data schema looks something like this:

data['data'][num controllers] = [latency:latency, nodes:[best-pos node(s)]]
data['metrics'] = [list of metrics data]
data['group'] = [list of controllers]

'''
import logging
import os
import time

import networkx as nx

from file_libs import write_csv_file, write_json_file, read_json_file
from file_libs import write_dist_csv_file
import metrics_lib as metrics
from topo_lib import get_topo_graph
from lib.options import parse_args

logging.basicConfig(level=logging.DEBUG)


def get_controllers(g, options):
    controllers = []
    if options.controllers:
        controllers = options.controllers
    else:
        # Controller numbers to compute data for.
        controllers = []
    
        # Eventually expand this to n.
        if options.compute_start:
            controllers += range(1, options.from_start + 1)
        
        if options.compute_end:
            controllers += (range(g.number_of_nodes() - options.from_end + 1, g.number_of_nodes() + 1))
    return controllers


def get_filename(topo, options, controllers):
    filename = "data_out/" + topo + "/"
    if options.controller_list:
        for c in controllers:
            filename += "%s" % c
    else:
        filename += "%s_to_%s" % (options.from_start, options.from_end)
    return filename


def get_extra_params(g):
    # Additional args to pass to metrics functions.
    extra_params = {
        'link_fail_prob': 0.01,
        'max_failures': 2
    }

    # Try to roughly match the failure probability of links.
    link_fail_prob = extra_params['link_fail_prob']
    distances = [g[src][dst]['weight'] for src, dst in g.edges()]
    weighted_link_fail_prob = g.number_of_edges() / float(sum(distances)) * link_fail_prob
    extra_params['link_fail_prob'] = weighted_link_fail_prob
    return extra_params


def do_metrics(options, topo, g):
    '''Compute the metrics for a single topology.'''

    print "computing metricss for topo: %s" % topo
    controllers = get_controllers(g, options)
    filename = get_filename(topo, options, controllers)

    data = {}  # See top for data schema details.
    apsp = nx.all_pairs_dijkstra_path_length(g)
    apsp_paths = nx.all_pairs_dijkstra_path(g)

    extra_params = get_extra_params(g)
    if options.use_prior:
        data = read_json_file(filename)
    else:
        start = time.time()
        weighted = True
        metrics.run_all_combos(options.metrics, g, controllers, data, apsp,
                               apsp_paths, weighted, options.write_dist,
                               options.write_combos, extra_params, options.processes,
                               options.multiprocess, options.chunksize, options.median)
        total_duration = time.time() - start
        print "%0.6f" % total_duration

    if not options.dist_only:
        metrics.run_greedy_informed(data, g, apsp, options.weighted)
        metrics.run_greedy_alg_dict(data, g, 'greedy-cc', 'latency', nx.closeness_centrality(g, weighted_edges = options.weighted), apsp, options.weighted)
        metrics.run_greedy_alg_dict(data, g, 'greedy-dc', 'latency', nx.degree_centrality(g), apsp, options.weighted)
        for i in [10, 100, 1000]:
            metrics.run_best_n(data, g, apsp, i, options.weighted)
            metrics.run_worst_n(data, g, apsp, i, options.weighted)

    print "*******************************************************************"

    # Ignore the actual combinations in CSV outputs as well as single points.
    exclude = ["distribution", "metric", "group", "id"]
    if not options.write_combos:
        exclude += ['highest_combo', 'lowest_combo']

    if options.write:
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        write_json_file(filename + '.json', data)
        if options.write_csv:
            write_csv_file(filename, data["data"], exclude = exclude)
            if options.write_dist:
                write_dist_csv_file(filename + '_dist', data["data"], exclude)

    return data, filename

if __name__ == '__main__':
    options = parse_args()
    for topo in options.topos:
        g = get_topo_graph(topo)
        do_metrics(options, topo, g)
