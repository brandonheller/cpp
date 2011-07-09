#!/usr/bin/env python
'''Generic cdf/pdf/ccdf plotting functions.'''
import errno
from optparse import OptionParser
import os
import json
from operator import itemgetter

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
rcParams['figure.subplot.bottom'] = 0.14
rcParams['figure.subplot.left'] = 0.2
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

DEF_TOPO = 'os3e'

DPI = 300


def parse_args():
    opts = OptionParser()

    # Topology selection
    opts.add_option("--topo", type = 'str', default = DEF_TOPO,
                    help = "topology name")
    opts.add_option("--topo_list", type = 'str', default = None,
                    help = "list of comma-separated topology names")
    opts.add_option("--topo_blacklist", type = 'str', default = None,
                    help = "list of comma-separated topologies to ignore")
    opts.add_option("--all_topos",  action = "store_true",
                    default = False,
                    help = "compute metric(s) for all topos?")
    opts.add_option("--from_start", type = 'int', default = 3,
                    help = "number of controllers from start")
    opts.add_option("--from_end", type = 'int', default = 0,
                    help = "number of controllers from end")
    opts.add_option("--controller_list", type = 'str', default = None,
                    help = "list of comma-separated controller totals")

    # Metric selection
    opts.add_option("--metric",
                    default = 'latency',
                    choices = METRICS,
                    help = "metric to compute, one in %s" % METRICS)
    opts.add_option("--all_metrics",  action = "store_true",
                    default = False,
                    help = "compute all metrics?")
    opts.add_option("--lat_metrics",  action = "store_true",
                    default = False,
                    help = "compute all latency metrics?")
    opts.add_option("--metric_list", type = 'string',
                    default = None,
                    help = "metrics to show, from %s" % METRICS)

    # Shared output args
    opts.add_option("-w", "--write",  action = "store_true",
                    default = False,
                    help = "write plots, rather than display?")

    # Multiprocessing options
    opts.add_option("--no-multiprocess",  action = "store_false",
                    default = True, dest = 'multiprocess',
                    help = "don't use multiple processes?")
    opts.add_option("--processes", type = 'int', default = 8,
                    help = "worker pool size; must set multiprocess=True")
    opts.add_option("--chunksize", type = 'int', default = 50,
                    help = "batch size for parallel processing")

    # Metrics-specific arguments
    opts.add_option("--write_combos",  action = "store_true",
                    default = False,
                    help = "write out combinations?")
    opts.add_option("--write_dist",  action = "store_true",
                    default = False,
                    help = "write_distribution?")
    opts.add_option("--write_csv",  action = "store_true",
                    default = False,
                    help = "write csv file?")
    opts.add_option("--no-dist_only",  action = "store_false",
                    default = True, dest = 'dist_only',
                    help = "don't write out _only_ the full distribution (i.e.,"
                    "run all algorithms.)")
    opts.add_option("--use_prior",  action = "store_true",
                    default = False,
                    help =  "Pull in previously computed data, rather than recompute?")
    opts.add_option("--no-compute_start",  action = "store_false",
                    default = True, dest = 'compute_start',
                    help = "don't compute metrics from start?")
    opts.add_option("--no-compute_end",  action = "store_false",
                    default = True, dest = 'compute_end',
                    help = "don't compute metrics from end?")
    opts.add_option("--median",  action = "store_true",
                    default = False,
                    help = "compute median?")

    # Plotting-specific input args
    opts.add_option("-i", "--input", type = 'string', 
                    default = None,
                    help = "name of input file")
    opts.add_option("--input_dir", type = 'string',
                    default = DEF_INPUT_DIR,
                    help = "name of input dir")
    opts.add_option("-o", "--output_dir", type = 'string',
                    default = DEF_OUTPUT_DIR,
                    help = "name of output file")

    # Plotting-specific params
    opts.add_option("--max", type = 'int', default = DEF_MAX,
                    help = "highest number of controllers to plot %s" % METRICS)
    opts.add_option("--minx", type = 'float', default = None,
                    help = "min X axis value")
    opts.add_option("--maxx", type = 'float', default = None,
                    help = "min X axis value")
    opts.add_option("--miny", type = 'float', default = None,
                    help = "min Y axis value")
    opts.add_option("--maxy", type = 'float', default = None,
                    help = "min Y axis value")
    opts.add_option("-e", "--ext", type = 'string',
                    default = DEF_EXT,
                    help = "file extension")
    opts.add_option("-l", "--labels",  action = "store_true",
                    default = False,
                    help = "write labels to images (map_combo only)?")

    options, arguments = opts.parse_args()

    # Handle metrics
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

    if options.all_metrics:
        options.metrics = metrics.METRICS
    elif options.lat_metrics:
        options.metrics = ['latency', 'wc_latency']
    else:
        options.metrics = [options.metric]

    options.controllers = None
    if options.controller_list:
        options.controllers = []
        for i in options.controller_list.split(','):
            options.controllers.append(int(i))

    if options.topo != DEF_TOPO and options.topo_list:
        raise Exception("Both topo and topo_list provided; pick one please")
    else:
        if options.topo_list:
            options.topos = options.topo_list.split(',')
        else:
            options.topos = [options.topo]

    if options.topo_blacklist:
        options.topos_blacklist = options.topo_blacklist.split(',')
    else:
        options.topos_blacklist = None

    return options


def load_stats(options):
    input_file = open(options.input, 'r')
    stats = json.load(input_file)
    return stats


def get_fig():
    fig = pylab.figure()
    fig.set_size_inches(6, 4)
    return fig


def escape(s):
    '''Backslash-escape underscores to use LaTeX output.'''
    s_escaped = ""
    for letter in s:
        if letter == '_':
            s_escaped += '\\'
        s_escaped += letter
    return s_escaped


# from http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise


def ranges(stats, metric, aspects, aspect_colors, aspect_fcns,
           xscale, yscale, label = None, axes = None,
           write_filepath = None, write = False, ext = 'pdf',
           legend = None, title = False, xlabel = None, ylabel = None,
           min_x = None, max_x = None, min_y = None, max_y = None):

    fig = get_fig()

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
        if not max_x:
            max_x = int(max(x))
        if not min_y:
            min_y = min([min(lines[aspect]) for aspect in aspects])
        if not max_y:
            max_y = max([max(lines[aspect]) for aspect in aspects])
        # Assume these are string-ified nums of controllers.
        axes = [min_x, max_x, 0, max_y]
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
        mkdir_p(os.path.dirname(filepath))
        fig.savefig(filepath, dpi = DPI)
        print "wrote file to %s" % filepath
    else:
        #pylab.show()
        pass


def pareto(data, colors, axes, xscale, yscale,
          write_filepath = None, write = False, num_bins = None, ext = 'pdf',
          legend = None, title = False, xlabel = None, ylabel = None,
          x_metric = None, y_metric = None, min_x = None, min_y = None,
          normalize = None, marks = True):

    fig = get_fig()
    lines = []
    datanames = []

    pylab.grid(True)

    paretos = []
    for i, k in enumerate(sorted(data.keys())):
        # Sort metrics by X
        points_list = []
        for d in data[k]:
            points_list.append((d[x_metric], d[y_metric]))
        lowest_y = None
        pareto = []  # List of points on a pareto-optimal curve
        sorted_by_x = sorted(points_list, key = itemgetter(0))
        for x, y in sorted_by_x:
            if not lowest_y or y < lowest_y:
                pareto.append((x, y))
                lowest_y = y

        x = [d[0] for d in pareto]
        y = [d[1] for d in pareto]
        if normalize:
            small_x = x[0]
            small_y = y[-1]
            pareto_new = []
            for d in pareto:
                pareto_new.append((d[0] / float(small_x), d[1] / float(small_y)))
            pareto = pareto_new
            x = [d[0] for d in pareto]
            y = [d[1] for d in pareto]

        color = colors[i]
        lines.append(pylab.plot(x, y, 'o-',
                                color = color,
                                markerfacecolor = color,
                                markeredgecolor = color,
                                markersize = 4, zorder = 2))
        if marks:
            kwargs = {'color': color,
                      'markerfacecolor': 'w',
                      'markeredgecolor': color,
                      'markeredgewidth': 2}
            # O to mark X metric optimal, X for Y metric optimal
            pylab.plot(x[0], y[0], 'o', markersize = 10, **kwargs)
            pylab.plot(x[-1], y[-1], 'x', markersize = 10, **kwargs)

        datanames.append(k)
        paretos.append(pareto)

    pylab.xscale(xscale)
    pylab.yscale(yscale)
    if axes:
        pylab.axis(axes)
    else:
        if normalize:
            margin_factor = 1.01
        else:
            margin_factor = 1.05  # avoid chopping markers at edge of grid
        if not min_x == 0 and not min_x:
            min_x = paretos[-1][0][0] / margin_factor
        if normalize:
            min_x = 1.0 / float(margin_factor)
        max_x = max([x[-1][0] for x in paretos]) * margin_factor
        if not min_y == 0 and not min_y:
            min_y = paretos[-1][-1][1] / margin_factor
        if normalize:
            min_y = 1.0 / float(margin_factor)
        max_y = max([y[0][1] for y in paretos]) * margin_factor
        pylab.axis([min_x, max_x, min_y, max_y])
    if xlabel:
        pylab.xlabel(xlabel)
    if ylabel:
        pylab.ylabel(ylabel)
    if legend:
        pylab.legend(lines, datanames, loc = "lower right")
    if write:
        filepath = write_filepath + '.' + ext
        mkdir_p(os.path.dirname(filepath))
        fig.savefig(filepath, dpi = DPI)
        print "wrote file to %s" % filepath


def cloud(data, colors, axes, xscale, yscale,
          write_filepath = None, write = False, num_bins = None, ext = 'pdf',
          legend = None, title = False, xlabel = None, ylabel = None,
          x_metric = None, y_metric = None):

    fig = get_fig()
    lines = []
    datanames = []

    pylab.grid(True)

    for i, k in enumerate(sorted(data.keys(), reverse = True)):
        x = [d[x_metric] for d in data[k]]
        y = [d[y_metric] for d in data[k]]
        # Plot in reverse order, so choose colors in reverse order
        color = colors[len(data) - 1 - i]
        pylab.plot(x, y, 'o',
                   markerfacecolor = color,
                   markeredgecolor = color,
                   markersize = 3)
        datanames.append(k)

    pylab.xscale(xscale)
    pylab.yscale(yscale)
    pylab.axis(axes)
    if xlabel:
        pylab.xlabel(xlabel)
    if ylabel:
        pylab.ylabel(ylabel)
    if legend:
        pylab.legend(lines, datanames, loc = "lower right")
    if write:
        filepath = write_filepath + '.' + ext
        mkdir_p(os.path.dirname(filepath))
        fig.savefig(filepath, dpi = DPI)
        print "wrote file to %s" % filepath
    else:
        pass


def plot(ptype, data, colors, axes, label, xscale, yscale,
         write_filepath = None, write = False, num_bins = None, ext = 'pdf',
         legend = None, title = False, xlabel = None, ylabel = None):

    fig = get_fig()
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
        mkdir_p(os.path.dirname(filepath))
        print "writing file to %s" % filepath
        fig.savefig(filepath, dpi = DPI)
    else:
        #pylab.show()
        pass

def show():
    pylab.show()
