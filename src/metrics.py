#!/usr/bin/env python
'''Compute metrics for varying number of controllers w/ different algorithms.

The data schema looks something like this:

data['data'][num controllers] = [latency:latency, nodes:[best-pos node(s)]]
data['metrics'] = [list of metrics data]
data['group'] = [list of controllers]

'''
import logging
from optparse import OptionParser
import os
import time

import networkx as nx

from file_libs import write_csv_file, write_json_file, read_json_file
from file_libs import write_dist_csv_file
import metrics_lib as metrics
from os3e_weighted import OS3EWeightedGraph


# From http://hoegners.de/Maxi/geo/
import geo
# To test, go to http://www.daftlogic.com/projects-google-maps-distance-calculator.htm
# and run this code - see if the Portland - SanFran distance is ~533 miles.
# portland = geo.xyz(45.5, -122.67)
# sanfran = geo.xyz(37.777, -122.419)
METERS_TO_MILES = 0.000621371192
# print geo.distance(portland, sanfran) * METERS_TO_MILES

DEF_TOPO = 'os3e'

logging.basicConfig(level=logging.DEBUG)


def parse_args():
    opts = OptionParser()
    opts.add_option("--topo", type = 'str', default = DEF_TOPO,
                    help = "topology name")
    opts.add_option("--topo_list", type = 'str', default = None,
                    help = "list of comma-separated controller totals")
    opts.add_option("--from_start", type = 'int', default = 3,
                    help = "number of controllers from start")
    opts.add_option("--from_end", type = 'int', default = 0,
                    help = "number of controllers from end")
    opts.add_option("--controller_list", type = 'str', default = None,
                    help = "list of comma-separated controller totals")
    opts.add_option("--metric",
                    default = 'latency',
                    choices = metrics.METRICS,
                    help = "metric to compute, one in %s" % metrics.METRICS)
    opts.add_option("--all_metrics",  action = "store_true",
                    default = False,
                    help = "compute all metrics?")    
    opts.add_option("--lat_metrics",  action = "store_true",
                    default = False,
                    help = "compute all latency metrics?")
    opts.add_option("-w", "--write",  action = "store_true",
                    default = False,
                    help = "write plots, rather than display?")
    opts.add_option("--median",  action = "store_true",
                    default = False,
                    help = "compute median?")
    opts.add_option("--no-multiprocess",  action = "store_false",
                    default = True, dest = 'multiprocess',
                    help = "don't use multiple processes?")
    opts.add_option("--processes", type = 'int', default = 4,
                    help = "worker pool size; must set multiprocess=True")
    opts.add_option("--chunksize", type = 'int', default = 50,
                    help = "batch size for parallel processing")
    opts.add_option("--write_combos",  action = "store_true",
                    default = False,
                    help = "write out combinations?")
    opts.add_option("--write_dist",  action = "store_true",
                    default = False,
                    help = "write_distribution?")
    opts.add_option("--write_csv",  action = "store_true",
                    default = False,
                    help = "write csv file?")
    opts.add_option("--no-dist_only",  action = "store_false",
                    default = True, dest = 'dist_only',
                    help = "don't write out _only_ the full distribution (i.e.,"
                    "run all algorithms.)")
    opts.add_option("--use_prior",  action = "store_true",
                    default = False,
                    help =  "Pull in previously computed data, rather than recompute?")
    opts.add_option("--no-compute_start",  action = "store_false",
                    default = True, dest = 'compute_start',
                    help = "don't compute metrics from start?")
    opts.add_option("--no-compute_end",  action = "store_false",
                    default = True, dest = 'compute_end',
                    help = "don't compute metrics from end?")
    options, arguments = opts.parse_args()

    if options.all_metrics:
        options.metrics = metrics.METRICS
    elif options.lat_metrics:
        options.metrics = ['latency', 'wc_latency']
    else:
        options.metrics = [options.metric]

    options.controllers = None
    if options.controller_list:
        options.controllers = []
        for i in options.controller_list.split(','):
            options.controllers.append(int(i))

    if options.topo != DEF_TOPO and options.topo_list:
        raise Exception("Both topo and topo_list provided; pick one please")
    else:
        if options.topo_list:
            options.topos = options.topo_list.split(',')
        else:
            options.topos = [options.topo]

    return options


def lat_long_pair(node):
    return (float(node["Latitude"]), float(node["Longitude"]))


def dist_in_miles(g, src, dst):
    '''Given a NetworkX graph data and node names, compute mileage between.'''
    src_pair = lat_long_pair(g.node[src])
    src_loc = geo.xyz(src_pair[0], src_pair[1])
    dst_pair = lat_long_pair(g.node[dst])
    dst_loc = geo.xyz(dst_pair[0], dst_pair[1])
    return geo.distance(src_loc, dst_loc) * METERS_TO_MILES


def import_zoo_graph(topo):
    '''Given name of Topology Zoo graph, read and assign mileage weights.'''
    filename = 'zoo/' + topo + '.gml'
    if not os.path.exists(filename):
        raise Exception("invalid topo path:%s" % filename)
    # Convert multigraphs to regular graphs; multiple edges don't affect
    # latency, but add complications when debugging.
    g = nx.Graph(nx.read_gml(filename))
    # Append weights
    for src, dst in g.edges():
        g[src][dst]["weight"] = dist_in_miles(g, src, dst)
        print "dist between %s and %s is %s" % (src, dst, g[src][dst]["weight"])
    return g


def get_topo_graph(topo):
    if topo == 'os3e':
        g = OS3EWeightedGraph()
    else:
        g = import_zoo_graph(topo)
    return g


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
    filename = "data_out/" + topo
    if options.controller_list:
        for c in controllers:
            filename += "_%s" % c
    else:
        filename += "_%s_to_%s" % (options.from_start, options.from_end)
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


def do_metrics():

    options = parse_args()

    for topo in options.topos:

        g = get_topo_graph(topo)
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
            write_json_file(filename + '.json', data)
            if options.write_csv:
                write_csv_file(filename, data["data"], exclude = exclude)
                if options.write_dist:
                    write_dist_csv_file(filename + '_dist', data["data"], exclude)


if __name__ == '__main__':
    do_metrics()
