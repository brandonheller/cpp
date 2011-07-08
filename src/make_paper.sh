#!/bin/sh
# Generate all OS3E graphs:

C=3
METRICS="latency,wc_latency"
EXT=pdf

# Generate all for OS3E topology
TOPO=os3e
./generate_one.sh $TOPO $C $METRICS $EXT

# Generate special big ones for OS3E
# BIG job (on Rhone)
#time ./metrics.py --from_start 12 --from_end 12 --lat_metrics --weighted -w --processes 8
./plot_ranges.py -i data_out/os3e/12_to_12.json -w --metric_list="latency,wc_latency" --maxx 12 --maxy 1  -e ${EXT}
