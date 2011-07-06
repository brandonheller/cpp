#!/usr/bin/env python
'''Plot CDFs of latency, where each series is a # of controllers.'''
import math

import lib.plot as plot


def do_cloud():
    options = plot.parse_args()
    print "loading JSON data..."
    stats = plot.load_stats(options)

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
    colors = ["r", "g", "b", "c", "m", "y", "k"]
    write_filepath = options.input
    write_filepath = write_filepath.replace('data_out', 'data_vis')
    write_filepath = write_filepath.replace('.json', '')
    first_data = stats['data'][sorted(stats['group'])[0]]
    axes = [0, first_data[x_metric]['highest'],
            0, first_data[y_metric]['highest']]
    plot.cloud(data, colors, axes,
               "linear", "linear", write_filepath + '_cloud',
               options.write,
               xlabel = x_metric + ' (miles)',
               ylabel = y_metric + ' (miles)',
               ext = options.ext,
               x_metric = x_metric,
               y_metric = y_metric)

    if not options.write:
        plot.show()

if __name__ == "__main__":
    do_cloud()