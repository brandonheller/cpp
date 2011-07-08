#!/usr/bin/env python
from operator import attrgetter
import networkx as nx

from topo_lib import get_topo_graph, has_weights, total_weight
from zoo_tools import for_each_zoo_topo

ZOO_DIR = 'zoo'

MAX = 20
NUM = 20  # Number of topologies to print for each list at the end

class GraphData(object):
    def __init__(self, name, n, e, ad, ic, c, w):
        self.name = name
        self.n = n
        self.e = e
        self.ad = ad
        self.ic = ic
        self.c = c
        self.w = w

    def __repr__(self):
        return repr((self.name, self.n, self.e, self.ad, self.ic, self.c,
                     self.w))


if __name__ == '__main__':

    data = []

    def add_to_data(name, g, i, t, data):
        g = get_topo_graph(name)
        print ">>>%s: %s of %s" % (name, i, t)
        de = GraphData(name = name,
                       n = g.number_of_nodes(),
                       e = g.number_of_edges(),
                       ad = g.number_of_edges() / float(g.number_of_nodes()),
                       ic = nx.is_connected(g),
                       c = nx.number_connected_components(g),
                       w = total_weight(g) if has_weights(g) else 0)
        data.append(de)
        print "\t" + str(de)

    for_each_zoo_topo(add_to_data, data, MAX)

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