#!/usr/bin/env python
'''Plot ranges, where each series is a # of controllers.'''
from lib.options import parse_args
import lib.plot as plot
from metrics_lib import metric_fullname, get_output_filepath

PLOTS = ['ranges', 'ratios', 'durations', 'bc_abs', 'bc_rel', 'abs_benefit', 'miles_cost']


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

        if 'ranges' in PLOTS:
            print "plotting ranges"
            aspect_colors = {'highest': 'rx',
                             'mean': 'bo',
                             'lowest': 'g+'}
            aspect_fcns = {'highest': (lambda g, d, m: d[m]['highest']),
                           'mean': (lambda g, d, m: d[m]['mean']),
                           'lowest': (lambda g, d, m: d[m]['lowest'])}
            aspects = aspect_fcns.keys()
            plot.ranges(stats, metric, aspects, aspect_colors, aspect_fcns,
                        "linear", "linear", None, None, this_write_filepath + '_ranges',
                        options.write, ext = options.ext,
                        xlabel = xlabel,
                        ylabel = metric_fullname(metric) + " (miles)")

        if 'miles_cost' in PLOTS:
            print "plotting ranges"
            aspect_colors = {'miles_cost': 'rx'}
            aspect_fcns = {'miles_cost': (lambda g, d, m: d[m]['lowest']  / float(g))}
            aspects = aspect_fcns.keys()
            plot.ranges(stats, metric, aspects, aspect_colors, aspect_fcns,
                        "linear", "linear", None, None, this_write_filepath + '_miles_cost',
                        options.write, ext = options.ext,
                        xlabel = xlabel,
                        ylabel = metric_fullname(metric) + "\nmiles over cost")

        if 'ratios' in PLOTS:
            aspect_colors = {'highest': 'rx',
                             'mean': 'bo',
                             'one': 'g+'}
            aspect_fcns = {'highest': (lambda g, d, m: divide(d[m]['highest'], d[m]['lowest'])),
                           'mean': (lambda g, d, m: divide(d[m]['mean'], d[m]['lowest'])),
                           'one': (lambda g, d, m: 1.0)}
            aspects = aspect_fcns.keys()
            plot.ranges(stats, metric, aspects, aspect_colors, aspect_fcns,
                        "linear", "linear", None, None, this_write_filepath + '_ratios',
                        options.write, ext = options.ext,
                        xlabel = xlabel,
                        ylabel = metric_fullname(metric) + "/optimal",
                        max_y = 10.0)
    
        if 'durations' in PLOTS:
            aspect_colors = {'duration': 'rx'}
            aspect_fcns = {'duration': (lambda g, d, m: d[m]['duration'])}
            aspects = aspect_fcns.keys()
            plot.ranges(stats, metric, aspects, aspect_colors, aspect_fcns,
                        "linear", "linear", None, None, this_write_filepath + '_durations',
                        options.write, ext = options.ext,
                        xlabel = xlabel,
                        ylabel = "duration (sec)")

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

        if 'bc_rel' in PLOTS:
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

        if 'abs_benefit' in PLOTS:
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


    if not options.write:
        plot.show()

if __name__ == "__main__":
    options = parse_args()
    print "loading JSON data..."
    stats = plot.load_stats(options)
    do_ranges(options, stats, None)