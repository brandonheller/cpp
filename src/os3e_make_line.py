#!/usr/bin/env python
'''Create data for plot comparing algorithm uptimes on Internet2 graph.'''

import json

import cc
from topo.os3e import OS3EGraph

FILENAME = "os3e_link.json"

MAX_LINK_FAIL_PROB = 0.02
LINK_FAIL_INCREMENT = 0.002
ALGS = ['sssp', 'any']

f = open(FILENAME, 'w')

g = OS3EGraph()

uptimes = {}
for alg in ALGS:
    uptimes[alg] = []
    lines = uptimes[alg]
    for i in range(1, int(MAX_LINK_FAIL_PROB / LINK_FAIL_INCREMENT)):
        link_fail_prob = i * LINK_FAIL_INCREMENT
        uptime = cc.compute(g, link_fail_prob, 0, 1, alg)
        lines.append((link_fail_prob, uptime))
        print "%s %03f %03f" % (alg, link_fail_prob, uptime)

json.dump(uptimes, f)