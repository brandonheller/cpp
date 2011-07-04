#!/bin/sh
# Generate all OS3E graphs:
C=5
METRICS="latency,wc_latency"
./metrics.py --from_start ${C} --lat_metrics -w --write_dist --write_combos
./plot_cdfs.py -i data_out/os3e_weighted_${C}_to_0.json -w --metric_list="${METRICS}"
./plot_ranges.py -i data_out/os3e_weighted_${C}_to_0.json -w --metric_list="${METRICS}"
./map_combos.py -i data_out/os3e_weighted_${C}_to_0.json -w