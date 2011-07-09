#!/usr/bin/env python
'''Find geocodes for each node name in the OS3e graph using PlaceFinder.'''
import os

# From http://hoegners.de/Maxi/geo/
import geo
# To test, go to http://www.daftlogic.com/projects-google-maps-distance-calculator.htm
# and run this code - see if the Portland - SanFran distance is ~533 miles.
# portland = geo.xyz(45.5, -122.67)
# sanfran = geo.xyz(37.777, -122.419)
METERS_TO_MILES = 0.000621371192
# print geo.distance(portland, sanfran) * METERS_TO_MILES

from file_libs import write_json_file, read_json_file
from geocode import get_lat_long
from topo.os3e import OS3EGraph

LATLONG_FILE = "geo/os3e_latlong.json"

def lat_long_pair(node):
    return (float(node["Latitude"]), float(node["Longitude"]))

def dist_in_miles(data, src, dst):
    '''Given a dict of names and location data, compute mileage between.'''
    src_pair = lat_long_pair(data[src])
    src_loc = geo.xyz(src_pair[0], src_pair[1])
    dst_pair = lat_long_pair(data[dst])
    dst_loc = geo.xyz(dst_pair[0], dst_pair[1])
    return geo.distance(src_loc, dst_loc) * METERS_TO_MILES

def OS3EWeightedGraph():

    data = {}
    g = OS3EGraph()

    # Get locations
    if os.path.isfile(LATLONG_FILE):
        print "Using existing lat/long file"
        data = read_json_file(LATLONG_FILE)
    else:
        print "Generating new lat/long file"
        for n in g.nodes():
            data[n] = get_lat_long(n)
        write_json_file(LATLONG_FILE, data)

    # Append weights
    for src, dst in g.edges():
        g[src][dst]["weight"] = dist_in_miles(data, src, dst)
        #print "%s to %s: %s" % (src, dst, g[src][dst]["weight"])

    return g

if __name__ == '__main__':
    g = OS3EWeightedGraph()