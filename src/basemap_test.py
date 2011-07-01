#!/usr/bin/env python
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

fig = plt.figure()
fig.set_size_inches(6, 4)

# US lower 48 states
m = Basemap(llcrnrlon=-119, llcrnrlat=22, urcrnrlon=-64,
            urcrnrlat=49, projection='lcc', lat_1=33,lat_2=45,
            lon_0=-95, resolution='c')

boundary_color = '#dddddd'
m.drawcoastlines(linewidth=0.5, color=boundary_color, antialiased=True)
m.drawcountries(linewidth=0.5, color=boundary_color, antialiased=True)
m.drawstates(linewidth=0.2, color=boundary_color, antialiased=True)

cities = [['New York', 40.7167, -74, 'ro'],
          ['San Francisco', 37.78, -122.4, 'b+']]

for city, lat, lon, dot in cities:
    x, y = m(lon, lat)
    plt.plot(x, y, dot, alpha = 1.0, markersize = 6, markeredgewidth = 1.4,
             markerfacecolor = '#ffffff', markeredgecolor = 'r')
    if lon < 37.0:
        # East coast: display to left of dot
        xshift = 0
    else:
        # West coast: display to right of dot
        xshift = 2500000
    plt.text(x + xshift, y - 180000, city)

plt.savefig('test.pdf')