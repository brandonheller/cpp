#!/usr/bin/env python
from operator import attrgetter
import networkx as nx

from topo_lib import get_topo_graph, has_weights, total_weight

import sys

COMPACT = True


def print_topo_stats(name, g):
    n = g.number_of_nodes()
    e = g.number_of_edges()
    ad = 2.0 * g.number_of_edges() / float(g.number_of_nodes())
    ic = nx.is_connected(g)
    c = nx.number_connected_components(g)
    w = total_weight(g) if has_weights(g) else 0
    if COMPACT:
        print "%s: %s %s %.1f %s %s %.1f" % (name, n, e, ad, ic, c, w)
    else:
        print "***********"
        print "topo name: %s" % name
        print "number of nodes: %s" % n
        print "number of edges: %s" % e
        print "average degree: %.1f" % ad
        print "is connected: %s" % ic
        print "connected components: %s" % c
        print "total weight: %.1f" % w

def custom(g):
    for n in g.nodes():
        if 'Latitude' not in g.node[n] or 'Longitude' not in g.node[n]:
            print "node missing a location: %s" % n
        else:
            print "loc OK: %s" % n
    print "connected components: %s" % nx.connected_components(g)

if __name__ == '__main__':

    if len(sys.argv) <= 1:
        print "please provide a topology name"
        exit()
    for topo in sys.argv[1:]:
        g, usable, note = get_topo_graph(topo)
        if g:
            print_topo_stats(topo, g)
            custom(g)

