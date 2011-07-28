#!/usr/bin/env python
'''
Generate a map to show a combo.
'''
import os
import string

from matplotlib import rc, rcParams

import lib.plot as plot
from lib.colors import COLORS
from lib.options import parse_args, DEF_EXT

rc('font',**{'family':'sans-serif','sans-serif':['Arial']})
rc('axes', **{'linewidth' : 0,
              'grid' : False})

rcParams['figure.subplot.top'] = 1
rcParams['figure.subplot.bottom'] = 0
rcParams['figure.subplot.left'] = 0
rcParams['figure.subplot.right'] = 0.98

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

from os3e_weighted import OS3EWeightedGraph
from os3e_weighted import LATLONG_FILE
from file_libs import read_json_file
from topo_lib import get_topo_graph
from metrics_lib import get_output_filepath

def write_map(g, city_data, metrics, metric_data, filename, write = False,
              ext = DEF_EXT, labels = False, color = None, marks = ['o', 'x', '+']):

    def add_city(city, dot, markersize, color):
        lon = city_data[city]['Longitude']
        lat = city_data[city]['Latitude']
        x, y = m(lon, lat)
        plt.plot(x, y, dot, markersize = markersize, markeredgewidth = 3.8,
                 markerfacecolor = '#ffffff', markeredgecolor = color,
                 zorder = 3)
        if labels:
            plt.text(x - 100000, y - 220000, city)

    def add_edge(edge):
        lon = city_data[edge[0]]['Longitude']
        lat = city_data[edge[0]]['Latitude']
        x1, y1 = m(lon, lat)
        lon = city_data[edge[1]]['Longitude']
        lat = city_data[edge[1]]['Latitude']
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
                urcrnrlat=50, projection='lcc', lat_1=33,lat_2=46,
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
    for i, metric in enumerate(metrics):
        for city in metric_data[i]:
            add_city(city, marks[i], 24, color)
    if write:
        filename = string.replace(filename, '.json', '')
        filename += '_' + ','.join(metrics)
        filepath = filename + '.' + ext
        fig.savefig(filepath)
        print "wrote file to %s" % filepath
    else:
        plt.show()
    plt.close(fig)


def do_plot(options, stats, g, write_filepath):
    city_data = None
    if os.path.isfile(LATLONG_FILE):
        city_data = read_json_file(LATLONG_FILE)

    data = {}
    if not write_filepath:
        write_filepath = get_output_filepath(options.input)
    write_filepath += '_map_'

    print "reformatting data & doing plot..."
    for i, c in enumerate(stats['group']):
        if options.max and i >= options.max:
            break
        data[str(c)] = stats['data'][str(c)]
        metric_data = []
        for metric in options.metrics:
            metric_data.append(data[str(c)][metric]['lowest_combo'])
        write_map(g, city_data, options.metrics, metric_data, write_filepath + str(c), options.write,
                  options.ext, options.labels, color = COLORS[i])


if __name__ == "__main__":
    options = parse_args()
    print "loading JSON data..."
    stats = plot.load_stats(options)
    g, usable, note = get_topo_graph(options.input.split('/')[1])
    do_plot(options, stats, g, None)