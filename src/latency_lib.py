#!/usr/bin/env python
'''Library of algorithms and helpers for computing latencies.'''

from itertools import combinations
import time

import numpy

from util import sort_by_val

BIG = 10000000

def get_total_path_len(g, controllers, apsp):
    '''Returns the total of path lengths from nodes to nearest controllers.
    
    @param g: NetworkX graph
    @param controllers: list of controller locations
    @return path_len_total: total of path lengths
    '''
    # path_lengths[node] = path from node to nearest item in combo
    path_lengths = {}
    for n in g.nodes():
        # closest_controller records controller w/shortest distance
        # to the currently-considered node.
        closest_controller = None
        shortest_path_len = BIG
        for c in controllers:
            path_len = apsp[n][c]
            if path_len < shortest_path_len:
                closest_controller = c
                shortest_path_len = path_len
        #  pick the best value from that list
        path_lengths[n] = shortest_path_len
    path_len_total = sum(path_lengths.values())
    return path_len_total


def run_optimal_latencies(g, controllers, data, apsp):
    '''Compute best, worst, and mean/median latencies.

    @param controllers: list of numbers of controllers to analyze.
    @param data: JSON data to be augmented.
    @param apsp: all-pairs shortest paths data
    '''

    for i in sorted(controllers):
        # compute best location(s) for i controllers.
    
        print "** combo size: %s" % i
        
        data[i] = {}
    
        best_combo_path_len_total = BIG
        best_combo = None
        worst_combo_path_len_total = -BIG
        worst_combo = None
        start_time = time.time()
    
        path_len_totals = []  # note all path lengths to compute stats later.
    
        combos = 0
    
        # for each combination of i controllers
        for combo in combinations(g.nodes(), i):
            combos += 1
    
            path_len_total = get_total_path_len(g, combo, apsp)
    
            if path_len_total < best_combo_path_len_total:
                best_combo_path_len_total = path_len_total
                best_combo = combo
    
            if path_len_total > worst_combo_path_len_total:
                worst_combo_path_len_total = path_len_total
                worst_combo = combo
    
            path_len_totals.append(path_len_total)
    
        duration = time.time() - start_time
    
        best_combo_path_len = best_combo_path_len_total / float(g.number_of_nodes())
        worst_combo_path_len = worst_combo_path_len_total / float(g.number_of_nodes())
        mean_combo_path_len = sum(path_len_totals) / float(combos) / float(g.number_of_nodes())
        median_combo_path_len = numpy.median(path_len_totals) / float(g.number_of_nodes())
    
        print "\topt"
        print "\t\tbest: %s %s" % (best_combo_path_len, best_combo)
        print "\t\tworst: %s %s" % (worst_combo_path_len, worst_combo)
        print "\t\tmean: %s" % (mean_combo_path_len)
        print "\t\tmedian: %s" % (median_combo_path_len)
        print "\t\tduration: %s" % duration
    
        data[i] = {
            'opt': {
                'latency': best_combo_path_len,
                'duration': duration,
                'combo': best_combo
            },
            'worst': {
                'latency': worst_combo_path_len,
                'combo': worst_combo
            },
            'random_mean': {
                'latency': mean_combo_path_len,
            },
            'random_median': {
                'latency': median_combo_path_len
            },
        }

def run_greedy_informed(data, g, apsp):
    '''Greedy algorithm for computing node ordering

    @param data: JSON data on which to append
    @param g: NetworkX graph
    @param apsp: all-pairs shortest data

    Re-calculates best value at each step, given the previous sol'n of size n-1.
    '''
    greedy_informed = []
    for i in range(1, g.number_of_nodes() + 1):        
        best_next_choice_path_len_total = BIG
        best_next_choice = None
    
        start_time = time.time()
    
        for n in [n for n in g.nodes() if n not in greedy_informed]:
    
            path_len_total = get_total_path_len(g, greedy_informed + [n], apsp)
            #print n, path_len_total, greedy_informed + [n]
    
            if path_len_total < best_next_choice_path_len_total:
                best_next_choice_path_len_total = path_len_total
                best_next_choice = n
    
        duration = time.time() - start_time
    
        greedy_informed.append(best_next_choice)
    
        best_next_choice_path_len = best_next_choice_path_len_total / float(g.number_of_nodes())
    
        path_len = best_next_choice_path_len
        if i in data and "opt" in data[i]:
            ratio = path_len / data[i]["opt"]["latency"] 
        else:
            ratio = 0
    
        print "** combo size: %s" % i
        print "\tgreedy_informed"
        print "\t\tlatency: %s %s" % (best_next_choice_path_len, best_next_choice)
        print "\t\tduration: %s" % duration
        print "\t\tcombo: %s" % greedy_informed
        print "\t\tratio: %s" % ratio
    
        json_to_add = {
            'greedy-informed': {
                'latency': best_next_choice_path_len,
                'combo': greedy_informed,
                'duration': duration,
                'ratio': ratio
            }
        }
    
        if i not in data:
            data[i] = {}
        data[i].update(json_to_add)


def run_greedy_alg(data, g, alg, param_name, greedy_dict, apsp,
                   max_iters = None, reversed = True):
    '''Run a greedy algorithm for optimizing latency.

    @param data: JSON data to append to, keyed by id (0...n)
        appended data will include the param_name, combination, and duration
    @param g: NetworkX graph
    @param alg: algorithm name
    @param param_name: semantic meaning of greedy parameter (e.g. latency)
    @param greedy_dict: dict with node keys and values for greedy choices
    @param apsp: all-pairs shortest data
    @param max_iters: maximum iterations; do all if falsy
    @param reversed: if True, larger values are picked first
    '''
    soln = []
    i = 0
    for n, value in sort_by_val(greedy_dict, reversed):
        i += 1
        if max_iters and i > max_iters:
            break
        soln.append(n)
        path_len_total = get_total_path_len(g, soln, apsp)
        duration = 0
        path_len = path_len_total / float(g.number_of_nodes())
        if i in data and "opt" in data[i]:
            ratio = path_len / data[i]["opt"]["latency"] 
        else:
            ratio = 0    

        json_to_add = {
            alg: {
                param_name: path_len,
                'duration': duration,
                'combo': soln,
                'ratio': 0
            }
        }

        print "** combo size: %s" % i
        print "\t" + alg
        print "\t\t%s: %s" % (param_name, path_len)
        print "\t\tduration: %s" % duration
        print "\t\tcombo: %s" % soln
        print "\t\tratio: %s" % ratio

        if i not in data:
            data[i] = {}
        data[i].update(json_to_add)
