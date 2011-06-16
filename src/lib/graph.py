#!/usr/bin/env python
'''
Library functions for working w/graphs that are not specific to an algorithm.
'''

import logging

import networkx as nx

lg = logging.getLogger("cc")


def flatten(paths):
    '''Compute and return flattened graph, given paths.

    By flattened graph, we mean one created from the union of a set of paths.

    @param paths: paths to flatten

    @return flattened: flattened NetworkX Graph
    '''
    used = nx.Graph()
    lg.debug("paths: %s" % paths)
    for path in paths.values():
        lg.debug("flattening path: %s" % path)
        used.add_path(path)
    return used


def loop_graph(n):
    '''Return loop graph with n nodes.'''
    g = nx.path_graph(n)
    # Add loop edge
    g.add_edge(g.number_of_nodes() - 1, 0)
    return g


def set_unit_weights(g):
    '''Set edge weights for NetworkX graph to 1 & return.'''
    for src, dst in g.edges():
        g[src][dst]['weight'] = 1
    return g