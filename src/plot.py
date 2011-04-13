#!/usr/bin/env python
# Plot graphs from pre-computed stats files
import json
from optparse import OptionParser
import os

import matplotlib.pyplot as plt
import networkx as nx
import pylab


# Input filename of metrics
DEF_INPUT = 'uptimes_link'

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
        opts.add_option("-w", "--write",  action = "store_true",
                        default = False,
                        help = "write plots, rather than display?")
        options, arguments = opts.parse_args()
        self.options = options

    def plot(self, ptype, data, color, axes, label, xscale, yscale, write = False):

        def gen_dirname():
            return self.options.input.split('.')[0]

        def gen_fname(name, insert):
            return name + '_' + insert + '.' + EXT

        fig = pylab.figure()
        if ptype == 'line':
            x = [d[0] for d in data]
            y = [d[1] for d in data]        
        else:
            raise Exception("invalid plot type")
        l1 = pylab.plot(x, y, color)
        #l2 = pylab.plot(range(1,BINS), results_one_queue[6], "r--")
        #l3 = pylab.plot(range(1,BINS), results_two_queue[6], "g-.")
        pylab.grid(True)
        pylab.xscale(xscale)
        pylab.yscale(yscale)
        pylab.axis(axes)
        pylab.xlabel("value")
        pylab.ylabel(ptype)
        pylab.title(label)
        #pylab.legend((l1,l2,l3), ("no congestion","one congestion point","two congestion points"),"lower right")
        if self.options.write:
            dirname = gen_dirname()
            if dirname not in os.listdir('.'):
                os.mkdir(dirname)
                print "created directory:", dirname
            filepath = os.path.join(dirname, dirname + '_' + gen_fname(label, xscale + '_' + yscale + '_' + ptype))
            fig.savefig(filepath)
        else:
            pylab.show()

    def plot_all(self, data):
        for alg in data.keys():
            for gtype in data[alg].keys():
                self.plot('line', data[alg][gtype], "r-", [0, 10, 0, 1.0], "_".join([alg, gtype]), "linear", "linear", self.options.write)
        
if __name__ == "__main__":
    Plot()
