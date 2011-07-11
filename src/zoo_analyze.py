#!/usr/bin/env python
from operator import attrgetter
import networkx as nx

from topo_lib import get_topo_graph, has_weights, total_weight

import sys


def print_topo_stats(name, g):
    print "topo name: %s" % name
    n = g.number_of_nodes()
    print "number of nodes: %s" % n
    e = g.number_of_edges()
    print "number of edges: %s" % e
    ad = 2.0 * g.number_of_edges() / float(g.number_of_nodes())
    print "average degree: %s" % ad
    ic = nx.is_connected(g)
    print "is connected: %s" % ic
    c = nx.number_connected_components(g)
    print "connected components: %s" % c
    w = total_weight(g) if has_weights(g) else 0
    print "total weight: %.1f" % w

if __name__ == '__main__':

    if len(sys.argv) <= 1:
        print "please provide a topology name"
        exit()
    for topo in sys.argv[1:]:
        print "***********"
        g = get_topo_graph(topo)
        print_topo_stats(topo, g)

