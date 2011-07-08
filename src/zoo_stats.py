#!/usr/bin/env python
import os
from operator import attrgetter
import networkx as nx

from topo_lib import get_topo_graph, has_weights, total_weight

ZOO_DIR = 'zoo'

MAX = None
NUM = 20

class GraphData(object):
    def __init__(self, name, n, e, ad, ic, c):
        self.name = name
        self.n = n
        self.e = e
        self.ad = ad
        self.ic = ic
        self.c = c

    def __repr__(self):
        return repr((self.name, self.n, self.e, self.ad, self.ic, self.c))


if __name__ == '__main__':
    data = []
    files = os.listdir(ZOO_DIR)
    # Ignore files starting with a .
    topos = [d.split(".")[0] for d in files if d != "" and d[0] != '.' and 'cache' not in d and '.gml' in d]
    # Extract to just names
    for i, topo in enumerate(topos):
        if MAX != None and i == MAX:
            break
        g = get_topo_graph(topo)
        if not g:
            pass
            #print "graph with no geos: %s" % topo
        else:
            print ">>>%s: %s of %s" % (topo, i, len(topos))
            if has_weights(g):
                w = total_weight(g)
            else:
                w = 0.0
            de = GraphData(name = topo,
                           n = g.number_of_nodes(),
                           e = g.number_of_edges(),
                           ad = g.number_of_edges() / float(g.number_of_nodes()),
                           ic = nx.is_connected(g),
                           c = nx.number_connected_components(g))
            data.append(de)
            print "\t" + str(de)
    
    keys = [d for d in dir(data[0]) if "__" not in d and d != 'name']
    for key in keys:
        print key
        s = sorted(data, key = attrgetter(key))
        print "\tlow to high:"
        for d in s[0:NUM]:
            print "\t\t%s" % d
        print "\thigh to low:"
        for d in reversed(s[-NUM-1:-1]):
            print "\t\t%s" % d