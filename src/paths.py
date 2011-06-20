#!/usr/bin/env python
'''Compute shortest pair between src and dst for a weighted graph.

From Survivable Networks: Algorithms for Diverse Routing by Ramesh Bhandari 

See also:
http://en.wikipedia.org/wiki/Edge_disjoint_shortest_pair_algorithm
'''
import sys

import networkx as nx

from lib.graph import interlacing_edges, pathlen, edges_on_path
from lib.graph import flip_and_negate_path, remove_edge_bidir, add_edge_bidir

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


def grouped_shortest_pair(g, shortest_path, shortest_path_2):
    '''Find shortest pair of paths of two interlacing original paths.

    Last step of the optimal edge-disjoint and vertex-disjoint shortest-pair
    algorithms.

    @param g: original NetworkX Graph or DiGraph
    @param shortest_path: list of path nodes
    @param shortest_path_2: list of path nodes
    @return path1: first non-interlacing shortest path
    @return path2: second non-interlacing shortest path
    '''
    src = shortest_path[0]
    dst = shortest_path[-1]
    assert src == shortest_path_2[0]
    assert dst == shortest_path_2[-1]

    g3 = nx.Graph()
    g3.add_path(shortest_path)
    g3.add_path(shortest_path_2)
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
    for a, b in edges_on_path(path1):
        g3.remove_edge(a, b)
    path2 = BFS(g3, src, dst)
    for a, b in edges_on_path(path2):
        g3.remove_edge(a, b)
    assert g3.number_of_edges() == 0

    return path1, path2


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
    path1, path2 = grouped_shortest_pair(g, shortest_path, shortest_path_2)

    path1len = pathlen(g, path1)
    path2len = pathlen(g, path2)
    second_pathtotal = path1len + path2len
    assert(first_pathtotal == second_pathtotal)

    return [path1, path2]


def vertex_disjoint_shortest_pair(g, src, dst):
    '''Return list of two vertex-disjoint paths w/shortest total cost.

    @param g: NetworkX Graph object
    @param src: src node label
    @param dst: dst node label
    @param paths: two-element list of path lists, arbitrary ordering
    '''
    # 1. Use BFS to get shortest path.
    shortest_path = BFS(g, src, dst)

    # 2. Replace each edge of the shortest path (equivalent to two oppositely
    # directed arcs) by a single arc directed toward the source vertex.
    # Also make the arc lengths negative.
    g2 = flip_and_negate_path(g, shortest_path)

    # 3. Find the first intermediate vertex from the destination vertex whose
    # degree is greater than 3 (vertex F in Figure 3.16b).  Replace the
    # external edges by arcs incident on this vertex.

    # Use list comprehension to get an indexable reversed array.
    sp_rev = [n for n in reversed(shortest_path)]
    special_v_index = len(shortest_path) - 1  # Large to skip if not found.
    for i in range(1, len(shortest_path) - 1):
        v = sp_rev[i]
        if g.degree(v) > 3:
            next_v = sp_rev[i + 1]
            prev_v = sp_rev[i - 1]
            # We don't need to delete prev_v's edge because it was already
            # made uni-direction in flip_and_negate_path.
            ext_vs = [n for n in g.neighbors(v) if n != next_v and n != prev_v]
            for ext_v in ext_vs:
                # Since g2 is directed, remove outgoing edge only, leaving
                # the internally-directed edge.
                g2.remove_edge(v, ext_v)
            special_v_index = i
            break

    # 4. Split each intermediate vertex on the shortest path (except the vertex
    # found in Step 3) into as many subvertices as there are external edges
    # connected to it; connect the external edges to these subvertices, one
    # edge to one subvertex (see Figure 3.16c).  Note splitting is absent for
    # a vertex with degree 2 or 3.

    subvertices = {}  # subvertices[v] = list of created subvertices
    special_v = sp_rev[special_v_index]
    subvertices[special_v] = [special_v]
    for i in range(special_v_index + 1, len(shortest_path)):
        v = sp_rev[i]
        subvertices[v] = []
        if g.degree(v) > 3:
            prev_v = sp_rev[i - 1]
            next_v = sp_rev[i + 1]
            ext_vs = [n for n in g.neighbors(v) if n != next_v and n != prev_v]

            primes = ""
            for ext_v in ext_vs:
                # Create subvertex: vertex-prime
                primes += "'"
                subvertex = v + primes
                subvertices[v].append(subvertex)

                # Step 4: split and connect external edge
                add_edge_bidir(g2, subvertex, ext_v, g[v][ext_v]['weight'])

            # Remove original vertex v, which will delete all edges to v.
            # Edges connecting to v on the reversed shortest path will be
            # added in the next step.
            g2.remove_node(v)

        else:
            subvertices[v].append(v)

    # 5. Add arcs in parallel on the shortest path such that each subvertex
    # belonging to a vertex is connected to subvertices of a neighboring
    # vertex.   All the added arcs must be directed toward the source vertex.
    # If m and n denote the number of subvertices of a pair of neighboring
    # vertices, there will be a total of m x n arcs in parallel between them
    # (see Figure 3.16d), each with a length equal to the negative of the
    # length of the corresponding edge in the original graph.
    for i in range(special_v_index, len(shortest_path) - 1):
        v = sp_rev[i]
        next_v = sp_rev[i + 1]
        for v_src in subvertices[v]:
            for next_v_dst in subvertices[next_v]:
                g2.add_edge(v_src, next_v_dst)
                g2[v_src][next_v_dst]['weight'] = -g[v][next_v]['weight']

    # 6. Run the modified Dijkstra or the BFS algorithm again from the source
    # vertex to the destination vertex in the above modified graph.
    shortest_path_2 = BFS(g2, src, dst)

    # 7. (A) Coalesce the subvertices back into their parent vertices, and the
    # parallel arcs into single arcs.  (B) Replace single arcs on the shortest
    # path by edges of positive length.  (C) Remove interlacing edges of the
    # two paths found above to obtain the shortest pair of vertex-disjoint
    # paths.
    for i, v in enumerate(sp_rev):
        # Ignore destination
        if i == 0 or i == len(sp_rev) - 1:
            continue
        prev_v = sp_rev[i - 1]
        next_v = sp_rev[i + 1]
        # Is this a split vertex?
        if v in subvertices and len(subvertices[v]) > 1:
            g2.add_node(v)
            # (A) Coalesce subvertices back into parent vertices
            for subvertex in subvertices[v]:
                # Restore external edges of subvertics
                neighbors = g2.neighbors(subvertex)
                ext_vs = [n for n in neighbors if n != prev_v and n != next_v]
                for ext_v in ext_vs:
                    add_edge_bidir(g2, v, ext_v, g[v][ext_v]['weight'])
                # Clear subvertex and all its edges
                g2.remove_node(subvertex)
        # (B) Replace single arcs on the shortest path by edges of
        # positive length.
        add_edge_bidir(g2, prev_v, v, g[prev_v][v]['weight'])
        add_edge_bidir(g2, v, next_v, g[v][next_v]['weight'])

    # Second part of (A) - coalesce nodes names in the second path.
    # Strip away any "prime" characters.
    shortest_path_2 = [n.rstrip("'") for n in shortest_path_2]

    # (C) Remove interlacing edges and return shortest pair
    path1, path2 = grouped_shortest_pair(g, shortest_path, shortest_path_2)
    return [path1, path2]
