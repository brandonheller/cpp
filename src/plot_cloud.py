#!/usr/bin/env python
'''Plot CDFs of latency, where each series is a # of controllers.'''
import math

import lib.plot as plot
from lib.colors import COLORS
from metrics_lib import metric_fullname, get_output_filepath

def do_cloud(options, stats, write_filepath, ext = None):

    assert len(options.metrics) == 2
    x_metric, y_metric = options.metrics
    print "reformatting data..."
    metrics = [x_metric, y_metric]
    data = {}
    for i, g in enumerate(stats['group']):
        if options.max and i >= options.max:
            break
        data[g] = [d for d in stats['data'][g]["distribution"]]

    print "plotting point cloud"

    if not write_filepath:
        write_filepath = get_output_filepath(options.input)

    first_data = stats['data'][sorted(stats['group'])[0]]
    axes = [0, first_data[x_metric]['highest'],
            0, first_data[y_metric]['highest']]
    if not ext:
        ext = options.ext
    plot.cloud(data, COLORS, axes,
               "linear", "linear", write_filepath + '_cloud',
               options.write,
               xlabel = metric_fullname(x_metric) + ' (miles)',
               ylabel = metric_fullname(y_metric) + ' (miles)',
               ext = ext,
               x_metric = x_metric,
               y_metric = y_metric)

    if not options.write:
        plot.show()

if __name__ == "__main__":
    options = plot.parse_args()
    print "loading JSON data..."
    stats = plot.load_stats(options)
    do_cloud(options, stats, None)