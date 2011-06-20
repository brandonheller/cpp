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
    set_weights(g, 1.0)


def set_weights(g, weight):
    '''Set edge weights for NetworkX graph to specified weight & return.'''
    for src, dst in g.edges():
        g[src][dst]['weight'] = weight
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


def pathlen(g, path):
    '''Return sum of path weights.

    @param g: NetworkX Graph
    @param path: list of nodes
    @return length: sum of path weights
    '''
    pathlen = 0
    for i, n in enumerate(path):
        if i != len(path) - 1:
            pathlen += g[n][path[i+1]]['weight']
    return pathlen


def edges_on_path(l):
    '''Return list of edges on a path list.'''
    return [(l[i], l[i + 1]) for i in range(len(l) - 1)]


def interlacing_edges(list1, list2):
    '''Return edges in common between two paths.

    Input paths are considered interlacing, even if they go in the opposite
    direction across the same link.  In that case, a single edge will be
    return in whatever order NetworkX prefers for an undirected edge.
    '''
    l1 = edges_on_path(list1)
    l1.extend(edges_on_path([i for i in reversed(list1)]))
    l2 = edges_on_path(list2)
    l2.extend(edges_on_path([i for i in reversed(list2)]))
    combined = [e for e in l1 if e in l2]
    return nx.Graph(combined).edges()


def flip_and_negate_path(g, path):
    '''Return new directed graph with the given path flipped & negated.

    @param g: NetworkX Graph (undirected)
    @param path: list of nodes in path
    @return g2: NetworkX DiGraph, modified
    '''
    g2 = nx.DiGraph(g)

    for i, n in enumerate(path):
        if i != len(path) - 1:
            n_next = path[i + 1]
            # Remove forward edge, leaving only reverse edge.
            g2.remove_edge(n, n_next)
            # Flip edge weight to negative of the original edge..
            g2[n_next][n]['weight'] *= -1

    return g2


def remove_edge_bidir(g, src, dst):
    '''Remove edge plus one in opposite direction.

    @param g: NetworkX DiGraph
    @param src: source node
    @param dst: destination node
    '''
    g.remove_edge(src, dst)
    g.remove_edge(dst, src)


def add_edge_bidir(g, src, dst, weight = None):
    '''Add edge plus one in opposite direction.

    @param g: NetworkX DiGraph
    @param src: source node
    @param dst: destination node
    @param weight: optional weight to set for both
    '''
    g.add_edge(src, dst)
    g.add_edge(dst, src)
    if weight:
        g[src][dst]['weight'] = weight
        g[dst][src]['weight'] = weight
