#!/usr/bin/env python
'''Generic cdf/pdf/ccdf plotting functions.'''
import os

# See http://matplotlib.sourceforge.net/users/customizing.html

from matplotlib import rc, rcParams
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
rcParams['xtick.labelsize'] = 20
rcParams['ytick.labelsize'] = 20
rcParams['xtick.major.pad'] = 6
rcParams['figure.subplot.bottom'] = 0.125
rcParams['lines.linewidth'] = 2

import matplotlib.pyplot as plt
import networkx as nx
import pylab


def escape(s):
    '''Backslash-escape underscores to use LaTeX output.'''
    s_escaped = ""
    for i, letter in enumerate(s):
        if letter == '_':
            s_escaped += '\\'
        s_escaped += letter
    return s_escaped


def plot(ptype, data, colors, axes, label, xscale, yscale,
         write_filepath = None, write = False, num_bins = None, ext = 'pdf',
         legend = None, title = False, xlabel = None, ylabel = None):

    fig = pylab.figure()
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

    text_override = {'fontsize': '24'}
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
        pylab.show()
