#!/usr/bin/env python
import cc
from topo.os3e import OS3EGraph

g = OS3EGraph()

link_fail_prob = 0.01
print "OS3E"
print "sssp: %03f" % cc.compute(g, link_fail_prob, 0, 1, 'sssp')
print "any: %03f" % cc.compute(g, link_fail_prob, 0, 1, 'any')