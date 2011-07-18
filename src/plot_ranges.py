#!/usr/bin/env python
'''Plot ranges, where each series is a # of controllers.'''
from lib.options import parse_args
import lib.plot as plot
from metrics_lib import metric_fullname, get_output_filepath
from util import divide_def0

PLOT_TYPES = ['ranges', 'ratios', 'durations', 'bc_abs', 'bc_rel', 'abs_benefit', 'miles_cost']
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
            {'highest': 'rx',
             'mean': 'bo',
             'lowest': 'g+'},
        'aspect_fcns':
            {'highest': (lambda g, d, m: d[m]['highest']),
            'mean': (lambda g, d, m: d[m]['mean']),
            'lowest': (lambda g, d, m: d[m]['lowest'])},
        'ylabel': (lambda m: metric_fullname(m) + " (miles)")
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
            {'highest': 'rx',
             'mean': 'bo',
             'one': 'g+'},
        'aspect_fcns':
            {'highest': (lambda g, d, m: divide_def0(d[m]['highest'], d[m]['lowest'])),
             'mean': (lambda g, d, m: divide_def0(d[m]['mean'], d[m]['lowest'])),
             'one': (lambda g, d, m: 1.0)},
        'ylabel': (lambda m: metric_fullname(m) + "/optimal"),
        'max_y': (lambda o: 10.0)
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
        'ylabel': (lambda m: metric_fullname(m) + "(1) /\n" + metric_fullname(m) + "/k"),
        'min_x': (lambda o: 1.0),
        'max_x': (lambda o: o.maxx),
        'max_y': (lambda o: o.maxy)
    },
    'abs_benefit': {
         'aspect_colors': {'abs_benefit': 'rx'},
         'aspect_fcns_gen': abs_benefit_fcns_gen,
         'ylabel': (lambda m: metric_fullname(m) + "\nincremental abs benefit (miles)"),
         'min_x': (lambda o: 2.0)
    }
}

def get_aspect_fcns(p, stats, metric):
    '''Return aspect fcns, whether defined as functions or not.'''
    if 'aspect_fcns_gen' in p:
        aspect_fcns = p['aspect_fcns_gen'](stats, metric)
    else:
        aspect_fcns = p['aspect_fcns']
    return aspect_fcns


def do_ranges(options, stats, write_filepath):

    if not write_filepath:
        write_filepath = get_output_filepath(options.input)

    for metric in options.metrics:

        this_write_filepath = write_filepath + '_' + metric
        xlabel = 'number of controllers (k)'

        for ptype in PLOTS:
            if ptype in PLOT_FCNS.keys():
                p = PLOT_FCNS[ptype]
                #print "plotting %s" % ptype

                filepath = this_write_filepath + '_' + ptype
                aspect_fcns = get_aspect_fcns(p, stats, metric)
                aspects = aspect_fcns.keys()
                aspect_colors = p['aspect_colors']
                ylabel = p['ylabel'](metric)
                min_x = p['min_x'](options) if 'min_x' in p else None
                max_x = p['max_x'](options) if 'max_x' in p else None
                min_y = p['min_y'](options) if 'min_y' in p else None
                max_y = p['max_y'](options) if 'max_y' in p else None

                plot.ranges(stats, metric, aspects, aspect_colors, aspect_fcns,
                            "linear", "linear", None, None, filepath,
                            options.write, ext = options.ext,
                            xlabel = xlabel,
                            ylabel = ylabel,
                            min_x = min_x,
                            max_x = max_x,
                            min_y = min_y,
                            max_y = max_y)
            else:
                raise Exception("undefined ptype: %s" % ptype)

    if not options.write:
        plot.show()

if __name__ == "__main__":
    options = parse_args()
    print "loading JSON data..."
    stats = plot.load_stats(options)
    do_ranges(options, stats, None)