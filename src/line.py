#!/usr/bin/env python
'''Generate JSON output data to be used in later graphing.'''
import json

from networkx import complete_graph, star_graph, path_graph

from cc import compute, loop_graph

FILENAME = "uptimes_link.json"

# Graph generators: given a size, generate a graph.
graph_types = {
    'complete': (lambda n: complete_graph(n)),
    'star': (lambda n: star_graph(n - 1)),
    'line': (lambda n: path_graph(n)),
    'loop': (lambda n: loop_graph(n))
}

f = open(FILENAME, 'w')

data = {}

algs = ['sssp', 'any']
for alg in algs:
    data[alg] = {}
    for gtype, fcn in graph_types.iteritems():
        values = []
        for i in range(3, 11):
            link_fail = 0.01
            node_fail = 0.0
            max_fail = 1
            g = fcn(i)
            uptime = compute(g, link_fail, node_fail, max_fail, alg)
            values.append((i, uptime))
        data[alg][gtype] = values

print data

json.dump(data, f)
