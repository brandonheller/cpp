#!/usr/bin/env python
'''Generate everything for one or more topos.'''
import copy
import json
import os

from lib.colors import COLORS
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

# Conversion factor for dual-y-scale graphs
# Assume speed of light in fiber is 2/3 that in other media
# (1m / 0.00062137 miles) * (1 sec / 2e8 m) * (1000 ms /sec)
# Comes to 0.0080467354394322243 ms / mile
MILES_TO_MS = (1/0.00062137) * (1/2e8) * 1000

USE_FRACTIONS = True  # Use fractions rather than raw for latex one-ctrl table?
SAFETY_MARGINS = [1.0, 1.5, 2.0]  # For use in one-ctrl table

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

# Half the two-way totals, to compare to one-way latencies.
LATENCY_LINES = [[5, 'switch processing'],
                 [25, 'ring protection'],
                 [100, 'mesh restoration']]

# Shared ranges data functions
ranges_get_data_fcns = {
    'base': {
        'get_data_fcn': (lambda g, s, af, a, m: plot.ranges_data(s, af, a, m)),
        'xlabel': (lambda m: 'number of controllers (k)'),
        'ylabel': (lambda m: metric_fullname(m) + " (miles)"),
        'min_y': (lambda o: 0.0),
        'ylabel2': (lambda m: metric_fullname(m) + " (ms)"),
        'max_y': (lambda o: 13000),
        'y2_scale_factor': MILES_TO_MS,
        'hlines': LATENCY_LINES
    },
    'base_ylog': {
        'get_data_fcn': (lambda g, s, af, a, m: plot.ranges_data(s, af, a, m)),
        'xlabel': (lambda m: 'number of controllers (k)'),
        'ylabel': (lambda m: metric_fullname(m) + " (miles)"),
        'max_y': (lambda o: 13000),
        'min_y': (lambda o: 10),
        'yscale': 'log',
        'ylabel2': (lambda m: metric_fullname(m) + " (ms)"),
        'y2_scale_factor': MILES_TO_MS,
        'hlines': LATENCY_LINES
    },
    'norm_xk': {
        'get_data_fcn': (lambda g, s, af, a, m: norm_x(plot.ranges_data(s, af, a, m), g.number_of_nodes())),
        'xlabel': (lambda m: 'number of controllers (k) / n'),
        'ylabel': (lambda m: metric_fullname(m) + " (miles)"),
        'max_x': (lambda o: 1.0),
        'min_y': (lambda o: 0),
        'ylabel2': (lambda m: metric_fullname(m) + " (ms)"),
        'y2_scale_factor': MILES_TO_MS,
        'hlines': LATENCY_LINES
    },
    'norm_xk_ylog': {
        'get_data_fcn': (lambda g, s, af, a, m: norm_x(plot.ranges_data(s, af, a, m), g.number_of_nodes())),
        'xlabel': (lambda m: 'number of controllers (k) / n'),
        'ylabel': (lambda m: metric_fullname(m) + " (miles)"),
        'max_x': (lambda o: 1.0),
        'max_y': (lambda o: 13000),
        'min_y': (lambda o: 10),
        'yscale': 'log',
        'ylabel2': (lambda m: metric_fullname(m) + " (ms)"),
        'y2_scale_factor': MILES_TO_MS,
        'hlines': LATENCY_LINES
    },
    'norm_y': {
        'get_data_fcn': (lambda g, s, af, a, m: norm_y(plot.ranges_data(s, af, a, m))),
        'xlabel': (lambda m: 'number of controllers (k)'),
        'ylabel': (lambda m: metric_fullname(m) + "\nrelative to value at k = 1"),
        'min_y': (lambda o: 0),
        'overlay_line' : {
            'fcn': (lambda c: 1.0 / float(c))
        },
        'overlay_line' : {
            'fcn': (lambda c: 1.0 / float(c)),
            'text': "proportional\nreduction",
            'xy': (1.45, 0.4),
        }
    },
    'norm_y_ylog': {
        'get_data_fcn': (lambda g, s, af, a, m: norm_y(plot.ranges_data(s, af, a, m))),
        'xlabel': (lambda m: 'number of controllers (k)'),
        'ylabel': (lambda m: metric_fullname(m) + "\nrelative to value at k = 1"),
        'min_y': (lambda o: 0.01),
        'yscale': 'log'
    },
    'norm_xk_norm_y': {
        'get_data_fcn':
            (lambda g, s, af, a, m: norm_x(norm_y(plot.ranges_data(s, af, a, m)), g.number_of_nodes())),
        'xlabel': (lambda m: 'number of controllers (k) / n'),
        'ylabel': (lambda m: metric_fullname(m) + "\nrelative to value at k = 1"),
        'max_x': (lambda o: 1.0),
        'min_y': (lambda o: 0)
    },
    'norm_xk_norm_ylog': {
        'get_data_fcn':
            (lambda g, s, af, a, m: norm_x(norm_y(plot.ranges_data(s, af, a, m)), g.number_of_nodes())),
        'xlabel': (lambda m: 'number of controllers (k) / n'),
        'ylabel': (lambda m: metric_fullname(m) + "\nrelative to value at k = 1"),
        'max_x': (lambda o: 1.0),
        'min_y': (lambda o: 0.01),
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


def dump_1ctrl_latex_table(latencies, write_filepath, safety_margins, fraction = False):
    latencies = sorted(latencies)
    write_filepath += '.latex'
    f = open(write_filepath, 'w')
    # Columns: Goals(2), Safety Margins(n)
    s = "\\begin{tabular}{*{%i}{l}}\n" % (len(safety_margins) + 2)
    s += "\\multicolumn{2}{c}{Round-trip Latency Target} & \\multicolumn{%i}{l}{Safety Margin} \\\\ \n" % len(safety_margins)
    s += "Name & Delay & %s\\\\ \n" % ' & '.join([str(a) + 'x' for a in safety_margins])
    s += "\hline\n"
    for ms, name in LATENCY_LINES:
        s += ' & '.join([name, str(ms * 2) + ' ms'])
        for i, safety_margin in enumerate(safety_margins):
            num_ok = len([a for a in latencies if a * MILES_TO_MS * safety_margin < ms])
            s += ' & '
            if fraction:
                # Make a percentage:
                s += "%0.0f\\%%" % (num_ok * 100.0 / float(len(latencies)))
            else:
                s += str(num_ok)
        s += "\\\\ \n"
    s += "\end{tabular}"
    print "wrote file to %s" % write_filepath
    f.write(s)

if __name__ == "__main__":

    options = plot.parse_args()

    if options.all_topos:
        topos = sorted(zoo_topos())
    else:
        topos = options.topos

    assert options.from_start
    assert not options.from_end

    total_usable = 0  # usable topologies: if data is computed, use them.
    total_used = 0  # topologies with data that we derive stats from

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
            total_usable += 1
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
                total_used += 1
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
                total_used += 1

            for metric in options.metrics:
                for ptype in options.plots:
                    if ptype not in RANGE_PLOT_TYPES:
                        raise Exception("invalid plot type specified")
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

    print "total topologies: %s" % len(topos)
    print "usable topologies: %s" % total_usable
    print "used topologies: %s" % total_used


    if plot_data == {}:
        raise Exception("null plot_data: verify that the expected data is in the right place.")

    # Dump CSV output:
    dump_csv(csv_tuples, csv_fields, options)

    # Now that we have the formatted data ready to go, proceed.
    for metric in options.metrics:
        print "building plots for metric %s" % metric
        metric_data = plot_data[metric]

        if 'latency' in options.cdf_plots:
            assert 'ranges_lowest' in metric_data
            assert 'base' in metric_data['ranges_lowest']
            topo_data = metric_data['ranges_lowest']['base']
            combined = {}  # keys are values for k; values are distribution of optimal latencies
            for topo, data_lines in topo_data.iteritems():
                x = data_lines['x']
                lines = data_lines['lines']
                for line_name, values in lines.iteritems():
                    for j, b in enumerate(values):
                        if x[j] not in combined:
                            combined[x[j]] = []
                        combined[x[j]].append(b)

            group_str = get_group_str(options)
            xmax = max(combined[sorted(combined.keys())[0]])
            axis_limits = [0, xmax, 0, 1]
            for xscale in ["linear", "log"]:
                ptype = 'latency_cdfs_' + xscale
                write_filepath = 'data_vis/merged/%s_%i_to_%i_%s_%s' % (group_str, options.from_start, options.from_end, metric, ptype)
                # Assume the loweest-numbered element is the smallest
                plot.plot('cdf', combined, COLORS, axis_limits,
                          metric, xscale, "linear", write_filepath,
                          options.write,
                          xlabel = 'optimal ' + metric_fullname(metric) + ' (miles)',
                          ylabel = 'fraction of topologies',
                          ext = options.ext,
                          legend = True)

            if options.gen_1ctrl_table:
                write_filepath = 'data_vis/merged/%s_%i_to_%i_%s_%s' % (group_str, options.from_start, options.from_end, metric, '1ctrl_table')
                dump_1ctrl_latex_table(combined[1], write_filepath, SAFETY_MARGINS, USE_FRACTIONS)

        if 'pareto' in options.cdf_plots:
            assert 'pareto_max' in metric_data
            assert 'base' in metric_data['pareto_max']
            topo_data = metric_data['pareto_max']['base']
            combined = {}  # keys are values for k; values are distribution of optimal latencies
            for topo, data_lines in topo_data.iteritems():
                x = data_lines['x']
                lines = data_lines['lines']
                for aspect, values in lines.iteritems():
                    for j, b in enumerate(values):
                        if x[j] not in combined:
                            combined[x[j]] = []
                        combined[x[j]].append(b)

            ptype = 'pareto_cdfs'
            group_str = get_group_str(options)
            write_filepath = 'data_vis/merged/%s_%i_to_%i_%s_%s' % (group_str, options.from_start, options.from_end, metric, ptype)
            # Assume the loweest-numbered element is the smallest
            all_x = []
            for values in combined.values():
                all_x.extend(values)
            xmax = max(all_x)
            axis_limits = [0, xmax, 0, 1]
            def metric_shortname(metric):
                if metric == 'latency':
                    return 'avg lat'
                if metric == 'wc_latency':
                    return 'w-c lat'
            plot.plot('cdf', combined, COLORS, axis_limits,
                      metric, "linear", "linear", write_filepath,
                      options.write,
                      xlabel = 'other metric increase for opt %s' % metric_shortname(metric),
                      ylabel = 'fraction of topologies',
                      ext = options.ext,
                      legend = True)


        for ptype in options.plots:
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
                ylabel2 = get_param('ylabel2', [metric], None, p, gdf)
                max_x = get_param('max_x', [options], None, p, gdf)
                max_y = get_param('max_y', [options], None, p, gdf)
                min_x = get_param('min_x', [options], None, p, gdf)
                min_y = get_param('min_y', [options], None, p, gdf)
                line_opts = get_param('line_opts', None, {}, p, gdf)
                xscale = get_param('xscale', None, 'linear', p, gdf)
                yscale = get_param('yscale', None, 'linear', p, gdf)
                y2_scale_factor = get_param('y2_scale_factor', None, None, p, gdf)
                box_whisker = get_param('box_whisker', None, False, p, gdf)
                hlines = get_param('hlines', None, None, p, gdf)
                overlay_line = get_param('overlay_line', None, None, p, gdf)
                plot.ranges_multiple(stats, metric, aspects, aspect_colors, aspect_fcns,
                            xscale, yscale, None, None, write_filepath + '_' + gdf_name,
                            options.write, ext = options.ext,
                            xlabel = xlabel,
                            ylabel = ylabel,
                            data = this_data,
                            min_x = min_x, max_x = max_x,
                            min_y = min_y, max_y = max_y,
                            line_opts = dict(COMMON_LINE_OPTS, **line_opts),
                            box_whisker = box_whisker,
                            ylabel2 = ylabel2,
                            y2_scale_factor = y2_scale_factor,
                            hlines = hlines,
                            overlay_line = overlay_line)
