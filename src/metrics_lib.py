#!/usr/bin/env python
'''Library of algorithms and helpers for computing metrics.'''

from itertools import combinations
import time

import numpy

from itertools_recipes import random_combination
from util import sort_by_val

BIG = 10000000

def get_total_path_len(g, controllers, apsp, weighted = False):
    '''Returns the total of path lengths from nodes to nearest controllers.
    
    @param g: NetworkX graph
    @param controllers: list of controller locations
    @param apsp: all-pairs shortest paths data
    @param weighted: is graph weighted?
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


def fairness(values):
    '''Compute Jain's fairness index for a list of values.

    See http://en.wikipedia.org/wiki/Fairness_measure for fairness equations.

    @param values: list of values
    @return fairness: JFI
    '''
    num = sum(values) ** 2
    denom = len(values) * sum([i ** 2 for i in values])
    return num / float(denom)


def controller_split_fairness(g, combo, apsp, weighted):
    '''Compute Jain's fairness index for switch/controller allocation.

    @param g: NetworkX graph
    @param controllers: list of controller locations
    @param apsp: all-pairs shortest paths data
    @param weighted: is graph weighted?
    @return fairness: JFI measure for the input
    '''
    # allocations[i] is total switches connected to controller i.  
    # For switches equally distance from n controllers, split share equally.
    allocations = {}
    for n in g.nodes():
        closest_controllers = set([])
        closest_controller_dist = BIG
        for c in combo:
            dist = apsp[n][c]
            if dist < closest_controller_dist:
                closest_controller_dist = dist
                closest_controllers = set([c])
            elif dist == closest_controller_dist:
                closest_controllers.add(c)
        for c in closest_controllers:
            if c not in allocations:
                allocations[c] = 0
            allocations[c] += 1 / float(len(closest_controllers))

    #print allocations.values()
    try:
        assert abs(sum(allocations.values()) - g.number_of_nodes()) < 0.0001
    except AssertionError:
        import code
        code.interact(local=locals())

    return fairness(allocations.values())


def run_all_combos(metrics, g, controllers, data, apsp, weighted = False,
                   write_dist = False, write_combos = False):
    '''Compute best, worst, and mean/median latencies, plus fairness.

    @param metrics: metrics to compute: in ['latency', 'fairness']
    @param g: NetworkX graph
    @param controllers: list of numbers of controllers to analyze.
    @param data: JSON data to be augmented.
    @param apsp: all-pairs shortest paths data
    @param weighted: is graph weighted?
    @param write_dist: write all values to the distribution.
    '''

    for combo_size in sorted(controllers):
        # compute best location(s) for i controllers.
    
        print "** combo size: %s" % combo_size

        best_combo_path_len_total = BIG
        best_combo = None
        worst_combo_path_len_total = -BIG
        worst_combo = None
        start_time = time.time()
    
        path_len_totals = []  # note all path lengths to compute stats later.

        distribution = [] # list of {combo, key:value}'s in JSON, per combo
        # for each combination of i controllers
        for combo in combinations(g.nodes(), combo_size):
    
            # Latency computation
            path_len_total = get_total_path_len(g, combo, apsp, weighted)
    
            if path_len_total < best_combo_path_len_total:
                best_combo_path_len_total = path_len_total
                best_combo = combo
    
            if path_len_total > worst_combo_path_len_total:
                worst_combo_path_len_total = path_len_total
                worst_combo = combo

            path_len_totals.append(path_len_total)

            # Fairness computation
            fairness_metric = controller_split_fairness(g, combo, apsp, weighted)

            if write_dist:
                json_entry = {}
                if 'latency' in metrics:
                    json_entry['latency'] = path_len_total / float(g.number_of_nodes())
                if 'fairness' in metrics:
                    json_entry['fairness'] = fairness_metric
                if write_combos:
                    json_entry['combo'] = combo

                distribution.append(json_entry)

        duration = time.time() - start_time
    
        best_combo_path_len = best_combo_path_len_total / float(g.number_of_nodes())
        worst_combo_path_len = worst_combo_path_len_total / float(g.number_of_nodes())
        mean_combo_path_len = sum(path_len_totals) / float(combo_size) / float(g.number_of_nodes())
        median_combo_path_len = numpy.median(path_len_totals) / float(g.number_of_nodes())
    
        print "\topt"
        print "\t\tbest: %s %s" % (best_combo_path_len, best_combo)
        print "\t\tworst: %s %s" % (worst_combo_path_len, worst_combo)
        print "\t\tmean: %s" % (mean_combo_path_len)
        print "\t\tmedian: %s" % (median_combo_path_len)
        print "\t\tduration: %s" % duration
    
        data[unicode(combo_size)] = {
            'opt': {
                'latency': best_combo_path_len,
                'duration': duration,
                'combo': best_combo
            },
            'worst': {
                'latency': worst_combo_path_len,
                'combo': worst_combo,
                'ratio': worst_combo_path_len / best_combo_path_len
            },
            'random_mean': {
                'latency': mean_combo_path_len,
                'ratio': mean_combo_path_len / best_combo_path_len
            },
            'random_median': {
                'latency': median_combo_path_len,
                'ratio': median_combo_path_len / best_combo_path_len
            },
            'distribution': distribution
        }


def run_best_n(data, g, apsp, n, weighted):
    '''Use best of n runs

    @param data: JSON data on which to append
    @param g: NetworkX graph
    @param apsp: all-pairs shortest data
    @param n: number of combinations to try
    @param weighted: is graph weighted?

    Randomly computes n possibilities and chooses the best one.
    '''
    def iter_fcn(combo_size, soln):
        '''Construct custom iter fcn.

        @param combo_size
        @param soln: partial, greedily-built sol'n.
        @return choice: node selection.
        '''
        best_next_combo_path_len_total = BIG
        best_next_combo = None
        for i in range(n):

            combo = random_combination(g.nodes(), combo_size)
            # oddly, tuples don't automatically print.
            # convert to array to get past this issue.
            combo = [c for c in combo]
            if n < 5:
                print "random combo: %s" % combo

            path_len_total = get_total_path_len(g, combo, apsp, weighted)

            if path_len_total < best_next_combo_path_len_total:
                best_next_combo_path_len_total = path_len_total
                best_next_combo = combo
    
        return best_next_combo

    run_alg(data, g, "best-n-" + str(n), "latency", iter_fcn, apsp, weighted)
    

def run_worst_n(data, g, apsp, n, weighted):
    '''Use worst of n runs

    @param data: JSON data on which to append
    @param g: NetworkX graph
    @param apsp: all-pairs shortest data
    @param n: number of combinations to try

    Randomly computes n possibilities and chooses the worst one.
    '''
    def iter_fcn(combo_size, soln):
        '''Construct custom iter fcn.

        @param combo_size
        @param soln: partial, greedily-built sol'n.
        @return choice: node selection.
        '''
        worst_next_combo_path_len_total = -BIG
        worst_next_combo = None
        for i in range(n):

            combo = random_combination(g.nodes(), combo_size)
            # oddly, tuples don't automatically print.
            # convert to array to get past this issue.
            combo = [c for c in combo]
            if n < 5:
                print "random combo: %s" % combo

            path_len_total = get_total_path_len(g, combo, apsp, weighted)

            if path_len_total > worst_next_combo_path_len_total:
                worst_next_combo_path_len_total = path_len_total
                worst_next_combo = combo
    
        return worst_next_combo

    run_alg(data, g, "worst-n-" + str(n), "latency", iter_fcn, apsp, weighted)


def run_greedy_informed(data, g, apsp, weighted):
    '''Greedy algorithm for computing node ordering

    @param data: JSON data on which to append
    @param g: NetworkX graph
    @param apsp: all-pairs shortest data
    @param weighted: is graph weighted?

    Re-calculates best value at each step, given the previous sol'n of size n-1.
    '''
    def greedy_choice(combo_size, soln):
        '''Construct custom greedy choice fcn.

        @param combo_size
        @param soln: partial, greedily-built sol'n.
        @return choice: node selection.
        '''
        best_next_choice_path_len_total = BIG
        best_next_choice = None
        for n in [n for n in g.nodes() if n not in soln]:

            path_len_total = get_total_path_len(g, soln + [n], apsp, weighted)
            #print n, path_len_total, greedy_informed + [n]
    
            if path_len_total < best_next_choice_path_len_total:
                best_next_choice_path_len_total = path_len_total
                best_next_choice = n
    
        return best_next_choice

    run_greedy_alg(data, g, "greedy-informed", "latency", greedy_choice, apsp, weighted)


def run_greedy_alg_dict(data, g, alg, param_name, greedy_dict, apsp, weighted,
                   max_iters = None, reversed = True):
    '''Convenience fcn to run a greedy algorithm w/choices from a list.

    @param data: JSON data to append to, keyed by id (0...n)
        appended data will include the param_name, combination, and duration
    @param g: NetworkX graph
    @param alg: algorithm name
    @param param_name: semantic meaning of greedy parameter (e.g. latency)
    @param greedy_dict: dict mapping node names to param values.
    @param apsp: all-pairs shortest data
    @param weighted: is graph weighted?
    @param max_iters: maximum iterations; do all if falsy
    @param reversed: if True, larger values are selected first.
    '''
    greedy_dict_sorted = sort_by_val(greedy_dict, reversed)
    def greedy_choice(combo_size, soln):
        '''Construct custom greedy choice fcn.

        @param i: iteration (0 is first one)
        @param soln: partial, greedily-built sol'n.
        @return choice: node selection.
        '''
        i = combo_size - 1
        n, value = greedy_dict_sorted[i]
        return n

    run_greedy_alg(data, g, alg, param_name, greedy_choice, apsp, weighted)


def run_greedy_alg(data, g, alg, param_name, greedy_choice, apsp, weighted,
                   max_iters = None):
    '''Run a greedy algorithm for optimizing latency.

    @param data: JSON data to append to, keyed by id (0...n)
        appended data will include the param_name, combination, and duration
    @param g: NetworkX graph
    @param alg: algorithm name
    @param param_name: semantic meaning of greedy parameter (e.g. latency)
    @param greedy_choice: fcn with:
        @param combo_size
        @param soln: partial, greedily-built sol'n.
        @return choice: node selection.
    @param apsp: all-pairs shortest data
    @param weighted: is graph weighted?
    @param max_iters: maximum iterations; do all if falsy
    '''
    def iter_fcn(combo_size, soln):
        choice = greedy_choice(combo_size, soln)
        soln.append(choice)
        return soln

    run_alg(data, g, alg, param_name, iter_fcn, apsp, weighted,
                   max_iters = None)


def run_alg(data, g, alg, param_name, iter_fcn, apsp, weighted,
                   max_iters = None):
    '''Run an iterative algorithm for optimizing latency.

    @param data: JSON data to append to, keyed by id (0...n)
        appended data will include the param_name, combination, and duration
    @param g: NetworkX graph
    @param alg: algorithm name
    @param param_name: semantic meaning of greedy parameter (e.g. latency)
    @param iter_fcn: fcn with:
        @param combo_size: size of current group of controllers
        @param soln: last solution
        @return new_soln: best sol'n for this iteration
    @param apsp: all-pairs shortest data
    @param weighted: is graph weighted?
    @param max_iters: maximum iterations; do all if falsy
    '''
    soln = []
    for combo_size in range(1, g.number_of_nodes() + 1):
        if max_iters and combo_size > max_iters:
            break

        start = time.time()
        soln = iter_fcn(combo_size, soln)
        duration = time.time() - start

        path_len_total = get_total_path_len(g, soln, apsp, weighted)

        path_len = path_len_total / float(g.number_of_nodes())
        if str(combo_size) in data and "opt" in data[str(combo_size)]:
            if data[str(combo_size)]["opt"]["latency"] == 0:
                ratio = 1
            else:
                ratio = path_len / data[str(combo_size)]["opt"]["latency"]
        else:
            ratio = 0    

        json_to_add = {
            alg: {
                param_name: path_len,
                'duration': duration,
                'combo': soln,
                'ratio': ratio
            }
        }

        print "** combo size: %s" % combo_size
        print "\t" + alg
        print "\t\t%s: %s" % (param_name, path_len)
        print "\t\tduration: %s" % duration
        print "\t\tcombo: %s" % soln
        print "\t\tratio: %s" % ratio
        print "\t\tpath_len: %s" % path_len

        if unicode(combo_size) not in data:
            data[unicode(combo_size)] = {}
        data[unicode(combo_size)].update(json_to_add)
