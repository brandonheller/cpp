#!/usr/bin/env python
'''Generate everything for one or more topos.'''
import lib.plot as plot
import metrics
import plot_cdfs
import plot_ranges
import plot_cloud
import plot_pareto
#import map_combos
from zoo_tools import zoo_topos
from topo_lib import get_topo_graph, has_weights


if __name__ == "__main__":

    global options
    options = plot.parse_args()

    def do_all(name, g, i, t, data):
        global options
        assert options
        stats, filename = metrics.do_metrics(options, name, g)
        filename = filename.replace('data_out', 'data_vis')
        plot_cdfs.do_cdfs(options, stats, filename)
        plot_ranges.do_ranges(options, stats, filename)
        plot_pareto.do_pareto(options, stats, filename)
        plot_cloud.do_cloud(options, stats, filename, 'png')
        #map_combos.do_plot(options, stats, g, filename)

    if options.all_topos:
        topos = sorted(zoo_topos())
    else:
        topos = options.topos

    t = len(topos)
    for i, topo in enumerate(topos):
        if not options.max == None and i >= options.max:
            break
        print "topo %s of %s: %s" % (i, t, topo)
        g = get_topo_graph(topo)
        if not g:
            raise Exception("WTF?  null graph: %s" % topo)
        if has_weights(g):
            do_all(topo, g, 1, 1, None)
        else:
            print "no weights for %s, skipping" % topo
