#!/bin/sh
# Generate all OS3E graphs:
C=5
METRICS="latency,wc_latency"
EXT=pdf
#./metrics.py --from_start ${C} --lat_metrics -w --write_dist --write_combos
./plot_cdfs.py -i data_out/os3e_weighted_${C}_to_0.json -w --metric_list="${METRICS}" -e ${EXT}
./plot_ranges.py -i data_out/os3e_weighted_${C}_to_0.json -w --metric_list="${METRICS}" -e ${EXT}
# generate PNGs for cloud - way too many points otherwise
./plot_cloud.py -i data_out/os3e_weighted_${C}_to_0.json -w --metric_list="${METRICS}" -e png
./map_combos.py -i data_out/os3e_weighted_${C}_to_0.json -w -e ${EXT}

# BIG job (on Rhone)
#time ./metrics.py --from_start 12 --from_end 12 --lat_metrics --weighted -w --processes 8
./plot_ranges.py -i data_out/os3e_weighted_12_to_12.json -w --metric_list="latency,wc_latency" --maxx 12 --maxy 1  -e ${EXT}
