#!/usr/bin/env python
'''Library of algorithms and helpers for computing metrics.'''

from itertools import combinations
import logging
import multiprocessing
import time

import numpy
import networkx as nx

from itertools_recipes import random_combination, choose
from util import sort_by_val

BIG = 10000000

lg = logging.getLogger("metrics_lib")


def closest_controllers(g, controllers, apsp):
    '''Returns a dict of each node to its closest controller.
    
    @param g: NetworkX graph
    @param controllers: list of controller locations
    @param apsp: all-pairs shortest paths data
    @return closest_controllers: dict of node to closest controller
    '''
    closest_controllers = {}  # map each node to closest controller
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
        closest_controllers[n] = closest_controller
    return closest_controllers


def get_total_path_len(g, controllers, apsp, weighted = False):
    '''Returns the total of path lengths from nodes to nearest controllers.

    @param g: NetworkX graph
    @param controllers: list of controller locations
    @param apsp: all-pairs shortest paths data
    @param weighted: is graph weighted?
    @return path_len_total: total of path lengths
    '''
    closest = closest_controllers(g, controllers, apsp)
    return sum([apsp[n][c] for n, c in closest.iteritems()])


def worst_case_latency(g, controllers, apsp, weighted = False):
    '''Returns the latency of the switch farthest from a controller.

    @param g: NetworkX graph
    @param controllers: list of controller locations
    @param apsp: all-pairs shortest paths data
    @param weighted: is graph weighted?
    @return worst_case_latency
    '''
    closest = closest_controllers(g, controllers, apsp)
    return max([apsp[n][c] for n, c in closest.iteritems()])


def fraction_within_latency(g, combo, apsp, lat_bound, weighted = False):
    '''Returns the fraction of nodes that are under a latency bound.

    @param g: NetworkX graph
    @param combo: list of controller locations
    @param apsp: all-pairs shortest paths data
    @param weighted: is graph weighted?
    @return fraction_within_latency
    '''
    closest = closest_controllers(g, combo, apsp)
    latencies = [apsp[n][c] for n, c in closest.iteritems()]
    return sum([l <= lat_bound for l in latencies]) / float(g.number_of_nodes())


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
    # For switches equally distant from n controllers, split share equally.
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

    assert abs(sum(allocations.values()) - g.number_of_nodes()) < 0.0001

    return fairness(allocations.values())


def control_traffic_congestion(g, combo, apsp, apsp_paths, weighted, extra_params = None):
    '''Find the worst-case control traffic overlap.

    That is, the single link for which the most control traffic is assigned
    along a shortest path.

    @param g: NetworkX graph
    @param controllers: list of controller locations
    @param apsp: all-pairs shortest paths data
    @param apsp_paths: all-pairs shortest paths path data
    @param weighted: is graph weighted?
    @return congestion: fraction of switches' traffic along worst-case link.
    '''
    # Counters for each used edge
    traffic = nx.Graph()
    for src, dst in g.edges():
        traffic.add_edge(src, dst)
        traffic[src][dst]["weight"] = 0.0

    # allocations[i] is total switches connected to controller i.
    # For switches equally distant from n controllers, split share equally.
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

        # Assign an equal fraction on each edge to each closest path.
        for c in closest_controllers:
            path = apsp_paths[n][c]
            for i, path_node in enumerate(path):
                if i != len(path) - 1:
                    traffic[path_node][path[i + 1]]["weight"] += 1.0 / float(len(closest_controllers))

    most_congested_total = -BIG
    most_congested_edge = None
    for src, dst in g.edges():
        w = traffic[src][dst]["weight"]
        if w > most_congested_total:
            most_congested_total = w
            most_congested_edge = [src, dst]

    #print "most congested edge: %s" % most_congested_edge
    #print "most congested total: %s" % most_congested_total
    
    # Return the largest such edge as a fraction of the number of switches.
    return most_congested_total / float(g.number_of_nodes())


def path_is_clear(path, failed_links):
    '''Return true if path and failed_links are disjoint.
    
    @param path: list of nodes
    @param failed_links: list of (src, dst) node pairs
    '''
    failed_links_set = set(failed_links)
    path_links_set = set([])
    for i, path_node in enumerate(path):
        if i != len(path) - 1:
            path_links_set.add((path_node, path[i + 1]))
            path_links_set.add((path[i + 1], path_node))

    # Path is clear if no intersection.
    return len(path_links_set.intersection(failed_links_set)) == 0


def connectivity_sssp(g, combo, apsp, apsp_paths, weighted, failed_links):
    '''Find the connectivity considering only SSSP-computed paths.

    That is, the fraction of switches happily connecting to their primary
    controller.

    What about switches that are equidistant?  Average results.

    @param g: NetworkX graph
    @param controllers: list of controller locations
    @param apsp: all-pairs shortest paths data
    @param apsp_paths: all-pairs shortest paths path data
    @param weighted: is graph weighted?
    @param failed_edges: list of edge failures
    @return connectivity: fraction of connected switches, on average
    '''
    connected = 0  # Number of connected switches
    for n in g.nodes():
        # Find best controller set
        closest_controllers = set([])
        closest_controller_dist = BIG
        for c in combo:
            dist = apsp[n][c]
            if dist < closest_controller_dist:
                closest_controller_dist = dist
                closest_controllers = set([c])
            elif dist == closest_controller_dist:
                closest_controllers.add(c)

        # Assign an equal fraction on each edge to each closest path.
        for c in closest_controllers:
            path = apsp_paths[n][c]
            if path_is_clear(path, failed_links):
                connected += 1.0 / float(len(closest_controllers))

    connectivity = connected / float(g.number_of_nodes())
    return connectivity


def link_failure_combinations(g, failures):
    '''Returns combinations with the specified number of link failures.
    
    @param g: NetworkX graph
    @param failures: exact number of failures
    @return combos: combinations of links (src/dst pairs)
    '''
    if failures == 0:
        return [()]
    combos = []
    for c in combinations(g.edges(), failures):
        combos.append(c)
    return combos

def availability_one_combo(g, combo, apsp, apsp_paths, weighted,
                           link_fail_prob, max_failures):
    '''Compute connectivity for a single combination of controllers.

    @param g: NetworkX graph
    @param controllers: list of controller locations
    @param apsp: all-pairs shortest paths data
    @param apsp_paths: all-pairs shortest paths path data
    @param weighted: is graph weighted?
    @param link_fail_prob: meaning depends on weighted.
        if weighted == True:
            probability per unit weight that a given link will fail
        if weighted == False:
            probability that a given link will fail
    @param max_failures: max # simultaneous failures to simulate
    @return availability: average availability fraction
    @return coverage: fraction of cases considered.
    '''
    availabilities = {}  # Probabilities * connectivity per # failures
    coverages = {}  # Coverage per # failures
    assert g

    for failures in range(max_failures + 1):
        availabilities[failures] = 0.0
        coverages[failures] = 0.0
        for failed_links in link_failure_combinations(g, failures):
            links = g.number_of_edges()
            if weighted:
                state_prob = 1.0
                for e in g.edges():
                    src, dst = e
                    weight = g[src][dst]['weight']
                    this_link_fail_prob = link_fail_prob * weight
                    if e in failed_links:
                        state_prob *= this_link_fail_prob
                    else:
                        state_prob *= (1.0 - this_link_fail_prob)
            else:
                bad_links = len(failed_links)
                good_links = links - bad_links
                link_success_prob = (1.0 - link_fail_prob)
                state_prob = ((link_success_prob ** good_links) *
                              (link_fail_prob ** bad_links))
            coverages[failures] += state_prob
            conn = connectivity_sssp(g, combo, apsp, apsp_paths, weighted, failed_links)
            availabilities[failures] += state_prob * conn

    availability = sum(availabilities.values())
    coverage = sum(coverages.values())
    return availability, coverage


def get_null(g, combo, apsp, apsp_paths, weighted, extra_params):
    return 0.0

def get_latency(g, combo, apsp, apsp_paths, weighted, extra_params):
    return get_total_path_len(g, combo, apsp, weighted) / float(g.number_of_nodes())

def get_wc_latency(g, combo, apsp, apsp_paths, weighted, extra_params):
    return worst_case_latency(g, combo, apsp, weighted)

def get_fairness(g, combo, apsp, apsp_paths, weighted, extra_params):
    return controller_split_fairness(g, combo, apsp, weighted)

def get_availability(g, combo, apsp, apsp_paths, weighted, extra_params):
    assert 'link_fail_prob' in extra_params
    assert 'max_failures' in extra_params
    availability, coverage = availability_one_combo(g, combo, apsp, apsp_paths,
        weighted, extra_params['link_fail_prob'], extra_params['max_failures'])
    return availability

# Map of metric names to functions to execute them.
# Functions must have these parameters:
# (g, combo, apsp, apsp_paths, weighted, extra_params)
METRIC_FCNS = {
    'null': get_null,
    'latency': get_latency,
    'wc_latency': get_wc_latency,
    'fairness': get_fairness,
    'congestion': control_traffic_congestion,
    'availability': get_availability
}

METRICS = METRIC_FCNS.keys()

def handle_combo(combo):
    '''Handle processing for a combination.
    
    Returns list with two elements:
        combo: list
        values: dict of metric, (value, duration) tuples.
    '''
    values = {}
    for metric in g_metrics:
        start_time = time.time()
        metric_value = METRIC_FCNS[metric](g_g, combo, g_apsp, g_apsp_paths,
                                           g_weighted, g_extra_params)
        duration = time.time() - start_time
        values[metric] = (metric_value, duration)
    return [combo, values]


def run_all_combos(metrics, g, controllers, data, apsp, apsp_paths,
                   weighted = False, write_dist = False, write_combos = False,
                   extra_params = None, processes = None, multiprocess = False,
                   chunksize = 1, median = False):
    '''Compute best, worst, and mean/median latencies, plus fairness.

    @param metrics: metrics to compute: in ['latency', 'fairness']
    @param g: NetworkX graph
    @param controllers: list of numbers of controllers to analyze.
    @param data: JSON data to be augmented.
    @param apsp: all-pairs shortest paths data
    @param apsp_paths: all-pairs shortest paths path data
    @param weighted: is graph weighted?
    @param write_dist: write all values to the distribution.
    @param write_combos: write combinations to JSON?
    @param extra_params: extra params to pass in; hook for custom params, e.g
        availability is parameterized by failure probabilities.
    @param processes: number of workers in pool
    @param multiprocess: use multiple processes?
    @param chunksize: chunksize for multiprocess map
    '''
    
    # Ugly hack to effectively write our reused objects to shared memory
    global g_metrics
    global g_g
    global g_apsp
    global g_apsp_paths
    global g_weighted
    global g_extra_params
    
    g_metrics = metrics
    g_g = g
    g_apsp = apsp
    g_apsp_paths = apsp_paths
    g_weighted = weighted
    g_extra_params = extra_params

    if multiprocess:
        pool = multiprocessing.Pool(processes)

    point_id = 0  # Unique index for every distribution point written out.
    data['data'] = {}  # Where all data point & aggregates are stored.
    for combo_size in sorted(controllers):
        # compute best location(s) for i controllers.

        print "** combo size: %s" % combo_size

        # Initialize metric tracking data
        metric_data = {}
        for metric in metrics:
            metric_data[metric] = {}
            this_metric = metric_data[metric]
            this_metric['highest'] = -BIG
            this_metric['highest_combo'] = None
            this_metric['lowest'] = BIG
            this_metric['lowest_combo'] = None
            this_metric['duration'] = 0.0
            this_metric['sum'] = 0.0
            this_metric['num'] = 0
            if median:
                this_metric['values'] = []

        distribution = [] # list of {combo, key:value}'s in JSON, per combo

        if multiprocess:
            results = pool.map(handle_combo, combinations(g.nodes(), combo_size),
                               chunksize)
        else:
            results = map(handle_combo, combinations(g.nodes(), combo_size))

        def process_result(combo, values, point_id, distribution, metric_data):
            json_entry = {}  # For writing to distribution
            json_entry['id'] = point_id
            point_id += 1
            for metric in metrics:
                this_metric = metric_data[metric]
                metric_value, duration = values[metric]
                this_metric['duration'] += duration
                if metric_value < this_metric['lowest']:
                    this_metric['lowest'] = metric_value
                    this_metric['lowest_combo'] = combo
                if metric_value > this_metric['highest']:
                    this_metric['highest'] = metric_value
                    this_metric['highest_combo'] = combo
                if median:
                    this_metric['values'].append(metric_value)
                this_metric['sum'] += metric_value
                this_metric['num'] += 1

                json_entry[metric] = metric_value

                if write_combos:
                    json_entry['combo'] = combo

                if write_dist:
                    distribution.append(json_entry)

            return point_id

        for combo, values in results:
            point_id = process_result(combo, values, point_id, distribution, metric_data)

        # Compute summary stats
        for metric in metrics:                    
            this_metric = metric_data[metric]
            # Previously, we stored all values - but with so many,
            # the storage of these values must go to disk swap and the CPU
            # usage drops to 1% waiting on disk.
            #this_metric['mean'] = sum(this_metric['values']) / len(this_metric['values'])
            this_metric['mean'] = this_metric['sum'] / float(this_metric['num'])
            if median:
                this_metric['median'] = numpy.median(this_metric['values'])
                del this_metric['values']
            # Work around Python annoyance where str(set) doesn't work
            this_metric['lowest_combo'] = list(this_metric['lowest_combo'])
            this_metric['highest_combo'] = list(this_metric['highest_combo'])

            PRINT_VALUES = True
            if PRINT_VALUES:
                print "\t" + "%s" % metric
                for key in sorted(this_metric.keys()):
                    if key != 'values':
                        print "\t\t%s: %s" % (key, this_metric[key])

        data['data'][unicode(combo_size)] = {}
        group_data = data['data'][unicode(combo_size)]
        for metric in metrics:
            group_data[metric] = metric_data[metric]
        group_data['distribution'] = distribution

    data['metric'] = metrics
    data['group'] = controllers


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
