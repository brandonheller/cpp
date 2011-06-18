#!/usr/bin/env python
'''Compute shortest pair between src and dst for a weighted graph.

From Survivable Networks: Algorithms for Diverse Routing by Ramesh Bhandari 

See also:
http://en.wikipedia.org/wiki/Edge_disjoint_shortest_pair_algorithm
'''
import sys

# From http://docs.python.org/library/sys.html:
# max    DBL_MAX    maximum representable finite float
INF = sys.float_info.max


def BFS(g, src, dst):
    '''BFS shortest path algorithm.

    Chapter 2.4, Pg. 33 in SN: ADR (see above)

    @param g: NetworkX Graph
    @param src: source node
    @param dst: destination node
    @return path: list of nodes in shortest path from src to dst
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
        return [A, Z]
    else:
        pred = P[Z]
        path = [Z]
        while pred != A:
            path.append(pred)
            pred = P[pred]
        path.append(pred)
        path.reverse()
        return path
