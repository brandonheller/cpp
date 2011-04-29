#!/usr/bin/env python
# Plot graphs from pre-computed stats files
import json
from optparse import OptionParser
import os

import matplotlib.pyplot as plt
import networkx as nx
import pylab


# Input filename of metrics
DEF_INPUT = 'os3e_link'

# Name of output file
DEF_OUTPUT_DIR = './'

EXT = 'png'


class Plot():
    
    def __init__(self):
        self.parse_args()
        options = self.options
        input_path = options.input + '.json'
        input_file = open(input_path, 'r')
        data = json.load(input_file)
        self.plot_all(data)

    def parse_args(self):
        opts = OptionParser()
        opts.add_option("-i", "--input", type = 'string', 
                        default = DEF_INPUT,
                        help = "name of input file")
        opts.add_option("-o", "--output", type = 'string',
                        default = DEF_OUTPUT_DIR,
                        help = "name of output file")
        opts.add_option("--xmin", type = 'int', default = 0)
        opts.add_option("--xmax", type = 'int', default = 0.02)
        opts.add_option("--ymin", type = 'int', default = 0.9)
        opts.add_option("--ymax", type = 'int', default = 1.001)
        opts.add_option("-w", "--write",  action = "store_true",
                        default = False,
                        help = "write plots, rather than display?")
        options, arguments = opts.parse_args()
        self.options = options

    def gen_dirname(self):
        return self.options.input.split('.')[0]

    def gen_fname(self, name, insert = None):
        if insert:
            return name + '_' + insert + '.' + EXT
        else:
            return name + '.' + EXT

    def plot(self, ptype, data, colors, axes, algs, label, write = False):

        fig = pylab.figure()
        if ptype != 'line':
            raise Exception("invalid plot type")

        if len(colors) < len(data.keys()):
            raise Exception("insufficient color data")

        lines = []
        datanames = []
        for i, gtype in enumerate(algs):
            line = data[gtype]
            x = [d[0] for d in line]
            y = [d[1] for d in line]
            print x, y, colors[i]
            lines.append(pylab.plot(x, y, colors[i]))
            datanames.append(gtype)
        pylab.grid(True)
        xscale = "linear"
        yscale = "linear"
        pylab.xscale(xscale)
        pylab.yscale(yscale)
        pylab.axis(axes)
        pylab.xlabel("p_edge_fail")
        pylab.ylabel("uptime")
        pylab.title(label)
        print data.keys()
        pylab.legend(lines, datanames, loc = "lower right")
        if self.options.write:
            dirname = self.gen_dirname()
            if dirname not in os.listdir('.'):
                os.mkdir(dirname)
                print "created directory:", dirname
            filepath = os.path.join(dirname, self.gen_fname(label))
            fig.savefig(filepath)
        else:
            pylab.show()

    def plot_all(self, data):
        colors = ["r-", "r--", "g-.", "b-"]
        range = [self.options.xmin, self.options.xmax, self.options.ymin, self.options.ymax]
        algs = data.keys()
        print algs
        label = 'os3e'
        self.plot('line', data, colors, range, algs, label, self.options.write)
        
if __name__ == "__main__":
    Plot()
