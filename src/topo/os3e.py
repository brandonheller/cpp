#!/usr/bin/env python
'''Generate a network topology corresponding to the Internet2 OS3E.

Info: at http://www.internet2.edu/network/ose

Graph source: http://www.internet2.edu/pubs/OS3Emap.pdf

34 nodes, 41 edges

May not be 100% accurate: 
    Vancouver, Miami are dashed links
    New York is two parallel links between two nodes
    Houston to Baton Rouge has two parallel links
    Sunnyvale to [Portland, Salt Lake] may share a span
'''
import networkx as nx

def OS3EGraph():
    g = nx.Graph()
    g.add_path(["Vancouver", "Seattle"])
    g.add_path(["Seattle", "Missoula", "Minneapolis", "Chicago"])
    g.add_path(["Seattle", "Salt Lake City"])
    g.add_path(["Seattle", "Portland", "Sunnyvale"])
    g.add_path(["Sunnyvale", "Salt Lake City"])
    g.add_path(["Sunnyvale", "Los Angeles"])
    g.add_path(["Los Angeles", "Salt Lake City"])
    g.add_path(["Los Angeles", "Tucson", "El Paso"])
    g.add_path(["Salt Lake City", "Denver"])
    g.add_path(["Denver", "Albuquerque", "El Paso"])
    g.add_path(["Denver", "Kansas City"])
    g.add_path(["Kansas City", "Dallas", "Houston"])
    g.add_path(["El Paso", "Houston"])
    g.add_path(["Houston", "Jackson", "Memphis", "Nashville"])
    g.add_path(["Houston", "Baton Rouge", "Jacksonville"])
    g.add_path(["Chicago", "Indianapolis", "Louisville", "Nashville"])
    g.add_path(["Nashville", "Atlanta"])
    g.add_path(["Atlanta", "Jacksonville"])
    g.add_path(["Jacksonville", "Miami"])
    g.add_path(["Chicago", "Cleveland"])
    g.add_path(["Cleveland", "Buffalo", "Boston", "New York", "Philadelphia", "Washington DC"])
    g.add_path(["Cleveland", "Pittsburgh", "Ashburn", "Washington DC"])
    g.add_path(["Washington DC", "Raleigh", "Atlanta"])
    return g