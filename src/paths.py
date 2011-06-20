#!/usr/bin/env python
'''Compute shortest pair between src and dst for a weighted graph.

From Survivable Networks: Algorithms for Diverse Routing by Ramesh Bhandari 

See also:
http://en.wikipedia.org/wiki/Edge_disjoint_shortest_pair_algorithm
'''
import sys

import networkx as nx

from lib.graph import interlacing_edges, pathlen, edges_on_path
from lib.graph import flip_and_negate_path

# From http://docs.python.org/library/sys.html:
# max    DBL_MAX    maximum representable finite float
INF = sys.float_info.max


def BFS(g, src, dst):
    '''BFS shortest path algorithm.

    Chapter 2.4, Pg. 33 in SN: ADR (see above)

    @param g: NetworkX Graph
    @param src: source node
    @param dst: destination node
    @return path: list of nodes in shortest path from src to dst, or None if
        no path exists.
    '''
    d = {}  # d[i] is distance of vertex i (in V) from source vertex A.  It
            # is the sum of arcs in a possible path from vertex A to vertex i.
    P = {}  # P[i] is predecessor of vertex i on the same path.
    A = src
    Z = dst
    V = g.nodes()

    def l(a, b):
        return g[a][b]['weight']

    # Step 1:
    # Start with:
    #  d(A)  = 0
    d[A] = 0.0
    #  d(i) = INF for all i in V (i != A)
    for i in V:
        if i != A:
            d[i] = INF
    # Assign P(i) = A for all i in V (i != A)
    for i in V:
        if i != A:
            P[i] = A
    # Let Gamma^T denote the set of vertices from which search or scanning
    # (fanning out) takes place in a given iteration, and let GammaI denote
    # the set of vertices whose labels are updated in that iteration.
    # Gamma_J as before denotes the set of neighbor vertices of vertex j.  Start
    # with GammaT = {A}.
    GammaT = set([])  # Set of vertices from which search or scanning
                      # (fanning out) takes place in a given iteration
    GammaI = set([])  # set of vertices whose labels are updated in that
                      # iteration.
    GammaT.add(A)

    while True:
        # Step 2:
        # Set GammaI = {null set}
        GammaI = set([])
        # For all j in GammaT
        for j in GammaT:
            # do the following:
            # For all i in GammaJ:
            for i in g.neighbors(j):
                # if d(j) + l(ji) < d(i) and d(j) + l(ji) < d(Z):
                #   set d(i) = d(j) + l(ji)
                #       P(i) = j
                #       GammaI = GammaI union {i}
                if d[j] + l(j, i) < d[i] and d[j] + l(j, i) < d[Z]:
                    d[i] = d[j] + l(j, i)
                    P[i] = j
                    GammaI.add(i)
        # Is this at the right level?  Ambiguous from description.
        # Set GammaT = GammaI - (GammaI intersect {Z}).
        GammaT = GammaI - (GammaI & set([Z]))
        
        # Step 3:
        # If GammaT = {null set}, END;
        if GammaT == set([]):
            break
        else:
            # otherwise go to 2.
            pass

    # Recover & return path
    if P[Z] == A:
        if g.has_edge(A, Z):
            return [A, Z]
        else:
            # Didn't find a path :-(
            return None
    else:
        pred = P[Z]
        path = [Z]
        while pred != A:
            path.append(pred)
            pred = P[pred]
        path.append(pred)
        path.reverse()
        return path


def two_step_edge_disjoint_pair(g, src, dst):
    '''Return shortest path and edge-disjoint second path from src to dst.

    NOTE: not guaranteed to return the combined shortest pair!  See pg. 40.

    @param g: NetworkX Graph object
    @param src: src node label
    @param dst: dst node label
    @param paths: two-element list of path lists
    '''
    g2 = g.copy()
    shortest_path = BFS(g2, src, dst)
    for i, n in enumerate(shortest_path):
        if i != len(shortest_path) - 1:
            g2.remove_edge(n, shortest_path[i + 1])
    return [shortest_path, BFS(g2, src, dst)]


def two_step_vertex_disjoint_pair(g, src, dst):
    '''Return shortest path and vertexx-disjoint second path from src to dst.

    NOTE: not guaranteed to return the combined shortest pair!  See pg. 40.

    @param g: NetworkX Graph object
    @param src: src node label
    @param dst: dst node label
    @param paths: two-element list of path lists
    '''
    g2 = g.copy()
    shortest_path = BFS(g2, src, dst)
    g2.remove_nodes_from(shortest_path[1:-1])
    return [shortest_path, BFS(g2, src, dst)]


def edge_disjoint_shortest_pair(g, src, dst):
    '''Return list of two edge-disjoint paths w/shortest total cost.

    @param g: NetworkX Graph object
    @param src: src node label
    @param dst: dst node label
    @param paths: two-element list of path lists, arbitrary ordering
    '''
    # 1. Use BFS to get shortest path.
    shortest_path = BFS(g, src, dst)

    # 2. Replace each edge of the shortest path (equivalent to two oppositely
    # directed arcs) by a single arc directed toward the source vertex.
    # 3. Make the length of each of the above arcs negative.
    g2 = flip_and_negate_path(g, shortest_path)

    # 4. Run the modified Dijkstra or the BFS algorithm again and from the
    # source vertex to the destination vertex in the above modified graph.
    shortest_path_2 = BFS(g2, src, dst)
    first_pathtotal = pathlen(g, shortest_path) + pathlen(g2, shortest_path_2)

    # 5. Transform to the original graph, and erase any interlacing edges of
    # the two paths found.  Group the remaining edges to obtain the shortest
    # pair of edge-disjoint paths.
    g3 = nx.Graph()
    g3.add_path(shortest_path)
    # copy edges on path:
    for a, b in edges_on_path(shortest_path):
        g3[a][b]['weight'] = g[a][b]['weight']
    g3.add_path(shortest_path_2)
    for a, b in edges_on_path(shortest_path_2):
        g3[a][b]['weight'] = g[a][b]['weight']
    for a, b in interlacing_edges(shortest_path, shortest_path_2):
        g3.remove_edge(a, b)

    # Find a path through graph and remove edges used.
    path1 = BFS(g3, src, dst)
    path1len = pathlen(g3, path1)
    for a, b in edges_on_path(path1):
        g3.remove_edge(a, b)
    path2 = BFS(g3, src, dst)
    path2len = pathlen(g3, path2)
    for a, b in edges_on_path(path2):
        g3.remove_edge(a, b)
    assert g3.number_of_edges() == 0

    second_pathtotal = path1len + path2len
    assert(first_pathtotal == second_pathtotal)

    return [path1, path2]
