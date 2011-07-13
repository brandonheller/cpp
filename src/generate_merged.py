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
from metrics_lib import metric_fullname, get_output_filepath

# Quick hack to not throw exception if we come across a topology for which
# we have no data
IGNORE_MISSING_DATA = True


# TODO: remove
def do_all(options, name, g, i, t, data):
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


if __name__ == "__main__":

    options = plot.parse_args()

    if options.all_topos:
        topos = sorted(zoo_topos())
    else:
        topos = options.topos

    # Grab raw data
    # plot_data[metric] = [dict of topo data, keyed by metric]
    # each value includes:
    # x: list of sorted controller k's
    # lines: dict of y-axis lists, keyed by aspect
    plot_data = {}
    for i, topo in enumerate(topos):
        if not options.max == None and i >= options.max:
            break

        g, usable, note = get_topo_graph(topo)

        if usable:
            # Check for --force here?
            controllers = metrics.get_controllers(g, options)
            exp_filename = metrics.get_filename(topo, options, controllers)

            # Compute data only when the following conditions hold:
            # - asked to complete metrics
            # - AND either the path doesn't exist of we're instructed to force it.      
            if ('metrics' in options.operations and 
                (not os.path.exists(exp_filename + '.json') or options.force)):
                print "skipping already-analyzed topo: %s" % topo
                stats, filename = metrics.do_metrics(options, topo, g)
                filename = filename.replace('data_out', 'data_vis')
            # Otherwise, load the data:
            else:
                if not os.path.exists(exp_filename + '.json'):
                    if IGNORE_MISSING_DATA:
                        # Ignore, continue.
                        continue
                    else:
                        raise Exception("invalid file path: %s" % exp_filename)
                input_file = open(exp_filename + '.json', 'r')
                stats = json.load(input_file)

            for metric in options.metrics:
                if metric not in plot_data:
                    plot_data[metric] = {}

                # Grab range data for the lowest metric values:
                #aspect_fcns = {'lowest': (lambda g, d, m: d[m]['lowest'])}
                aspect_fcns = {'highest': (lambda g, d, m: d[m]['highest']),
                               'mean': (lambda g, d, m: d[m]['mean']),
                               'lowest': (lambda g, d, m: d[m]['lowest'])}
                aspects = aspect_fcns.keys()
                x, lines = plot.ranges_data(stats, aspect_fcns, aspects, metric)    
                plot_data[metric][topo] = {
                    'x': x,
                    'lines': lines
                }
        else:
            print "ignoring unusable topology: %s (%s)" % (topo, note)

        print "topo %s of %s: %s" % (i, len(topos), topo)

    # Now that we have the formatted data ready to go, proceed.
    for metric in options.metrics:
        print "building plots for metric %s" % metric
        assert options.from_start
        assert not options.from_end
        if options.topo_group:
            group_str = options.topo_group
        elif options.all_topos:
            group_str = 'all'
        else:
            group_str = ','.join(options.topos)

        write_filepath = 'data_vis/merged/%s_%i_to_%i_%s' % (group_str, options.from_start, options.from_end, metric)

        xlabel = 'number of controllers (k)'
        aspect_colors = {'highest': 'rx',
                         'mean': 'bo',
                         'lowest': 'g+'}
        this_data_lines = plot_data[metric].values()
        plot.ranges_multiple(stats, metric, aspects, aspect_colors, aspect_fcns,
                    "linear", "linear", None, None, write_filepath + '_ranges',
                    options.write, ext = options.ext,
                    xlabel = xlabel,
                    ylabel = metric_fullname(metric) + " (miles)",
                    data_lines = this_data_lines)
