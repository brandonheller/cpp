#!/usr/bin/env python
'''
Generate a map to show a combo.
'''
import json
import os
from optparse import OptionParser
import string

from matplotlib import rc, rcParams

rc('font',**{'family':'sans-serif','sans-serif':['Arial']})
rc('axes', **{'linewidth' : 0,
              'grid' : False})

rcParams['figure.subplot.top'] = 1
rcParams['figure.subplot.bottom'] = 0.0
rcParams['figure.subplot.left'] = 0.02
rcParams['figure.subplot.right'] = 0.98

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np

from os3e_weighted import OS3EWeightedGraph
from os3e_weighted import LATLONG_FILE
from file_libs import read_json_file
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

DEF_EXT = 'pdf'


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
    opts.add_option("-e", "--ext", type = 'string',
                    default = DEF_EXT,
                    help = "file extension")
    opts.add_option("-l", "--labels",  action = "store_true",
                    default = False,
                    help = "write labels to images?")
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


def write_map(g, city_data, avg_combo, wc_combo, filename, write = False,
              ext = DEF_EXT, labels = False):

    def add_city(city, dot, markersize):
        lon = city_data[city]['longitude']
        lat = city_data[city]['latitude']
        x, y = m(lon, lat)
        plt.plot(x, y, dot, markersize = markersize, markeredgewidth = 2,
                 markerfacecolor = '#ffffff', markeredgecolor = 'r',
                 zorder = 3)
        if labels:
            plt.text(x - 100000, y - 220000, city)

    def add_edge(edge):
        lon = city_data[edge[0]]['longitude']
        lat = city_data[edge[0]]['latitude']
        x1, y1 = m(lon, lat)
        lon = city_data[edge[1]]['longitude']
        lat = city_data[edge[1]]['latitude']
        x2, y2 = m(lon, lat)
        plt.plot([x1, x2], [y1, y2],
                 marker = 'o', linewidth = 1.5,
                 color = '#aaaaaa',
                 markersize = 3, markeredgewidth = 1.4,
                 markerfacecolor = '#666666', markeredgecolor = 'k',
                 zorder = 2)

    def lower_48_basemap():
        m = Basemap(llcrnrlon=-119, llcrnrlat=22, urcrnrlon=-64,
                urcrnrlat=49, projection='lcc', lat_1=33,lat_2=45,
                lon_0=-95, resolution='c')
        boundary_color = '#dddddd'
        m.drawcoastlines(linewidth=0.5, color=boundary_color, antialiased=True)
        m.drawcountries(linewidth=0.5, color=boundary_color, antialiased=True)
        m.drawstates(linewidth=0.2, color=boundary_color, antialiased=True)
        return m

    fig = plt.figure()
    fig.set_size_inches(6, 4)
    
    m = lower_48_basemap()
    for edge in g.edges():
        add_edge(edge)
    for city in avg_combo:
        add_city(city, 'o', 9)
    for city in wc_combo:
        add_city(city, '+', 11)
    if write:
        filename = string.replace(filename, '.json', '')
        filepath =  filename + '.' + ext
        fig.savefig(filepath)
        print "wrote file to %s" % filepath
    else:
        plt.show()


def do_plot():
    city_data = None
    if os.path.isfile(LATLONG_FILE):
        city_data = read_json_file(LATLONG_FILE)
    
    options = parse_args()
    print "loading JSON data..."
    stats = load_stats(options)
    data = {}

    os3e = OS3EWeightedGraph()

    print "reformatting data & doing plot..."
    for i, g in enumerate(stats['group']):
        if options.max and i >= options.max:
            break
        data[str(g)] = stats['data'][str(g)]
        write_filepath = options.input + '_latencies_' + str(g)
        avg = data[str(g)]['latency']['lowest_combo']
        wc = data[str(g)]['wc_latency']['lowest_combo']
        write_map(os3e, city_data, avg, wc, write_filepath, options.write,
                  options.ext, options.labels)


if __name__ == "__main__":
    do_plot()
