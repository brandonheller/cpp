#!/usr/bin/env python
'''Plot CDFs of latency, where each series is a # of controllers.'''
import os
from optparse import OptionParser
import json
import math

import plot

# Highest number of controllers to plot
MAX = 5

# Weighted or not?
WEIGHTED = True

# Input filename of metrics
DEF_INPUT = 'os3e_latencies_'
if WEIGHTED:
    DEF_INPUT += 'weighted_'
else:
    DEF_INPUT += 'unweighted_'
DEF_INPUT += str(MAX) + '_0'

DEF_INPUT_DIR = 'data_out'

# Name of output file
DEF_OUTPUT_DIR = 'data_out'


def parse_args():
    opts = OptionParser()
    opts.add_option("-i", "--input", type = 'string', 
                    default = DEF_INPUT,
                    help = "name of input file")
    opts.add_option("--input_dir", type = 'string',
                    default = DEF_INPUT_DIR,
                    help = "name of input dir")
    opts.add_option("-o", "--output_dir", type = 'string',
                    default = DEF_OUTPUT_DIR,
                    help = "name of output file")
    opts.add_option("-w", "--write",  action = "store_true",
                    default = False,
                    help = "write plots, rather than display?")
    options, arguments = opts.parse_args()
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
    for i in range(1, MAX + 1):
        data[str(i)] = [d["latency"] for d in stats[str(i)]["distribution"]]
    colors = ["r-", "r--", "g-.", "b-", "g--"]
    write_filepath = os.path.join(options.output_dir, options.input)
    plot.plot('cdf', data, colors, [0, round(math.ceil(max(data["1"]))), 0, 1],
              "Latency", "linear", "linear", write_filepath, options.write)

if __name__ == "__main__":
    do_plot()