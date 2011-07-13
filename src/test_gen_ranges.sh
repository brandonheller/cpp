#!/bin/sh
# Simple test case to validate that ranges generation is working.
EXT=pdf
CS='4'
MP='--no-multiprocess'
OPS='--operation_list ranges'
TOPOS='--topo Aarnet'
FORCE='--force'

for C in ${CS}
do
  ./generate.py ${TOPOS} --from_start ${C} --lat_metrics -w -e ${EXT} ${FORCE} ${MP} ${OPS}
done