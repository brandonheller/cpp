#!/usr/bin/env python
'''Generate everything for one or more topos.'''
import json
import os

import networkx as nx

import lib.plot as plot
import metrics
import plot_cdfs
import plot_ranges
import plot_cloud
import plot_pareto
#import map_combos
from zoo_tools import zoo_topos
from topo_lib import get_topo_graph, has_weights


if __name__ == "__main__":

    global options
    options = plot.parse_args()

    def do_all(name, g, i, t, data):
        global options
        assert options
        filename = ''
        if 'metrics' in options.operations:
            stats, filename = metrics.do_metrics(options, name, g)
            filename = filename.replace('data_out', 'data_vis')
        else:
            controllers = metrics.get_controllers(g, options)
            exp_filename = metrics.get_filename(name, options, controllers)
            if not os.path.exists(exp_filename + '.json'):
                raise Exception("invalid file path: %s" % exp_filename)
            input_file = open(exp_filename + '.json', 'r')
            stats = json.load(input_file)
            filename = exp_filename.replace('data_out', 'data_vis')
        if 'cdfs' in options.operations:
            plot_cdfs.do_cdfs(options, stats, filename)
        if 'ranges' in options.operations:
            plot_ranges.do_ranges(options, stats, filename)
        if 'pareto' in options.operations:
            plot_pareto.do_pareto(options, stats, filename)
        if 'cloud' in options.operations:
            plot_cloud.do_cloud(options, stats, filename, 'png')
        #map_combos.do_plot(options, stats, g, filename)

    if options.all_topos:
        topos = sorted(zoo_topos())
    else:
        topos = options.topos

    t = len(topos)
    ignored = []
    successes = []
    for i, topo in enumerate(topos):
        if not options.max == None and i >= options.max:
            break

        print "topo %s of %s: %s" % (i, t, topo)
        g, usable, note = get_topo_graph(topo)
        cc = nx.number_connected_components(g)
        controllers = metrics.get_controllers(g, options)
        exp_filename = metrics.get_filename(topo, options, controllers)

        if not g:
            raise Exception("WTF?  null graph: %s" % topo)

        if options.topos_blacklist and topo in options.topos_blacklist:
            print "ignoring topo %s - in blacklist" % topo
            ignored.append(topo)
        elif cc != 1:  # Ignore multiple-CC topos, which confuse APSP calcs
            print "ignoring topo, cc != 1: %s" % topo
            ignored.append(topo)
        elif g.number_of_nodes() < len(controllers):
            print "skipping topo, c >= n: %s" % topo
            ignored.append(topo)
        elif not options.force and os.path.exists(exp_filename + '.json'):
            # Don't bother doing work if our metrics are already there.
            print "skipping already-analyzed topo: %s" % topo
            ignored.append(topo)
        elif not has_weights(g):
            ignored.append(topo)
            print "no weights for %s, skipping" % topo
        else:
            do_all(topo, g, 1, 1, None)
            successes.append(topo)

    print "successes: %s of %s: %s" % (len(successes), t, successes)
    print "ignored: %s of %s: %s" % (len(ignored), t, ignored)