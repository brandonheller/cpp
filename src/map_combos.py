#!/usr/bin/env python
'''
Generate a map to show a combo.
'''
import os
import string

from matplotlib import rc, rcParams

import lib.plot as plot

rc('font',**{'family':'sans-serif','sans-serif':['Arial']})
rc('axes', **{'linewidth' : 0,
              'grid' : False})

rcParams['figure.subplot.top'] = 1
rcParams['figure.subplot.bottom'] = 0
rcParams['figure.subplot.left'] = 0
rcParams['figure.subplot.right'] = 0.98

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np

from os3e_weighted import OS3EWeightedGraph
from os3e_weighted import LATLONG_FILE
from file_libs import read_json_file
import metrics_lib as metrics


COLORS = ["r", "g", "b", "c", "m", "y", "k"]


def write_map(g, city_data, avg_combo, wc_combo, filename, write = False,
              ext = plot.DEF_EXT, labels = False, color = None):

    def add_city(city, dot, markersize, color):
        lon = city_data[city]['longitude']
        lat = city_data[city]['latitude']
        x, y = m(lon, lat)
        plt.plot(x, y, dot, markersize = markersize, markeredgewidth = 3.8,
                 markerfacecolor = '#ffffff', markeredgecolor = color,
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
        c = '#888888'
        plt.plot([x1, x2], [y1, y2],
                 marker = 'o', linewidth = 2.5,
                 color = c,
                 markersize = 5.5, markeredgewidth = 2.0,
                 markerfacecolor = c, markeredgecolor = c,
                 zorder = 2)

    def lower_48_basemap():
        m = Basemap(llcrnrlon=-119, llcrnrlat=22, urcrnrlon=-64,
                urcrnrlat=49, projection='lcc', lat_1=33,lat_2=45,
                lon_0=-95, resolution='c')
        boundary_color = '#eaeaea'
        m.drawcoastlines(linewidth=0.5, color=boundary_color, antialiased=True)
        m.drawcountries(linewidth=0.5, color=boundary_color, antialiased=True)
        m.drawstates(linewidth=0.2, color=boundary_color, antialiased=True)
        return m

    fig = plt.figure()
    fig.set_size_inches(6, 4)
    colors = []

    m = lower_48_basemap()
    for edge in g.edges():
        add_edge(edge)
    for city in avg_combo:
        add_city(city, 'o', 15, color)
    for city in wc_combo:
        add_city(city, 'x', 15, color)
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
    
    options = plot.parse_args()
    print "loading JSON data..."
    stats = plot.load_stats(options)
    data = {}
    os3e = OS3EWeightedGraph()

    print "reformatting data & doing plot..."
    for i, g in enumerate(stats['group']):
        if options.max and i >= options.max:
            break
        data[str(g)] = stats['data'][str(g)]
        write_filepath = options.input + '_latencies_' + str(g)
        write_filepath = write_filepath.replace('data_out', 'data_vis')
        avg = data[str(g)]['latency']['lowest_combo']
        wc = data[str(g)]['wc_latency']['lowest_combo']
        write_map(os3e, city_data, avg, wc, write_filepath, options.write,
                  options.ext, options.labels, color = COLORS[i])


if __name__ == "__main__":
    do_plot()
