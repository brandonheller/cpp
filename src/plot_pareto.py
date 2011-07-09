#!/usr/bin/env python
'''Plot CDFs of latency, where each series is a # of controllers.'''
import math

import lib.plot as plot
from lib.colors import COLORS
from metrics_lib import metric_fullname, get_output_filepath


def do_pareto(options, stats, write_filepath):

    assert len(options.metrics) == 2
    x_metric, y_metric = options.metrics
    print "reformatting data..."
    data = {}
    for i, g in enumerate(stats['group']):
        if options.max and i >= options.max:
            break
        data[g] = [d for d in stats['data'][g]["distribution"]]

    print "plotting point pareto"
    if not write_filepath:
        write_filepath = get_output_filepath(options.input)
    write_filepath += '_pareto'
    plot.pareto(data, COLORS, None,
               "linear", "linear", write_filepath,
               options.write,
               xlabel = metric_fullname(x_metric) + ' (miles)',
               ylabel = metric_fullname(y_metric) + ' (miles)',
               ext = options.ext,
               x_metric = x_metric,
               y_metric = y_metric,
               min_x = 0,
               min_y = 0)

    plot.pareto(data, COLORS, None,
               "linear", "linear", write_filepath + '_zoom',
               options.write,
               xlabel = metric_fullname(x_metric) + ' (miles)',
               ylabel = metric_fullname(y_metric) + ' (miles)',
               ext = options.ext,
               x_metric = x_metric,
               y_metric = y_metric)

    plot.pareto(data, COLORS, None,
               "linear", "linear", write_filepath + '_norm',
               options.write,
               xlabel = metric_fullname(x_metric) + ' (miles)',
               ylabel = metric_fullname(y_metric) + ' (miles)',
               ext = options.ext,
               x_metric = x_metric,
               y_metric = y_metric,
               normalize = True)

    if not options.write:
        plot.show()

if __name__ == "__main__":
    options = plot.parse_args()
    print "loading JSON data..."
    stats = plot.load_stats(options)
    do_pareto(options, stats, None)