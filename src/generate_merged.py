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
from topo_lib import get_topo_graph, total_weight
from metrics_lib import metric_fullname
from util import divide_def0
from plot_ranges import get_aspect_fcns, bc_rel_aspect_fcns_gen

# Quick hack to not throw exception if we come across a topology for which
# we have no data
IGNORE_MISSING_DATA = True

# Options for Matplotlib that are common to all graphs (but overrideable.)
COMMON_LINE_OPTS = {'alpha': 0.5, 'markersize': 2}

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
        'get_data_fcn': (lambda g, s, af, a, m: plot.ranges_data(s, af, a, m)),
        'xlabel': (lambda m: 'number of controllers (k)'),
        'ylabel': (lambda m: metric_fullname(m) + " (miles)"),
        'min_y': (lambda o: 0)
    },
    'base_ylog': {
        'get_data_fcn': (lambda g, s, af, a, m: plot.ranges_data(s, af, a, m)),
        'xlabel': (lambda m: 'number of controllers (k)'),
        'ylabel': (lambda m: metric_fullname(m) + " (miles)"),
        'min_y': (lambda o: 1),
        'yscale': 'log'
    },
    'norm_xk': {
        'get_data_fcn': (lambda g, s, af, a, m: norm_x(plot.ranges_data(s, af, a, m), g.number_of_nodes())),
        'xlabel': (lambda m: 'number of controllers (k) / n'),
        'ylabel': (lambda m: metric_fullname(m) + " (miles)"),
        'max_x': (lambda o: 1.0),
        'min_y': (lambda o: 0)
    },
    'norm_xk_ylog': {
        'get_data_fcn': (lambda g, s, af, a, m: norm_x(plot.ranges_data(s, af, a, m), g.number_of_nodes())),
        'xlabel': (lambda m: 'number of controllers (k) / n'),
        'ylabel': (lambda m: metric_fullname(m) + " (miles)"),
        'max_x': (lambda o: 1.0),
        'min_y': (lambda o: 1),
        'yscale': 'log'
    },
    'norm_y': {
        'get_data_fcn': (lambda g, s, af, a, m: norm_y(plot.ranges_data(s, af, a, m))),
        'xlabel': (lambda m: 'number of controllers (k)'),
        'ylabel': (lambda m: metric_fullname(m) + "\nrelative to value at k = 1"),
        'min_y': (lambda o: 0)
    },
    'norm_y_ylog': {
        'get_data_fcn': (lambda g, s, af, a, m: norm_y(plot.ranges_data(s, af, a, m))),
        'xlabel': (lambda m: 'number of controllers (k)'),
        'ylabel': (lambda m: metric_fullname(m) + "\nrelative to value at k = 1"),
        'min_y': (lambda o: 0.001),
        'yscale': 'log'
    },
    'norm_xk_y': {
        'get_data_fcn':
            (lambda g, s, af, a, m: norm_x(norm_y(plot.ranges_data(s, af, a, m)), g.number_of_nodes())),
        'xlabel': (lambda m: 'number of controllers (k) / n'),
        'ylabel': (lambda m: metric_fullname(m) + "\nrelative to value at k = 1"),
        'max_x': (lambda o: 1.0),
        'min_y': (lambda o: 0)
    },
    'norm_xk_ylog': {
        'get_data_fcn':
            (lambda g, s, af, a, m: norm_x(norm_y(plot.ranges_data(s, af, a, m)), g.number_of_nodes())),
        'xlabel': (lambda m: 'number of controllers (k) / n'),
        'ylabel': (lambda m: metric_fullname(m) + "\nrelative to value at k = 1"),
        'max_x': (lambda o: 1.0),
        'min_y': (lambda o: 0.0001),
        'yscale': 'log'
    }
}

shared_get_data_fcns = {
    'base': {
        'get_data_fcn': (lambda g, s, af, a, m: plot.ranges_data(s, af, a, m)),
        'xlabel': (lambda m: 'number of controllers (k)'),
    },
    'norm_xk': {
        'get_data_fcn':
            (lambda g, s, af, a, m: norm_x(plot.ranges_data(s, af, a, m), g.number_of_nodes())),
        'xlabel': (lambda m: 'number of controllers (k) / n'),
        'max_x': (lambda o: 1.0)
    }
}

# get_data_fcn: fcn(g, stats, aspect_fcns, aspects, metric) that returns JSON data
MERGED_RANGE_PLOT_DATA_FCNS = {
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
        'get_data_fcns': ranges_get_data_fcns,
        'min_y': (lambda o: 0.0)
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
        'min_y': (lambda o: 0.8),
        'max_y': (lambda o: 6.0),
        'get_data_fcns': shared_get_data_fcns
    },
    'ratios_mean': {
        'aspect_colors': {
            'mean': 'b*',
            'one': 'g+'
        },
        'aspect_fcns': {
            'mean': (lambda g, d, m: divide_def0(d[m]['mean'], d[m]['lowest'])),
            'one': (lambda g, d, m: 1.0)
        },
        'ylabel': (lambda m: metric_fullname(m) + "/optimal"),
        'min_y': (lambda o: 0.8),
        'max_y': (lambda o: 5.0),
        'get_data_fcns': shared_get_data_fcns
    },
    'bc_rel': {
        'aspect_colors': {
            'bc_rel': 'rx'
        },
        'aspect_fcns_gen': bc_rel_aspect_fcns_gen,
        'ylabel': (lambda m: metric_fullname(m) + "(1) /\n" + metric_fullname(m) + "/k"),
        'max_y': (lambda o: 2.0),
        'min_y': (lambda o: -0.1),
        'get_data_fcns': shared_get_data_fcns
    },
    'pareto_max': {
        'aspect_colors': {
            'max': 'rx'
        },
        'aspect_fcns': {
            'max': (lambda g, d, m: d[m])
        },
        'min_y': 0.0,
        'get_data_fcns': {
            'base': {
                'get_data_fcn': (lambda g, s, af, a, m: plot.pareto_norm(s, af, a, m)),
            }
        },
        'xlabel': (lambda m: 'number of controllers (k)'),
        'ylabel': (lambda m: 'max tradeoff (fraction)'),
    },
    'pareto_max_bw': {
        'aspect_colors': {
            'max': 'rx'
        },
        'aspect_fcns': {
            'max': (lambda g, d, m: d[m])
        },
        'min_y': -0.1,
        'get_data_fcns': {
            'base': {
                'get_data_fcn': (lambda g, s, af, a, m: plot.pareto_norm(s, af, a, m)),
            }
        },
        'min_x': 0.5,
        'max_x': (lambda o: o.from_start + 0.5),
        'xlabel': (lambda m: 'number of controllers (k)'),
        'ylabel': (lambda m: 'other metric increase when\nopt for %s' % metric_fullname(m)),
        'box_whisker': True
    }
}

RANGE_PLOT_TYPES = ['ranges_lowest', 'ratios_all', 'ratios_mean', 'bc_rel', 'pareto_max', 'pareto_max_bw']

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


def get_param(name, fcn_args, default, *args):
    '''Search chain in order for first hit; return default if no hits.'''
    for arg in args:
        if arg and name in arg:
            # Is it a function (that is, callable)?
            if hasattr(arg[name], '__call__'):
                return arg[name](*fcn_args)
            else:
                return arg[name]
    return default


def dump_csv(csv_tuples, csv_fields, options):
    print "dumping CSV output"
    group_str = get_group_str(options)
    filepath = 'data_out/csv/%s_%i_to_%i.csv' % (group_str, options.from_start, options.from_end)
    plot.mkdir_p(os.path.dirname(filepath))
    f = open(filepath, 'w')
    f.write(',\t'.join(csv_fields) + '\n')
    for csv_tuple in csv_tuples:
        f.write(',\t'.join([str(s) for s in csv_tuple]) + '\n')
    f.close()


if __name__ == "__main__":

    options = plot.parse_args()

    if options.all_topos:
        topos = sorted(zoo_topos())
    else:
        topos = options.topos

    assert options.from_start
    assert not options.from_end

    used = 0  # topologies that are usable and used.

    # Grab raw data
    # plot_data[ptype] = [dict of metric data, keyed by ptype]:
    # plot_data[ptype][metric] = [dict of topo data, keyed by metric]
    # each value includes:
    # x: list of sorted controller k's
    # lines: dict of y-axis lists, keyed by aspect
    plot_data = {}
    # CSV format:
    csv_fields = ['metric', 'ptype', 'name', 'topo', 'n', 'e', 'w', 'gdf_name', 'x', 'y']
    csv_tuples = []
    for i, topo in enumerate(topos):
        if not options.max == None and i >= options.max:
            break

        g, usable, note = get_topo_graph(topo)

        if usable:
            w = total_weight(g)

            # Check for --force here?
            print "usable topo: %s" % topo
            used += 1
            controllers = metrics.get_controllers(g, options)
            exp_filename = metrics.get_filename(topo, options, controllers)

            path_exists = os.path.exists(exp_filename + '.json')
            compute_metrics = 'metrics' in options.operations

            # Compute data only when the following conditions hold:
            # - asked to complete metrics, AND
            # - asked to force, or data is missing
            if compute_metrics and (options.force or not path_exists):
                print "freshly analyzing topo: %s" % topo
                stats, filename = metrics.do_metrics(options, topo, g)
                filename = filename.replace('data_out', 'data_vis')
            # Otherwise, load the data:
            else:
                if not os.path.exists(exp_filename + '.json'):
                    if IGNORE_MISSING_DATA:
                        # Ignore, continue.
                        print "ignoring missing data"
                        continue
                    else:
                        raise Exception("invalid file path: %s" % exp_filename)
                input_file = open(exp_filename + '.json', 'r')
                stats = json.load(input_file)

            for metric in options.metrics:
                for ptype in RANGE_PLOT_TYPES:
                    if metric not in plot_data:
                        plot_data[metric] = {}
                        print "intializing metric: %s" % metric
                    if ptype not in plot_data[metric]:
                        plot_data[metric][ptype] = {}

                    p = MERGED_RANGE_PLOT_DATA_FCNS[ptype]
                    aspect_fcns = get_aspect_fcns(p, stats, metric)
                    aspects = aspect_fcns.keys()

                    for name, gdf in p['get_data_fcns'].iteritems():
                        if name not in plot_data[metric][ptype]:
                            plot_data[metric][ptype][name] = {}
                        gdf_fcn = gdf['get_data_fcn']
                        plot_data[metric][ptype][name][topo] = gdf_fcn(g, stats, aspect_fcns, aspects, metric)

                        # Emit tuple for plot data construction:
                        n = g.number_of_nodes()
                        e = g.number_of_edges()
                        x = plot_data[metric][ptype][name][topo]['x']
                        lines = plot_data[metric][ptype][name][topo]['lines']
                        for line_name, values in lines.iteritems():
                            for j, b in enumerate(values):
                                csv_tuples.append([metric, ptype, name, topo, n, e, w, line_name, x[j], b])

        else:
            print "ignoring unusable topology: %s (%s)" % (topo, note)

        print "topo %s of %s: %s" % (i, len(topos), topo)


    print "used %s topologies" % used

    if plot_data == {}:
        raise Exception("null plot_data: verify that the expected data is in the right place.")

    # Dump CSV output:
    dump_csv(csv_tuples, csv_fields, options)

    # Now that we have the formatted data ready to go, proceed.
    for metric in options.metrics:
        print "building plots for metric %s" % metric
        metric_data = plot_data[metric]

        for ptype in RANGE_PLOT_TYPES:
            p = MERGED_RANGE_PLOT_DATA_FCNS[ptype]
            group_str = get_group_str(options)
            write_filepath = 'data_vis/merged/%s_%i_to_%i_%s_%s' % (group_str, options.from_start, options.from_end, metric, ptype)

            aspect_fcns = get_aspect_fcns(p, stats, metric)
            aspect_colors = p['aspect_colors']
            aspects = aspect_fcns.keys()
            for gdf_name, values_by_topo in metric_data[ptype].iteritems():
                this_data = values_by_topo.values()
                gdf = p['get_data_fcns'][gdf_name]
                xlabel = get_param('xlabel', [metric], None, p, gdf)
                ylabel = get_param('ylabel', [metric], None, p, gdf)
                max_x = get_param('max_x', [options], None, p, gdf)
                max_y = get_param('max_y', [options], None, p, gdf)
                min_x = get_param('min_x', [options], None, p, gdf)
                min_y = get_param('min_y', [options], None, p, gdf)
                line_opts = get_param('line_opts', None, {}, p, gdf)
                xscale = get_param('xscale', None, 'linear', p, gdf)
                yscale = get_param('yscale', None, 'linear', p, gdf)
                box_whisker = get_param('box_whisker', None, False, p, gdf)
                plot.ranges_multiple(stats, metric, aspects, aspect_colors, aspect_fcns,
                            xscale, yscale, None, None, write_filepath + '_' + gdf_name,
                            options.write, ext = options.ext,
                            xlabel = xlabel,
                            ylabel = ylabel,
                            data = this_data,
                            min_x = min_x, max_x = max_x,
                            min_y = min_y, max_y = max_y,
                            line_opts = dict(COMMON_LINE_OPTS, **line_opts),
                            box_whisker = box_whisker)
