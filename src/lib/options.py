#!/usr/bin/env python
from optparse import OptionParser

import metrics_lib as metrics

# Highest number of controllers to plot.  If none, plot all.
DEF_MAX = None

# Weighted or not?
DEF_WEIGHTED = True

# Metric to plot
METRICS = metrics.METRICS
DEF_METRIC = metrics.METRICS[0]

DEF_INPUT_DIR = 'data_out'
DEF_OUTPUT_DIR = DEF_INPUT_DIR

OPERATIONS = ['metrics', 'cdfs', 'ranges', 'pareto', 'cloud']
DEF_OPERATIONS = OPERATIONS

DEF_EXT = 'png'

DEF_TOPO = 'os3e'

DPI = 300


def parse_args():
    opts = OptionParser()

    # Topology selection
    opts.add_option("--topo", type = 'str', default = DEF_TOPO,
                    help = "topology name")
    opts.add_option("--topo_list", type = 'str', default = None,
                    help = "list of comma-separated topology names")
    opts.add_option("--topo_blacklist", type = 'str', default = None,
                    help = "list of comma-separated topologies to ignore")
    opts.add_option("--all_topos",  action = "store_true",
                    default = False,
                    help = "compute metric(s) for all topos?")
    opts.add_option("--from_start", type = 'int', default = 3,
                    help = "number of controllers from start")
    opts.add_option("--from_end", type = 'int', default = 0,
                    help = "number of controllers from end")
    opts.add_option("--controller_list", type = 'str', default = None,
                    help = "list of comma-separated controller totals")

    # Operations
    opts.add_option("--operation_list", type = 'string',
                    default = None,
                    help = "operations to show, from %s" % OPERATIONS)

    # Metric selection
    opts.add_option("--metric",
                    default = 'latency',
                    choices = METRICS,
                    help = "metric to compute, one in %s" % METRICS)
    opts.add_option("--all_metrics",  action = "store_true",
                    default = False,
                    help = "compute all metrics?")
    opts.add_option("--lat_metrics",  action = "store_true",
                    default = False,
                    help = "compute all latency metrics?")
    opts.add_option("--metric_list", type = 'string',
                    default = None,
                    help = "metrics to show, from %s" % METRICS)

    # Shared output args
    opts.add_option("-w", "--write",  action = "store_true",
                    default = False,
                    help = "write plots, rather than display?")

    # Multiprocessing options
    opts.add_option("--no-multiprocess",  action = "store_false",
                    default = True, dest = 'multiprocess',
                    help = "don't use multiple processes?")
    opts.add_option("--processes", type = 'int', default = 8,
                    help = "worker pool size; must set multiprocess=True")
    opts.add_option("--chunksize", type = 'int', default = 50,
                    help = "batch size for parallel processing")

    # Metrics-specific arguments
    opts.add_option("--write_combos",  action = "store_true",
                    default = False,
                    help = "write out combinations?")
    opts.add_option("--write_dist",  action = "store_true",
                    default = False,
                    help = "write_distribution?")
    opts.add_option("--write_csv",  action = "store_true",
                    default = False,
                    help = "write csv file?")
    opts.add_option("--no-dist_only",  action = "store_false",
                    default = True, dest = 'dist_only',
                    help = "don't write out _only_ the full distribution (i.e.,"
                    "run all algorithms.)")
    opts.add_option("--use_prior",  action = "store_true",
                    default = False,
                    help =  "Pull in previously computed data, rather than recompute?")
    opts.add_option("--no-compute_start",  action = "store_false",
                    default = True, dest = 'compute_start',
                    help = "don't compute metrics from start?")
    opts.add_option("--no-compute_end",  action = "store_false",
                    default = True, dest = 'compute_end',
                    help = "don't compute metrics from end?")
    opts.add_option("--median",  action = "store_true",
                    default = False,
                    help = "compute median?")
    opts.add_option("-f", "--force", action = "store_true",
                    default = False,
                    help = "force operations to occur even if metrics are there")

    # Plotting-specific input args
    opts.add_option("-i", "--input", type = 'string', 
                    default = None,
                    help = "name of input file")
    opts.add_option("--input_dir", type = 'string',
                    default = DEF_INPUT_DIR,
                    help = "name of input dir")
    opts.add_option("-o", "--output_dir", type = 'string',
                    default = DEF_OUTPUT_DIR,
                    help = "name of output file")

    # Plotting-specific params
    opts.add_option("--max", type = 'int', default = DEF_MAX,
                    help = "highest number of controllers to plot %s" % METRICS)
    opts.add_option("--minx", type = 'float', default = None,
                    help = "min X axis value")
    opts.add_option("--maxx", type = 'float', default = None,
                    help = "min X axis value")
    opts.add_option("--miny", type = 'float', default = None,
                    help = "min Y axis value")
    opts.add_option("--maxy", type = 'float', default = None,
                    help = "min Y axis value")
    opts.add_option("-e", "--ext", type = 'string',
                    default = DEF_EXT,
                    help = "file extension")
    opts.add_option("-l", "--labels",  action = "store_true",
                    default = False,
                    help = "write labels to images (map_combo only)?")

    options, arguments = opts.parse_args()

    # Handle metrics
    if options.metric_list:
        metrics_split = options.metric_list.split(',')
        options.metrics = []
        for metric in metrics_split:
            if metric not in METRICS:
                raise Exception("Invalid metric(s): %s in %s; choose from %s" %
                                (metric, options.metric_list, METRICS))
            options.metrics.append(metric)

    if (options.metric != DEF_METRIC) and options.metric_list:
        raise Exception("Can't specify both --metric and --metric_list")

    if options.metric and not options.metric_list:
        options.metrics = [options.metric]

    if options.all_metrics:
        options.metrics = metrics.METRICS
    elif options.lat_metrics:
        options.metrics = ['latency', 'wc_latency']
    else:
        options.metrics = [options.metric]

    if options.operation_list:
        options.operations = options.operation_list.split(',')
    else:
        options.operations = DEF_OPERATIONS

    options.controllers = None
    if options.controller_list:
        options.controllers = []
        for i in options.controller_list.split(','):
            options.controllers.append(int(i))

    if options.topo != DEF_TOPO and options.topo_list:
        raise Exception("Both topo and topo_list provided; pick one please")
    else:
        if options.topo_list:
            options.topos = options.topo_list.split(',')
        else:
            options.topos = [options.topo]

    if options.topo_blacklist:
        options.topos_blacklist = options.topo_blacklist.split(',')
    else:
        options.topos_blacklist = None

    return options