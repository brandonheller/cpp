#!/usr/bin/env python
'''Plot CDFs of latency, where each series is a # of controllers.'''
import lib.plot as plot


def do_ranges():
    options = plot.parse_args()
    print "loading JSON data..."
    stats = plot.load_stats(options)

    write_filepath = options.input + '_' + options.metric
    write_filepath = write_filepath.replace('.json', '')

    # Plot raw values
    print "plotting ranges"
    aspect_colors = {'highest': 'rx',
                     'mean': 'bo',
                     'lowest': 'g+'}
    aspect_fcns = {'highest': (lambda d, m: d[m]['highest']),
                   'mean': (lambda d, m: d[m]['mean']),
                   'lowest': (lambda d, m: d[m]['lowest'])}
    aspects = aspect_fcns.keys()
    plot.ranges(stats, options.metric, aspects, aspect_colors, aspect_fcns,
                "linear", "linear", None, None, write_filepath + '_ranges',
                options.write, ext = options.ext,
                xlabel = 'number of controllers',
                ylabel = options.metric + " miles")

    # Plot ratios
    aspect_colors = {'highest': 'rx',
                     'mean': 'bo',
                     'one': 'g+'}
    aspect_fcns = {'highest': (lambda d, m: d[m]['highest'] / d[m]['lowest']),
                   'mean': (lambda d, m: d[m]['mean'] / d[m]['lowest']),
                   'one': (lambda d, m: 1.0)}
    aspects = aspect_fcns.keys()
    plot.ranges(stats, options.metric, aspects, aspect_colors, aspect_fcns,
                "linear", "linear", None, None, write_filepath + '_ratios',
                options.write, ext = options.ext,
                xlabel = 'number of controllers',
                ylabel = options.metric + " ratio")

    # Plot ratios
    aspect_colors = {'duration': 'rx'}
    aspect_fcns = {'duration': (lambda d, m: d[m]['duration'])}
    aspects = aspect_fcns.keys()
    plot.ranges(stats, options.metric, aspects, aspect_colors, aspect_fcns,
                "linear", "linear", None, None, write_filepath + '_durations',
                options.write, ext = options.ext,
                xlabel = 'number of controllers',
                ylabel = "duration (sec)")

    if not options.write:
        plot.show()

if __name__ == "__main__":
    do_ranges()