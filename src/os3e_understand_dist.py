#!/usr/bin/env python
'''Create data for plot comparing algorithm uptimes on Internet2 graph.'''

from operator import itemgetter
import json

import networkx as nx

from cc import compute, sssp_conn
from topo.os3e import OS3EGraph

link_fail_prob = 0.001
ALGS = [sssp_conn] # ['sssp', 'any']

g = OS3EGraph()

uptimes = {}
for alg in ALGS:
    uptimes[alg] = []
    lines = uptimes[alg]
    uptime, conn_data = compute(g, link_fail_prob, 0, 1, alg)
    dc = nx.degree_centrality(g)
    cc = nx.closeness_centrality(g)
    bc = nx.betweenness_centrality(g)
    ec = nx.eigenvector_centrality(g)
    #print conn_data
    tuples = []
    for key, val in conn_data.iteritems():
        tuples.append((key, val, dc[key], cc[key], bc[key], ec[key]))

    tuples = sorted(tuples, key = itemgetter(1), reverse = True)
    for vals in tuples:
        print "%016s %1.5f %05f %05f %05f %05f" % vals

    # check if cc is ordered
    bc_prev = 1.0
    for vals in tuples:
        bc = vals[3]
        if bc > bc_prev:
            raise Exception("not sorted in order!!! %s %s" % (vals[0], bc))
        bc_prev = vals[3]

    lines.append((link_fail_prob, uptime))
    print "%s %03f %03f" % (alg, link_fail_prob, uptime)

#json.dump(uptimes, f)