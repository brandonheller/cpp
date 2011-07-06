#!/usr/bin/env python
'''Plot ranges, where each series is a # of controllers.'''
import lib.plot as plot

PLOTS = ['ranges', 'ratios', 'durations', 'bc_abs', 'bc_rel']

def divide(left, right):
    if right == 0:
        return 0.0
    else:
        return (left / float(right))


def do_ranges():
    options = plot.parse_args()
    print "loading JSON data..."
    stats = plot.load_stats(options)

    for metric in options.metrics:

        write_filepath = options.input + '_' + metric
        write_filepath = write_filepath.replace('data_out', 'data_vis')
        write_filepath = write_filepath.replace('.json', '')

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
                        "linear", "linear", None, None, write_filepath + '_ranges',
                        options.write, ext = options.ext,
                        xlabel = 'number of controllers',
                        ylabel = metric + " (miles)")

        if 'ratios' in PLOTS:
            aspect_colors = {'highest': 'rx',
                             'mean': 'bo',
                             'one': 'g+'}
            aspect_fcns = {'highest': (lambda g, d, m: divide(d[m]['highest'], d[m]['lowest'])),
                           'mean': (lambda g, d, m: divide(d[m]['mean'], d[m]['lowest'])),
                           'one': (lambda g, d, m: 1.0)}
            aspects = aspect_fcns.keys()
            plot.ranges(stats, metric, aspects, aspect_colors, aspect_fcns,
                        "linear", "linear", None, None, write_filepath + '_ratios',
                        options.write, ext = options.ext,
                        xlabel = 'number of controllers',
                        ylabel = metric + " ratio")
    
        if 'durations' in PLOTS:
            aspect_colors = {'duration': 'rx'}
            aspect_fcns = {'duration': (lambda g, d, m: d[m]['duration'])}
            aspects = aspect_fcns.keys()
            plot.ranges(stats, metric, aspects, aspect_colors, aspect_fcns,
                        "linear", "linear", None, None, write_filepath + '_durations',
                        options.write, ext = options.ext,
                        xlabel = 'number of controllers',
                        ylabel = "duration (sec)")

        if 'bc_abs' in PLOTS:
            aspect_colors = {'bc_abs': 'rx'}
            value_one = stats['data'][sorted(stats['group'])[0]][metric]['lowest']
            aspect_fcns = {'bc_abs': (lambda g, d, m: (value_one - d[m]['lowest']) / max(1, (float(g) - 1)))}
            aspects = aspect_fcns.keys()
            plot.ranges(stats, metric, aspects, aspect_colors, aspect_fcns,
                        "linear", "linear", None, None, write_filepath + '_bc_abs',
                        options.write, ext = options.ext,
                        xlabel = 'number of controllers',
                        ylabel = metric + " benefit/cost (miles)", min_x = 2)

        if 'bc_rel' in PLOTS:
            aspect_colors = {'bc_rel': 'rx'}
            value_one = stats['data'][sorted(stats['group'])[0]][metric]['lowest']
            aspect_fcns = {'bc_rel': (lambda g, d, m: divide(value_one, float(d[m]['lowest'])) / float(g))}
            aspects = aspect_fcns.keys()
            plot.ranges(stats, metric, aspects, aspect_colors, aspect_fcns,
                        "linear", "linear", None, None, write_filepath + '_bc_rel',
                        options.write, ext = options.ext,
                        xlabel = 'number of controllers',
                        ylabel = metric + " benefit/cost (ratio)", min_x = 1)

    if not options.write:
        plot.show()

if __name__ == "__main__":
    do_ranges()