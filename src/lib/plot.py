#!/usr/bin/env python
'''Generic cdf/pdf/ccdf plotting functions.'''
from optparse import OptionParser
import os
import json

# See http://matplotlib.sourceforge.net/users/customizing.html

from matplotlib import rc, rcParams

# yet another attempt:
rc('font',**{'family':'sans-serif','sans-serif':['Arial']})

#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
# Computer Modern Roman, Palatino...
# Example at http://www.scipy.org/Cookbook/Matplotlib/UsingTex"
ESCAPE = False
# Why does this look like crap?
#rc('font', **{'family':'sans-serif','sans-serif':['Helvetica'],'size':28})
#rc('font', **{'family':'serif','serif':['Computer Modern Roman'],'size':28})
#rc('text', usetex=True)

rc('axes', **{'labelsize' : 'large',
              'titlesize' : 'large',
              'linewidth' : 0,
              'grid' : True})
rcParams['axes.labelsize'] = 20
rcParams['xtick.labelsize'] = 18
rcParams['ytick.labelsize'] = 18
rcParams['xtick.major.pad'] = 4
rcParams['ytick.major.pad'] = 6
rcParams['figure.subplot.bottom'] = 0.15
rcParams['figure.subplot.left'] = 0.165
rcParams['figure.subplot.right'] = 0.95
rcParams['lines.linewidth'] = 2
rcParams['grid.color'] = '#cccccc'
rcParams['grid.linewidth'] = 0.6


import matplotlib.pyplot as plt
import networkx as nx
import pylab

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

DEF_EXT = 'png'


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
    opts.add_option("-e", "--ext", type = 'string',
                    default = DEF_EXT,
                    help = "file extension")
    opts.add_option("--metric",
                    default = DEF_METRIC,
                    choices = METRICS,
                    help = "metric to show, one in %s" % METRICS)
    opts.add_option("--metric_list", type = 'string',
                    default = None,
                    help = "metrics to show, from %s" % METRICS)
    opts.add_option("-o", "--output_dir", type = 'string',
                    default = DEF_OUTPUT_DIR,
                    help = "name of output file")
    opts.add_option("-w", "--write",  action = "store_true",
                    default = False,
                    help = "write plots, rather than display?")
    opts.add_option("-l", "--labels",  action = "store_true",
                    default = False,
                    help = "write labels to images (map_combo only)?")
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

    if options.metric_list:
        metrics_split = options.metric_list.split(',')
        options.metrics = []
        for metric in metrics_split:
            if metric not in METRICS:
                raise Exception("Invalid metric(s): %s in %s; choose from %s" %
                                (metric, options.metric_list, METRICS))
            options.metrics.append(metric)

    if (options.metric != DEF_METRIC) and options.metric_list:
        raise Exception("Can't specify both --metric and --metric_list")

    if options.metric and not options.metric_list:
        options.metrics = [options.metric]

    return options


def load_stats(options):
    input_file = open(options.input, 'r')
    stats = json.load(input_file)
    return stats


def escape(s):
    '''Backslash-escape underscores to use LaTeX output.'''
    s_escaped = ""
    for i, letter in enumerate(s):
        if letter == '_':
            s_escaped += '\\'
        s_escaped += letter
    return s_escaped

def ranges(stats, metric, aspects, aspect_colors, aspect_fcns,
           xscale, yscale, label = None, axes = None,
           write_filepath = None, write = False, ext = 'pdf',
           legend = None, title = False, xlabel = None, ylabel = None,
           min_x = None):

    fig = pylab.figure()
    fig.set_size_inches(6, 4)

    # Build lines
    lines = {}
    x = sorted([int(a) for a in stats['group']])
    for g in x:
        data_agg = stats['data'][str(g)]
        for aspect, fcn in aspect_fcns.iteritems():
            assert aspect in aspects
            if aspect not in lines:
                lines[aspect] = []
            lines[aspect].append(fcn(g, data_agg, metric))
    #print lines


    for aspect in aspects:
        y = lines[aspect]
        pylab.plot(x, y, aspect_colors[aspect], linestyle = '-', linewidth = 1)

    pylab.grid(True)
    pylab.xscale(xscale)
    pylab.yscale(yscale)
    if axes:
        pylab.axis(axes)
    else:
        if not min_x:
            min_x = int(min(x))
        min_y = min([min(lines[aspect]) for aspect in aspects])
        max_y = max([max(lines[aspect]) for aspect in aspects])
        # Assume these are string-ified nums of controllers.
        axes = [min_x, int(max(x)), 0, max_y]
        pylab.axis(axes)
    if xlabel:
        pylab.xlabel(xlabel)
    if ylabel:
        pylab.ylabel(ylabel)
    if title:
        if ESCAPE:
            pylab.title(escape(label))
        else:
            pylab.title(label)
    if legend:
        pylab.legend(lines, aspect, loc = "lower right")
    if write:
        filepath = write_filepath + '.' + ext
        fig.savefig(filepath)
        print "wrote file to %s" % filepath
    else:
        #pylab.show()
        pass


def plot(ptype, data, colors, axes, label, xscale, yscale,
         write_filepath = None, write = False, num_bins = None, ext = 'pdf',
         legend = None, title = False, xlabel = None, ylabel = None):

    fig = pylab.figure()
    fig.set_size_inches(6, 4)
    lines = []
    datanames = []

    if ptype == 'cdf':
        index = 0
        for key in sorted(data.keys()):
            val = data[key]
            x = sorted(val)
            y = [(float(i + 1) / len(x)) for i in range(len(x))]
            lines.append(pylab.plot(x, y, colors[index]))
            datanames.append(key)
            index += 1
#    elif ptype == 'ccdf':
#        x = sorted(data)
#        y = [1.0 - (float(i + 1) / len(x)) for i in range(len(x))]
#    elif ptype == 'pdf':
#        # bin data by value
#        hist = {}
#        data_max = max(data)
#        # use all bins if our data is integers
#        if data_max == int(data_max):
#            num_bins = data_max
#        else:
#            num_bins = 1000
#        for d in data:
#            bin = int((float(d) * num_bins) / float(data_max))
#            if bin not in hist:
#                hist[bin] = 1
#            else:
#                hist[bin] += 1
#
#        x = []
#        y = []
#        for i in range(num_bins + 1):
#            range_lo = float(i) / float(num_bins) * data_max
#            range_hi = float(i + 1) / float(num_bins) * data_max
#            y_val = (float(hist[i]) / len(data)) if i in hist else 0
#            x.append(range_lo)
#            y.append(y_val)
#
#            x.append(range_hi)
#            y.append(y_val)
#
#        # scale max Y
#        axes[3] = float(max(hist.values())) / len(data)
    else:
        raise Exception("invalid plot type")

    pylab.grid(True)
    pylab.xscale(xscale)
    pylab.yscale(yscale)
    pylab.axis(axes)
    if xlabel:
        pylab.xlabel(xlabel)
    if ylabel:
        pylab.ylabel(ylabel)
    if title:
        if ESCAPE:
            pylab.title(escape(label))
        else:
            pylab.title(label)
    if legend:
        pylab.legend(lines, datanames, loc = "lower right")
    if write:
        filepath = write_filepath + '.' + ext
        fig.savefig(filepath)
        print "wrote file to %s" % filepath
    else:
        #pylab.show()
        pass

def show():
    pylab.show()
