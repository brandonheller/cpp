#!/usr/bin/env python
'''Plot CDFs of latency, where each series is a # of controllers.'''
import math

import lib.plot as plot


def do_pareto():
    options = plot.parse_args()
    print "loading JSON data..."
    stats = plot.load_stats(options)

    assert len(options.metrics) == 2
    x_metric, y_metric = options.metrics
    print "reformatting data..."
    data = {}
    for i, g in enumerate(stats['group']):
        if options.max and i >= options.max:
            break
        data[g] = [d for d in stats['data'][g]["distribution"]]

    print "plotting point pareto"
    colors = ["r", "g", "b", "c", "m", "y", "k"]
    write_filepath = options.input
    write_filepath = write_filepath.replace('data_out', 'data_vis')
    write_filepath = write_filepath.replace('.json', '')
    plot.pareto(data, colors, None,
               "linear", "linear", write_filepath + '_pareto',
               options.write,
               xlabel = x_metric + ' (miles)',
               ylabel = y_metric + ' (miles)',
               ext = options.ext,
               x_metric = x_metric,
               y_metric = y_metric,
               min_x = 0,
               min_y = 0)

    plot.pareto(data, colors, None,
               "linear", "linear", write_filepath + '_pareto_zoom',
               options.write,
               xlabel = x_metric + ' (miles)',
               ylabel = y_metric + ' (miles)',
               ext = options.ext,
               x_metric = x_metric,
               y_metric = y_metric)

    plot.pareto(data, colors, None,
               "linear", "linear", write_filepath + '_pareto_norm',
               options.write,
               xlabel = x_metric + ' (miles)',
               ylabel = y_metric + ' (miles)',
               ext = options.ext,
               x_metric = x_metric,
               y_metric = y_metric,
               normalize = True)

    if not options.write:
        plot.show()

if __name__ == "__main__":
    do_pareto()