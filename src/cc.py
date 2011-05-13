#!/usr/bin/env python
'''
Connectivity Checker

A simple tool to evaluate the connectivity of a graph, given a failure rate.

Intended to help answer questions about the fault tolerance aspects of SDN,
and the algorithms for bootstrapping the switch-controller connection. 
'''
import itertools
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

def sssp_conn(g, controller_node, link_fail_prob):
    # Store pairs of (probability, connectivity)
    uptime_dist = []

    # Compute SSSP.
    # Need a list of nodes from each switch to the controller to see how
    # connectivity changes when links go down.
    paths = nx.single_source_shortest_path(g, controller_node)
    # Store the flattened set of shortest paths to the controller as a
    # graph.  Useful later to only consider those nodes or edges that might
    # have an effect on reliability.
    used = flatten(paths)

    for failed_edge in g.edges():
        lg.debug("------------------------")
        lg.debug("considering failed edge: %s" % str(failed_edge))

        # If failed edge is not a part of the path set, then no effect on
        # reliability.
        if used.has_edge(failed_edge[0], failed_edge[1]):
            # Failed edge matters for connectivity for some switch.

            # Check switch-to-controller connectivity.
            connected = 0
            disconnected = 0
            for sw in g.nodes():
                path_graph = nx.Graph()
                path_graph.add_path(paths[sw])
                #lg.debug("path graph edges: %s" % path_graph.edges())
                if path_graph.has_edge(failed_edge[0], failed_edge[1]):
                    lg.debug("disconnected sw: %s" % sw)
                    disconnected += 1
                else:
                    lg.debug("connected sw: %s" % sw)
                    connected += 1
            connectivity = float(connected) / g.number_of_nodes()
            uptime_dist.append((link_fail_prob, connectivity))
        else:
            # No effect on connectivity.
            lg.debug("edge not in sssp graph; ignoring")
            uptime_dist.append((link_fail_prob, 1.0))

    return uptime_dist


def any_conn(g, controller_node, link_fail_prob):
    # Store pairs of (probability, connectivity)
    uptime_dist = []

    for failed_edge in g.edges():
        lg.debug("------------------------")
        lg.debug("considering failed edge: %s" % str(failed_edge))

        # Check switch-to-controller connectivity.
        gcopy = g.copy()
        gcopy.remove_edge(failed_edge[0], failed_edge[1])
        reachable = nx.dfs_tree(gcopy, controller_node).nodes()
        if controller_node not in reachable:
            reachable += [controller_node]
        nodes = g.number_of_nodes()
        connectivity = float(len(reachable)) / nodes
        uptime_dist.append((link_fail_prob, connectivity))

    return uptime_dist


def compute(g, link_fail_prob, node_fail_prob, max_failures, alg_fcn):
    '''Compute connectivity assuming independent failures.

    @param g: input graph as NetworkX Graph
    @param link_fail_prob: link failure probability
    @param node_fail_prob: node failure probability
    @param max_failures: max failures to consider
    @param alg_fcn: fucntion for static controller connection algorithm, with form:
        @param g: input graph
        @param controller_node: input controller node
        @param link_fail_prob: link failure probability
        @return uptime_dist: list of pairs of form (link_fail_prob, connectivity)

    @return avg_conn: distribution of switch-to-controller connectivity
    @return connectivity_data: dict of uptimes for each controller location
    '''

    # Consider one failure only, for now.  Eventually extend to handle
    # multiple failures by pushing all combinations as lists onto a stack
    # and considering the effect of each one.
    if max_failures != 1:
        raise Exception("only 1 failure supported")

    if node_fail_prob != 0:
        raise Exception("only link failures supported")

    if link_fail_prob * g.number_of_nodes() > 1.0:
        raise Exception("unable to handle case where > 1 failure is typical")

    if type(alg_fcn) is str:
        raise Exception("alg_fcn cannot be a string")

    # Store data used to build an uptime distribution later
    # connectivity_data[controller_location] = uptime
    connectivity_data = {}

    # For each controller location (assume directly attached to a switch
    # with a perfectly reliable link), repeat the analysis.
    for controller_node in g.nodes():

        lg.debug("   >>> considering controller at: %s" % controller_node)

        # Store pairs of (probability, connectivity)
        uptime_dist = []

        uptime_dist = alg_fcn(g, controller_node, link_fail_prob)

        lg.debug("uptime dist: %s" % uptime_dist)
        fraction_covered = sum([x[0] for x in uptime_dist])
        lg.debug("covered %s (fraction) of the uptime distribution" % fraction_covered)
        weighted_conn = 0
        for percentage, conn in uptime_dist:
            lg.debug("adding %s to weighted_conn" % (percentage * conn))
            weighted_conn += percentage * conn
        # Account for time when nothing's broken:
        weighted_conn += (1.0 - fraction_covered) * 1.0
        lg.debug("weighted connectivity: %s" % weighted_conn)

        connectivity_data[controller_node] = weighted_conn

    avg_conn = sum(connectivity_data.values()) / len(connectivity_data.keys())
    lg.debug("average connectivity: %f" % avg_conn)
    return avg_conn, connectivity_data

def compare_lists(one, two):
    '''Compare two ordered lists.  One must be a permutation of the other.

    @param one: list
    @param two: list
    @return sum: value representing avg absolute distance between pairs
    '''
    # two_dict[element] = pos in array two
    two_dict = {}
    for i, e in enumerate(two):
        two_dict[e] = i
    sum = 0
    for i, e in enumerate(one):
        sum += abs(i - two_dict[e])
    return sum

def permutations_len_total_diff(size):
    '''Given list length, add up list distances for all permutations.'''
    return permutations_total_diff([a for a in range(size)])

def permutations_total_diff(a):
    '''Given a list, add up list distances for all permutations.'''
    sum = 0
    for p in itertools.permutations(a):
        d = compare_lists(a, p)
        logging.debug("distance between %s and %s is %s" % (a, p, d))
        sum += d
    return sum
