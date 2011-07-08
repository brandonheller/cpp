import os

import networkx as nx
# From http://hoegners.de/Maxi/geo/
import geo
# To test, go to http://www.daftlogic.com/projects-google-maps-distance-calculator.htm
# and run this code - see if the Portland - SanFran distance is ~533 miles.
# portland = geo.xyz(45.5, -122.67)
# sanfran = geo.xyz(37.777, -122.419)
METERS_TO_MILES = 0.000621371192
# print geo.distance(portland, sanfran) * METERS_TO_MILES

from os3e_weighted import OS3EWeightedGraph


def lat_long_pair(node):
    return (float(node["Latitude"]), float(node["Longitude"]))


def dist_in_miles(g, src, dst):
    '''Given a NetworkX graph data and node names, compute mileage between.'''
    src_pair = lat_long_pair(g.node[src])
    src_loc = geo.xyz(src_pair[0], src_pair[1])
    dst_pair = lat_long_pair(g.node[dst])
    dst_loc = geo.xyz(dst_pair[0], dst_pair[1])
    return geo.distance(src_loc, dst_loc) * METERS_TO_MILES


def import_zoo_graph(topo):
    '''Given name of Topology Zoo graph, read and assign mileage weights.'''
    filename = 'zoo/' + topo + '.gml'
    if not os.path.exists(filename):
        raise Exception("invalid topo path:%s" % filename)
    # Convert multigraphs to regular graphs; multiple edges don't affect
    # latency, but add complications when debugging.
    g = nx.Graph(nx.read_gml(filename))
    # Append weights
    for src, dst in g.edges():
        g[src][dst]["weight"] = dist_in_miles(g, src, dst)
        print "dist between %s and %s is %s" % (src, dst, g[src][dst]["weight"])
    return g


def get_topo_graph(topo):
    if topo == 'os3e':
        g = OS3EWeightedGraph()
    else:
        g = import_zoo_graph(topo)
    return g
