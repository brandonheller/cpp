#!/usr/bin/env python
'''Generic cdf/pdf/ccdf plotting functions.'''
import errno
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


from lib.options import parse_args, DPI

import matplotlib.pyplot as plt
import networkx as nx
import pylab


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

# Matplotlib does not close figures when creating them, leading to a horrendous
# memory leak.  Solutions at:
# http://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg13222.html
def clear_fig(fig):
    plt.close(fig)


# from http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise


def ranges_data(stats, aspect_fcns, aspects, metric):
    '''Extract out range data given aspect functions.

    @return json_data: dict with two keys, x and lines:
        @param x: sorted list of integer controller values
        @param lines: dicts keyed by metric value with y-axis data
    '''
    lines = {}
    x = sorted([int(a) for a in stats['group']])
    for g in x:
        data_agg = stats['data'][str(g)]
        for aspect, fcn in aspect_fcns.iteritems():
            assert aspect in aspects
            if aspect not in lines:
                lines[aspect] = []
            lines[aspect].append(fcn(g, data_agg, metric))
    return {'x': x, 'lines': lines}


def ranges(stats, metric, aspects, aspect_colors, aspect_fcns,
           xscale, yscale, label = None, axes = None,
           write_filepath = None, write = False, ext = 'pdf',
           legend = None, title = False, xlabel = None, ylabel = None,
           min_x = None, max_x = None, min_y = None, max_y = None,
           x = None, lines = None):

    # Build lines if not already provided.
    if not x and lines or x and not lines:
        raise Exception("must specify x and lines together")

    if not x and not lines:
        data = [ranges_data(stats, aspect_fcns, aspects, metric)]
    else:
        data = [{'x': x, 'lines': lines}]

    ranges_multiple(stats, metric, aspects, aspect_colors, aspect_fcns,
           xscale, yscale, label, axes,
           write_filepath = write_filepath, write = write, ext = ext,
           legend = legend, title = title, xlabel = xlabel, ylabel = ylabel,
           min_x = min_x, max_x = max_x, min_y = min_y, max_y = max_y,
           data = data)


def ranges_multiple(stats, metric, aspects, aspect_colors, aspect_fcns,
           xscale, yscale, label = None, axes = None,
           write_filepath = None, write = False, ext = 'pdf',
           legend = None, title = False, xlabel = None, ylabel = None,
           min_x = None, max_x = None, min_y = None, max_y = None,
           data = None):
    '''Plot multiple ranges on one graph.
    
    @param data_lines: list of dicts, each of:
        {x: [list of x's],
         lines: [dict of data lists, keyed by aspects.]}
    '''
    assert data

    fig = get_fig()

    for d in data:
        x = d['x']
        lines = d['lines']
        #print "plotting: %s %s" % (x, lines)
        for aspect in aspects:
            y = lines[aspect]
            pylab.plot(x, y, aspect_colors[aspect], linestyle = '-', linewidth = 1)


    pylab.grid(True)
    pylab.xscale(xscale)
    pylab.yscale(yscale)
    if axes:
        pylab.axis(axes)
    else:
        all_x = []
        all_y = []
        for d in data:
            x = d['x']
            y = d['lines']
            all_x.extend(x)
            for a, l in y.iteritems():
                all_y.extend(l)

        if not min_x:
            min_x = int(min(all_x))
        if not max_x:
            max_x = int(max(all_x))
        if not min_y:
            min_y = min(all_y)
        if not max_y:
            max_y = max(all_y)
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
    clear_fig(fig)


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
            if len(x) == 1 and len(y) == 1 and x[0] == 0.0 and y[0] == 0.0:
                # Do nothing, because at k = n, we'd incur a divide-by-zero
                # error trying to optimize.
                # A cleaner way to detect this case might be to pass in g,
                # or store N in stats.
                pass
            else:
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
    clear_fig(fig)


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
    clear_fig(fig)


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
    clear_fig(fig)

def show():
    pylab.show()
