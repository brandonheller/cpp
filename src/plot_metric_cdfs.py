#!/usr/bin/env python
'''Plot CDFs of latency, where each series is a # of controllers.'''
import os
from optparse import OptionParser
import json
import math

import plot


# Highest number of controllers to plot.
DEF_MAX = 2

# Weighted or not?
DEF_WEIGHTED = True

# Metric to plot
METRICS = ['latency', 'fairness']
DEF_METRIC = 'latency'

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

    return options


def load_stats(options):
    options = parse_args()
    input_path = os.path.join(options.input_dir, options.input + '.json')
    input_file = open(input_path, 'r')
    stats = json.load(input_file)
    return stats


def do_plot():
    options = parse_args()
    stats = load_stats(options)
    data = {}
    for i in range(1, options.max + 1):
        data[str(i)] = [d[options.metric] for d in stats['data'][str(i)]["distribution"]]
    colors = ["r-", "r--", "g-.", "b-", "g--"]
    write_filepath = os.path.join(options.output_dir, options.input)
    plot.plot('cdf', data, colors, [0, round(math.ceil(max(data["1"]))), 0, 1],
              options.metric, "linear", "linear", write_filepath, options.write)

if __name__ == "__main__":
    do_plot()