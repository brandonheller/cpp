#!/usr/bin/env python
'''Plot ranges, where each series is a # of controllers.'''
from lib.options import parse_args
import lib.plot as plot
from metrics_lib import metric_fullname, get_output_filepath

PLOT_TYPES = ['ranges', 'ratios', 'durations', 'bc_abs', 'bc_rel', 'abs_benefit', 'miles_cost']
PLOTS = PLOT_TYPES

# Master dict from plot types to all the info needed to construct them.
# Now in a declarative style because the code duplication became tedious.
# Each plot type can include:
#    aspect_colors: dict from aspect names to color and marker strings
#    aspect_fcns: dict from aspect names to fcns to extract their data
#    ylabel: fcn to generate ylabel, given metric
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
            {'highest': (lambda g, d, m: divide(d[m]['highest'], d[m]['lowest'])),
             'mean': (lambda g, d, m: divide(d[m]['mean'], d[m]['lowest'])),
             'one': (lambda g, d, m: 1.0)},
        'ylabel': (lambda m: metric_fullname(m) + "/optimal"),
        'max_y': 10.0
    },
    'durations': {
        'aspect_colors':
            {'duration': 'rx'},
        'aspect_fcns':
            {'duration': (lambda g, d, m: d[m]['duration'])},
        'ylabel': (lambda m: metric_fullname(m) + "duration (sec)")
    }
}


def divide(left, right):
    if right == 0:
        return 0.0
    else:
        return (left / float(right))


def do_ranges(options, stats, write_filepath):

    if not write_filepath:
        write_filepath = get_output_filepath(options.input)

    for metric in options.metrics:

        this_write_filepath = write_filepath + '_' + metric
        xlabel = 'number of controllers (k)'

        for ptype in PLOTS:
            if ptype in PLOT_FCNS.keys():
                p = PLOT_FCNS[ptype]
                print "plotting %s" % ptype

                filepath = this_write_filepath + '_' + ptype
                aspects = p['aspect_fcns'].keys()
                aspect_fcns = p['aspect_fcns']
                aspect_colors = p['aspect_colors']
                ylabel = p['ylabel'](this_write_filepath)
                max_y = p['max_y'] if 'max_y' in p else None

                plot.ranges(stats, metric, aspects, aspect_colors, aspect_fcns,
                            "linear", "linear", None, None, filepath,
                            options.write, ext = options.ext,
                            xlabel = xlabel,
                            ylabel = ylabel,
                            max_y = max_y)
    
            if 'bc_abs' in PLOTS:
                aspect_colors = {'bc_abs': 'rx'}
                value_one = stats['data'][sorted(stats['group'])[0]][metric]['lowest']
                aspect_fcns = {'bc_abs': (lambda g, d, m: (value_one - d[m]['lowest']) / max(1, (float(g) - 1)))}
                aspects = aspect_fcns.keys()
                plot.ranges(stats, metric, aspects, aspect_colors, aspect_fcns,
                            "linear", "linear", None, None, this_write_filepath + '_bc_abs',
                            options.write, ext = options.ext,
                            xlabel = xlabel,
                            ylabel = metric_fullname(metric) + "\nabs reduction/k (miles)", min_x = 2)
    
            elif 'bc_rel' in PLOTS:
                aspect_colors = {'bc_rel': 'rx'}
                value_one = stats['data'][sorted(stats['group'])[0]][metric]['lowest']
                aspect_fcns = {'bc_rel': (lambda g, d, m: divide(value_one, float(d[m]['lowest'])) / float(g))}
                aspects = aspect_fcns.keys()
                plot.ranges(stats, metric, aspects, aspect_colors, aspect_fcns,
                            "linear", "linear", None, None, this_write_filepath + '_bc_rel',
                            options.write, ext = options.ext,
                            xlabel = xlabel,
                            ylabel = metric_fullname(metric) + "(1) /\n" + metric_fullname(metric) + "/k", min_x = 1,
                            max_x = options.maxx, max_y = options.maxy)
    
            elif 'abs_benefit' in PLOTS:
                aspect_colors = {'abs_benefit': 'rx'}
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
                aspects = aspect_fcns.keys()
                plot.ranges(stats, metric, aspects, aspect_colors, aspect_fcns,
                            "linear", "linear", None, None, this_write_filepath + '_abs_benefits',
                            options.write, ext = options.ext,
                            xlabel = xlabel,
                            ylabel = metric_fullname(metric) + "\nincremental abs benefit (miles)", min_x = 2)
            else:
                raise Exception("undefined ptype: %s" % ptype)

    if not options.write:
        plot.show()

if __name__ == "__main__":
    options = parse_args()
    print "loading JSON data..."
    stats = plot.load_stats(options)
    do_ranges(options, stats, None)