#!/usr/bin/env python
'''Plot CDFs of latency, where each series is a # of controllers.'''
import lib.plot as plot
from lib.colors import COLORS
from metrics_lib import metric_fullname, get_output_filepath
from lib.options import parse_args

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

    # Series may not have values that monotonically decrease by the controller
    # number, so consider each value when choosing axis extents.
    extra_margin = 1.02
    maxes = {x_metric: [], y_metric: []}
    for c in stats['group']:
        for metric in options.metrics:
            maxes[metric].append(stats['data'][c][metric]['highest'])
    axes = [0, max(maxes[x_metric]) * extra_margin, 0, max(maxes[y_metric]) * extra_margin]
    if not ext:
        ext = options.ext
    plot.cloud(data, COLORS, axes,
               "linear", "linear", write_filepath + '_cloud_' + ','.join(options.metrics),
               options.write,
               xlabel = metric_fullname(x_metric) + ' (miles)',
               ylabel = metric_fullname(y_metric) + ' (miles)',
               ext = ext,
               x_metric = x_metric,
               y_metric = y_metric,
               legend = True)

    if not options.write:
        plot.show()

if __name__ == "__main__":
    options = parse_args()
    print "loading JSON data..."
    stats = plot.load_stats(options)
    do_cloud(options, stats, None)