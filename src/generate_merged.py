#!/usr/bin/env python
'''Generate everything for one or more topos.'''
import copy
import json
import os

import lib.plot as plot
import metrics
import plot_cdfs
import plot_ranges
import plot_cloud
import plot_pareto
#import map_combos
from zoo_tools import zoo_topos
from topo_lib import get_topo_graph
from metrics_lib import metric_fullname
from util import divide_def0
from plot_ranges import get_aspect_fcns, bc_rel_aspect_fcns_gen

# Quick hack to not throw exception if we come across a topology for which
# we have no data
IGNORE_MISSING_DATA = True


def norm_y(data):
    data_copy = copy.copy(data)
    for metric, line in data['lines'].iteritems():
        first = line[0]
        data_copy['lines'][metric] = [d / float(first) for d in line]
    return data_copy

def norm_x(data, k):
    data_copy = copy.copy(data)
    data_copy['x'] = [d / float(k) for d in data['x']]
    return data_copy


# Shared ranges data functions
ranges_get_data_fcns = {
    'base': {
        'get_data_fcn':
            (lambda g, s, af, a, m: plot.ranges_data(s, af, a, m)),
        'xlabel':
            (lambda m: 'number of controllers (k)'),
        'ylabel':
            (lambda m: metric_fullname(m) + " (miles)")
    },
    'norm_xk': {
        'get_data_fcn':
            (lambda g, s, af, a, m: norm_x(plot.ranges_data(s, af, a, m), g.number_of_nodes())),
        'xlabel':
            (lambda m: 'number of controllers (k) / n'),
        'ylabel':
            (lambda m: metric_fullname(m) + " (miles)"),
        'max_x':
            (lambda o: 1.0)
    },
    'norm_y': {
        'get_data_fcn':
            (lambda g, s, af, a, m: norm_y(plot.ranges_data(s, af, a, m))),
        'xlabel':
            (lambda m: 'number of controllers (k)'),
        'ylabel':
            (lambda m: metric_fullname(m) + "\nrelative to value at k = 1")
    },
    'norm_xk_y': {
        'get_data_fcn':
            (lambda g, s, af, a, m: norm_x(norm_y(plot.ranges_data(s, af, a, m)), g.number_of_nodes())),
        'xlabel':
            (lambda m: 'number of controllers (k) / n'),
        'ylabel':
            (lambda m: metric_fullname(m) + "\nrelative to value at k = 1"),
        'max_x':
            (lambda o: 1.0)
    }
}

shared_get_data_fcns = {
    'base': {
        'get_data_fcn':
            (lambda g, s, af, a, m: plot.ranges_data(s, af, a, m)),
        'xlabel':
            (lambda m: 'number of controllers (k)'),
    },
    'norm_xk': {
        'get_data_fcn':
            (lambda g, s, af, a, m: norm_x(plot.ranges_data(s, af, a, m), g.number_of_nodes())),
        'xlabel':
            (lambda m: 'number of controllers (k) / n'),
        'max_x':
            (lambda o: 1.0)
    }
}

# get_data_fcn: fcn(g, stats, aspect_fcns, aspects, metric) that returns JSON data
MERGED_PLOT_DATA_FCNS = {
    'ranges_all': {
        'aspect_fcns': {
            'highest': (lambda g, d, m: d[m]['highest']),
            'mean': (lambda g, d, m: d[m]['mean']),
            'lowest': (lambda g, d, m: d[m]['lowest'])
        },
        'aspect_colors': {
            'highest': 'rx',
            'mean': 'bo',
            'lowest': 'g+'
        },
        'get_data_fcns': ranges_get_data_fcns
    },
    'ranges_lowest': {
        'aspect_fcns': {
            'lowest': (lambda g, d, m: d[m]['lowest'])
        },
        'aspect_colors': {
            'lowest': 'g+'
        },
        'get_data_fcns': ranges_get_data_fcns
    },
    'ratios_all': {
        'aspect_colors': {
            'highest': 'rx',
            'mean': 'bo',
            'one': 'g+'
        },
        'aspect_fcns': {
            'highest': (lambda g, d, m: divide_def0(d[m]['highest'], d[m]['lowest'])),
            'mean': (lambda g, d, m: divide_def0(d[m]['mean'], d[m]['lowest'])),
            'one': (lambda g, d, m: 1.0)
        },
        'ylabel': (lambda m: metric_fullname(m) + "/optimal"),
        'max_y': (lambda o: 10.0),
        'get_data_fcns': shared_get_data_fcns
    },
    'bc_rel': {
        'aspect_colors': {
            'bc_rel': 'rx'
        },
        'aspect_fcns_gen': bc_rel_aspect_fcns_gen,
        'ylabel': (lambda m: metric_fullname(m) + "(1) /\n" + metric_fullname(m) + "/k"),
        'max_y': (lambda o: o.maxy),
        'get_data_fcns': shared_get_data_fcns
    },
}

PLOT_TYPES = ['ranges_lowest', 'ratios_all', 'bc_rel']


def get_group_str(options):
    if options.topo_group:
        group_str = options.topo_group
    elif options.all_topos:
        group_str = 'all'
    else:
        group_str = ','.join(options.topos)
    return group_str


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


def get_param(name, fcn_args, *args):
    '''Search chain in order for first hit.

    If none is defined at the end of the args list, and all miss, return None.
    Else, raise exception.
    '''
    for i, arg in enumerate(args):
        if arg == None:
            if i == len(args) - 1:
                return None
            else:
                raise Exception("encountered False value in chain before end")
        elif name in arg:
            # Is it a function (that is, callable)?
            if hasattr(arg[name], '__call__'):
                return arg[name](*fcn_args)
            else:
                return arg[name]

    raise Exception("could not find parameter: %s" % name)


if __name__ == "__main__":

    options = plot.parse_args()

    if options.all_topos:
        topos = sorted(zoo_topos())
    else:
        topos = options.topos

    # Grab raw data
    # plot_data[ptype] = [dict of metric data, keyed by ptype]:
    # plot_data[ptype][metric] = [dict of topo data, keyed by metric]
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

                for ptype in PLOT_TYPES:
                    if metric not in plot_data:
                        plot_data[metric] = {}
                    if ptype not in plot_data[metric]:
                        plot_data[metric][ptype] = {}

                    p = MERGED_PLOT_DATA_FCNS[ptype]
                    aspect_fcns = get_aspect_fcns(p, stats, metric)
                    aspects = aspect_fcns.keys()

                    for name, gdf in p['get_data_fcns'].iteritems():
                        if name not in plot_data[metric][ptype]:
                            plot_data[metric][ptype][name] = {}
                        gdf_fcn = gdf['get_data_fcn']

                        plot_data[metric][ptype][name][topo] = gdf_fcn(g, stats, aspect_fcns, aspects, metric)
        else:
            print "ignoring unusable topology: %s (%s)" % (topo, note)

        print "topo %s of %s: %s" % (i, len(topos), topo)

    # Now that we have the formatted data ready to go, proceed.
    for metric in options.metrics:
        print "building plots for metric %s" % metric
        assert options.from_start
        assert not options.from_end
        group_str = get_group_str(options)
        metric_data = plot_data[metric]

        for ptype in PLOT_TYPES:
            p = MERGED_PLOT_DATA_FCNS[ptype]
            write_filepath = 'data_vis/merged/%s_%i_to_%i_%s_%s' % (group_str, options.from_start, options.from_end, metric, ptype)

            aspect_fcns = get_aspect_fcns(p, stats, metric)
            aspect_colors = p['aspect_colors']
            aspects = aspect_fcns.keys()
            for gdf_name, values_by_topo in metric_data[ptype].iteritems():
                this_data = values_by_topo.values()
                gdf = p['get_data_fcns'][gdf_name]
                xlabel = get_param('xlabel', [metric], p, gdf)
                ylabel = get_param('ylabel', [metric], p, gdf)
                max_x = get_param('max_x', [options], p, gdf, None)
                max_y = get_param('max_y', [options], p, gdf, None)
                plot.ranges_multiple(stats, metric, aspects, aspect_colors, aspect_fcns,
                            "linear", "linear", None, None, write_filepath + '_' + gdf_name,
                            options.write, ext = options.ext,
                            xlabel = xlabel,
                            ylabel = ylabel,
                            data = this_data,
                            max_x = max_x,
                            max_y = max_y)
