#!/usr/bin/env python
'''Plot ranges, where each series is a # of controllers.'''
from lib.options import parse_args
import lib.plot as plot
from metrics_lib import metric_fullname, get_output_filepath, METRIC_FCNS
from util import divide_def0
from lib.dist import MILES_TO_MS, LATENCY_LINES
import networkx as nx
from topo_lib import get_topo_graph

PLOT_TYPES = ['ranges', 'ratios', 'durations', 'bc_abs', 'bc_rel', 'abs_benefit', 'miles_cost', 'ft_cost']
PLOTS = PLOT_TYPES


def bc_abs_aspect_fcns_gen(stats, metric):
    value_one = stats['data'][sorted(stats['group'])[0]][metric]['lowest']
    aspect_fcns = {'bc_abs': (lambda g, d, m: (value_one - d[m]['lowest']) / max(1, (float(g) - 1)))}
    return aspect_fcns

def bc_rel_aspect_fcns_gen(stats, metric):
    value_one = stats['data'][sorted(stats['group'])[0]][metric]['lowest']
    aspect_fcns = {'bc_rel': (lambda g, d, m: divide_def0(value_one, float(d[m]['lowest'])) / float(g))}
    return aspect_fcns

def abs_benefit_fcns_gen(stats, metric):
    groups = sorted([int(g) for g in stats['group']])
    abs_benefits = {}
    for i, g in enumerate(groups):
        if i == 0:
            abs_benefits[g] = 0
        else:
            now = stats['data'][str(g)][metric]['lowest']
            if str(g - 1) not in stats['data']:
                prev = now
            else:
                prev = stats['data'][str(g - 1)][metric]['lowest']
            abs_benefits[g] = prev - now
    aspect_fcns = {'abs_benefit': (lambda g, d, m: abs_benefits[g])}
    return aspect_fcns

def ft_cost_fcn(g, d, m1, m2, graph):
    '''
    m1 is the metric we use for comparison; m2 is the opponent.
    '''
    m1_opt_combo = d[m1]['lowest_combo']
    m2_opt_combo = d[m2]['lowest_combo']
    apsp = nx.all_pairs_dijkstra_path_length(graph)
    apsp_paths = nx.all_pairs_dijkstra_path(graph)
    weighted = True
    extra_params = None
    m1_opt_m1_value = d[m1]['lowest']
    m2_opt_m1_value = METRIC_FCNS[m1](graph, m2_opt_combo, apsp, apsp_paths, weighted, extra_params)
    print "metric values for %s" % (m1)
    print "  value for combo %s opt for %s: %s" % (m1_opt_combo, m1, m1_opt_m1_value)
    print "  value for combo %s opt for %s: %s" % (m2_opt_combo, m2, m2_opt_m1_value)
    value = divide_def0(m2_opt_m1_value, m1_opt_m1_value)
    print "    return value of: %s for k = %s" % (value, g)
    return value

def other_metric(metric):
    if metric == 'latency':
        other_metric = 'latency_2'
    elif metric == 'latency_2':
        other_metric = 'latency'
    elif metric == 'wc_latency':
        other_metric = 'wc_latency_2'
    elif metric == 'wc_latency_2':
        other_metric = 'wc_latency'
    else:
        raise Exception("not sure what to compare against")
    return other_metric

def ft_cost_aspect_fcns_gen(stats, metric, graph):
    aspect_fcns = {'ft_cost': (lambda g, d, m: ft_cost_fcn(g, d, metric, other_metric(m), graph))}
    return aspect_fcns

# Master dict from plot types to all the info needed to construct them.
# Now in a declarative style because the code duplication became tedious.
# Each plot type can include:
#    aspect_colors: dict from aspect names to color and marker strings
#    aspect_fcns: dict from aspect names to fcns to extract their data
#    aspect_fcns_gen: fcn(stats, metrics) that genreates aspect_fcns
#    ylabel: fcn to generate ylabel, given metric
#    (opt) min/max-*: fcn(options) to generate corresponding value
PLOT_FCNS = {
    'ranges': {
        'aspect_colors':
            {#'highest': 'rx',
             'mean': 'bo',
             'lowest': 'g+'},
        'aspect_fcns':
            {#'highest': (lambda g, d, m: d[m]['highest']),
            'mean': (lambda g, d, m: d[m]['mean']),
            'lowest': (lambda g, d, m: d[m]['lowest'])},
        'ylabel': (lambda m: metric_fullname(m) + " (miles)"),
        'ylabel2': (lambda m: metric_fullname(m) + " (ms)"),
        'y2_scale_factor': MILES_TO_MS
    },
    'miles_cost': {
         'aspect_colors':
            {'miles_cost': 'rx'},
        'aspect_fcns':
            {'miles_cost': (lambda g, d, m: d[m]['lowest']  / float(g))},
        'ylabel': (lambda m: metric_fullname(m) + "\nmiles over cost")
    },
    'ratios': {
        'aspect_colors':
            {#'highest': 'rx',
             'mean': 'bo',
             'one': 'g+'},
        'aspect_fcns':
            {#'highest': (lambda g, d, m: divide_def0(d[m]['highest'], d[m]['lowest'])),
             'mean': (lambda g, d, m: divide_def0(d[m]['mean'], d[m]['lowest'])),
             'one': (lambda g, d, m: 1.0)},
        'ylabel': (lambda m: metric_fullname(m) + "/optimal"),
        'max_x': (lambda o: 12.0),
        'min_y': (lambda o: 1.0),
        'max_y': (lambda o: 2.5)
    },
    'durations': {
        'aspect_colors':
            {'duration': 'rx'},
        'aspect_fcns':
            {'duration': (lambda g, d, m: d[m]['duration'])},
        'ylabel': (lambda m: metric_fullname(m) + "duration (sec)")
    },
    'bc_abs': {
        'aspect_colors':
            {'bc_abs': 'rx'},
        'aspect_fcns_gen': bc_abs_aspect_fcns_gen,
        'ylabel': (lambda m: metric_fullname(m) + "\nabs reduction/k (miles)"),
        'min_x': (lambda o: 2.0)
    },
    'bc_rel': {
        'aspect_colors':
            {'bc_rel': 'rx'},
        'aspect_fcns_gen': bc_rel_aspect_fcns_gen,
#        'ylabel': (lambda m: metric_fullname(m) + "(1) /\n" + metric_fullname(m) + "/k"),
        'ylabel': (lambda m: "cost/benefit ratio for\noptimized " + metric_fullname(m)),
        'min_x': (lambda o: 1.0),
        'max_x': (lambda o: o.maxx),
        'max_y': (lambda o: o.maxy)
    },
    'abs_benefit': {
        'aspect_colors': {'abs_benefit': 'rx'},
        'aspect_fcns_gen': abs_benefit_fcns_gen,
        'ylabel': (lambda m: metric_fullname(m) + "\nincremental abs benefit (miles)"),
        'min_x': (lambda o: 2.0)
    },
    'ft_cost': {
        'aspect_colors':
            {'ft_cost': 'rx'},
        'aspect_fcns_gen_with_graph': ft_cost_aspect_fcns_gen,
        'ylabel': (lambda m: '%s/%s,\nshowing %s' % (other_metric(m), m, m)),
        'min_y': (lambda o: 1.0),
        'min_x': (lambda o: 2.0)
    }
}

def get_aspect_fcns(p, stats, metric, graph):
    '''Return aspect fcns, whether defined as functions or not.'''
    if 'aspect_fcns_gen_with_graph' in p:
        aspect_fcns = p['aspect_fcns_gen_with_graph'](stats, metric, graph)
    elif 'aspect_fcns_gen' in p:
        aspect_fcns = p['aspect_fcns_gen'](stats, metric)
    else:
        aspect_fcns = p['aspect_fcns']
    return aspect_fcns


def do_ranges(options, stats, write_filepath, topo_name):

    # Grab topo to enable analysis that requires generating new metric values,
    # such as the value of one metric with a combo optimized for another one.
    '''
    topo_graph returns
        @param g: NetworkX Graph
        @param usable: boolean: locations on all nodes and connected?
        @param note: error or note about mods
    '''
    print "generating topo for: %s" % topo_name
    graph, usable, note = get_topo_graph(topo_name)
    if not usable:
        raise Exception("unusable graph?")

    if not write_filepath:
        write_filepath = get_output_filepath(options.input)

    for metric in options.metrics:

        this_write_filepath = write_filepath + '_' + metric
        xlabel = 'number of controllers (k)'

        for ptype in options.plots:
            if ptype in PLOT_FCNS.keys():
                p = PLOT_FCNS[ptype]
                #print "plotting %s" % ptype

                filepath = this_write_filepath + '_' + ptype
                aspect_fcns = get_aspect_fcns(p, stats, metric, graph)
                aspects = aspect_fcns.keys()
                aspect_colors = p['aspect_colors']
                ylabel = p['ylabel'](metric)
                min_x = p['min_x'](options) if 'min_x' in p else None
                max_x = p['max_x'](options) if 'max_x' in p else None
                min_y = p['min_y'](options) if 'min_y' in p else None
                max_y = p['max_y'](options) if 'max_y' in p else None
                ylabel2 = p['ylabel2'](metric) if 'ylabel2' in p else None
                y2_scale_factor = p['y2_scale_factor'] if 'y2_scale_factor' in p else None
                hlines = p['hlines'] if 'hlines' in p else None

                plot.ranges(stats, metric, aspects, aspect_colors, aspect_fcns,
                            "linear", "linear", None, None, filepath,
                            options.write, ext = options.ext,
                            xlabel = xlabel,
                            ylabel = ylabel,
                            min_x = min_x,
                            max_x = max_x,
                            min_y = min_y,
                            max_y = max_y,
                            ylabel2 = ylabel2,
                            y2_scale_factor = y2_scale_factor,
                            hlines = hlines)
            else:
                raise Exception("undefined ptype: %s" % ptype)

    if not options.write:
        plot.show()

if __name__ == "__main__":
    options = parse_args()
    print "loading JSON data..."
    stats = plot.load_stats(options)
    topo_name = options.input.split('/')[1]
    do_ranges(options, stats, None, topo_name)