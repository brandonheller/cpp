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


def nx_graph_from_tuples(undir_tuples, dir_tuples = None):
    g = nx.Graph()
    for a, b, w in undir_tuples:
        g.add_edge(a, b, weight = w)
    if dir_tuples:
        g = nx.DiGraph(g)
        for a, b, w in dir_tuples:
            g.add_edge(a, b, weight = w)
    return g


def vertex_disjoint(paths):
    '''Check if provided paths are vertex-disjoint.

    @param paths: list of path lists
    '''
    vertices = set([])
    for path in paths:
        for n in path:
            if n in vertices:
                return False
            vertices.add(n)
    return True


def edge_disjoint(paths):
    '''Check if provided paths are edge-disjoint.

    @param paths: list of path lists
    '''
    edges = set([])
    # Ensure edge disjointness
    for path in paths:
        for i, n in enumerate(path):
            if i != len(path) - 1:
                e = (n, path[i + 1])
                if e in edges:
                    return False
                edges.add(e)
                e_rev = (path[i + 1], n)
                if e_rev in edges:
                    return False
                edges.add(e_rev)
    return True