#!/bin/sh
# Generate metrics and plots for a controller range
TOPO=$1
C=$2
METRICS=$3
EXT=$4
./metrics.py --topo ${TOPO} --from_start ${C} --lat_metrics -w --write_dist --write_combos
./plot_cdfs.py -i data_out/${TOPO}/${C}_to_0.json -w --metric_list="${METRICS}" -e ${EXT}
./plot_ranges.py -i data_out/${TOPO}/${C}_to_0.json -w --metric_list="${METRICS}" -e ${EXT}
# generate PNGs for cloud - way too many points otherwise
./plot_cloud.py -i data_out/${TOPO}/${C}_to_0.json -w --metric_list="${METRICS}" -e png
./plot_pareto.py -i data_out/${TOPO}/${C}_to_0.json -w --metric_list="${METRICS}" -e ${EXT}
./map_combos.py -i data_out/${TOPO}/${C}_to_0.json -w -e ${EXT}

