#!/bin/sh
# Simple test case to validate that ranges generation is working.
EXT=pdf
C='--from_start 4'
MP='--no-multiprocess'
OPS='--operation_list ranges'
FORCE='--force'
METRICS='--lat_metrics'

# Should generate an identical plot to generate.py w/operations_list='ranges'
# data_vis/merged/4_to_0_latency_ranges.pdf
# data_vis/Aarnet/4_to_0_latency_ranges.pdf
GROUP='--topo_group test1'
./generate_merged.py ${GROUP} ${C} ${METRICS} -w -e ${EXT} ${FORCE} ${MP} ${OPS}

# Should generate combination of two:
# data_vis/merged/4_to_0_latency_ranges.pdf
# data_vis/Aarnet/4_to_0_latency_ranges.pdf
# data_vis/Abilene/4_to_0_latency_ranges.pdf
GROUP='--topo_group test2'
./generate_merged.py ${GROUP} ${C} ${METRICS} -w -e ${EXT} ${FORCE} ${MP} ${OPS}

TOPOS='--all_topos'
#./generate_merged.py ${TOPOS} ${C} ${METRICS} -w -e ${EXT} ${FORCE} ${MP} ${OPS}
