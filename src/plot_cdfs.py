#!/usr/bin/env python
'''Plot CDFs of latency, where each series is a # of controllers.'''
import math

import lib.plot as plot
from lib.colors import COLORS


def do_cdfs():
    options = plot.parse_args()
    print "loading JSON data..."
    stats = plot.load_stats(options)

    for metric in options.metrics:
        print "reformatting data..."
        data = {}
        for i, g in enumerate(stats['group']):
            if options.max and i >= options.max:
                break
            data[g] = [d[metric] for d in stats['data'][g]["distribution"]]
    
        print "plotting CDFs"
        write_filepath = options.input + '_' + metric
        write_filepath = write_filepath.replace('data_out', 'data_vis')
        write_filepath = write_filepath.replace('.json', '')
        xmax = round(math.ceil(max(data[stats['group'][0]])))
        axis_limits = [0, xmax, 0, 1]
        if options.minx:
            axis_limits[0] = options.minx
        if options.maxx:
            axis_limits[1] = options.maxx
        plot.plot('cdf', data, COLORS, axis_limits,
                  metric, "linear", "linear", write_filepath + '_cdfs',
                  options.write,
                  xlabel = metric + '(miles)', ylabel = 'fraction',
                  ext = options.ext)

    if not options.write:
        plot.show()

if __name__ == "__main__":
    do_cdfs()