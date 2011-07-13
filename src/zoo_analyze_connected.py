#!/usr/bin/env python
import sys

from topo_lib import get_topo_graph, num_geo_locations
from zoo_tools import zoo_topos

if __name__ == '__main__':

    if len(sys.argv) <= 1:
        print "using all zoo topos"
        topos = sorted(zoo_topos())
    else:
        topos = sys.argv[1:]
    one_c_c = []  # One connected component
    fully_locationed = []  # All locations found
    some_locationed = []  # Partial locations
    locations_missing = {}  # All w/missing
    noted_topos = {}
    processed = []
    for topo in topos:
        g, usable, note = get_topo_graph(topo)
        if usable:
            processed.append(topo)
        
        if note:
            if note not in noted_topos:
                noted_topos[note] = []
            noted_topos[note].append(topo)
            print topo, ':', note

        if g and (note == "Missing location(s)"):
            num_in, num_out = num_geo_locations(g)
            if num_out > 0 and num_out != g.number_of_nodes():
                if num_out not in locations_missing:
                    locations_missing[num_out] = []
                locations_missing[num_out].append(topo)
            print "topo: %s, in: %s, out: %s" % (topo, num_in, num_out)

    print "topos: %s" % len(topos)
    total_noted = 0
    for note, values in noted_topos.iteritems():
        total_noted += len(values)
    print "processed: %s" % len(processed)
    print "ignored: %s" % len(topos) - len(processed)
    print "*****************************"
    for note, values in noted_topos.iteritems():
        print "** %s (%s):\n%s\n" % (note, len(values), values) 
    print "*****************************"
    print "processed: %s" % processed
    #print "one connected component (%s): \n%s" % (len(one_c_c), one_c_c)
    #print "not one connected component (%s): \n%s" % (len(topos) - len(one_c_c), [a for a in topos if a not in one_c_c])
    #print "*****************************"
    #print "all locations defined (%s): \n%s" % (len(fully_locationed), fully_locationed)
    #print "some locations defined (%s): \n%s" % (len(topos) - len(fully_locationed), [a for a in topos if a not in fully_locationed])
    #print "*****************************"
    #print "some locations defined (%s): \n%s" % (len(some_locationed), some_locationed)
    #print "no locations defined (%s): \n%s" % (len(topos) - len(some_locationed), [a for a in topos if a not in some_locationed])
    print "*****************************"
    print "some locations defined, but some missing:"
    for n, m in locations_missing.iteritems():
        print "\t%s location(s) missing (%s): %s" % (n, len(m), m)
    #print "*****************************"
    #no_loc = set(topos) - set(some_locationed)
    #not_one_c_c = set(topos) - set(one_c_c)
    #unusable = no_loc | not_one_c_c
    #print "unusable: no locations, or multiple connected components (%s): \n%s" % (len(unusable), unusable)