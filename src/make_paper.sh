#!/bin/sh
# Generate all OS3E graphs:

C=5
EXT=pdf

# Generate all for OS3E topology
TOPO=os3e
./generate.py --topo ${TOPO} --from_start ${C} --lat_metrics -w --write_dist --write_combos -w -e ${EXT} -f
./map_combos.py -i data_out/${TOPO}/${C}_to_0.json --from_start ${C} --lat_metrics -w --write_dist --write_combos -w -e ${EXT}

# Generate special big ones for OS3E
# BIG job (on Rhone)
#time ./metrics.py --from_start 12 --from_end 12 --lat_metrics --weighted -w
./plot_ranges.py -i data_out/os3e/12_to_12.json -w --lat_metrics --maxx 12 --maxy 1  -e ${EXT}
