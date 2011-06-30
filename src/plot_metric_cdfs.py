#!/usr/bin/env python
'''Plot CDFs of latency, where each series is a # of controllers.'''
import os
from optparse import OptionParser
import json
import math

import plot
import metrics_lib as metrics

# Highest number of controllers to plot.  If none, plot all.
DEF_MAX = None

# Weighted or not?
DEF_WEIGHTED = True

# Metric to plot
METRICS = metrics.METRICS
DEF_METRIC = metrics.METRICS[0]

DEF_INPUT_DIR = 'data_out'
DEF_OUTPUT_DIR = DEF_INPUT_DIR


def parse_args():
    opts = OptionParser()
    opts.add_option("-i", "--input", type = 'string', 
                    default = None,
                    help = "name of input file")
    opts.add_option("--input_dir", type = 'string',
                    default = DEF_INPUT_DIR,
                    help = "name of input dir")
    opts.add_option("--max", type = 'int', default = DEF_MAX,
                    help = "highest number of controllers to plot %s" % METRICS)
    opts.add_option("--minx", type = 'float', default = None,
                    help = "min X axis value")
    opts.add_option("--maxx", type = 'float', default = None,
                    help = "min X axis value")
    opts.add_option("--metric",
                    default = DEF_METRIC,
                    choices = METRICS,
                    help = "metric to show, one in %s" % METRICS)
    opts.add_option("-o", "--output_dir", type = 'string',
                    default = DEF_OUTPUT_DIR,
                    help = "name of output file")
    opts.add_option("-w", "--write",  action = "store_true",
                    default = False,
                    help = "write plots, rather than display?")
    opts.add_option("--weighted",  action = "store_true",
                    default = False,
                    help = "used weighted input graph?")
    options, arguments = opts.parse_args()

    # Input filename of metrics
    if not options.input:
        input = 'os3e_'
        if options.weighted:
            input += 'weighted_'
        else:
            input += 'unweighted_'
        input += str(options.max) + '_0'
        options.input = input
        options.input = os.path.join(options.input_dir, options.input + '.json')

    return options


def load_stats(options):
    options = parse_args()
    input_file = open(options.input, 'r')
    stats = json.load(input_file)
    return stats


def do_plot():
    options = parse_args()
    print "loading JSON data..."
    stats = load_stats(options)
    data = {}

    print "reformatting data..."
    for i, g in enumerate(stats['group']):
        if options.max and i >= options.max:
            break
        data[str(g)] = [d[options.metric] for d in stats['data'][str(g)]["distribution"]]

    print "doing plot"
    colors = ["r-", "g--", "b-.", "c-", "m--", "y-.", "k--"]
    write_filepath = options.input + '_' + options.metric
    xmax = round(math.ceil(max(data[str(stats['group'][0])])))
    axis_limits = [0, xmax, 0, 1]
    if options.minx:
        axis_limits[0] = options.minx
    if options.maxx:
        axis_limits[1] = options.maxx
    plot.plot('cdf', data, colors, axis_limits,
              options.metric, "linear", "linear", write_filepath, options.write,
              xlabel = options.metric, ylabel = 'fraction (CDF)')

if __name__ == "__main__":
    do_plot()