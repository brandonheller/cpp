#!/bin/sh
# Generate everything for all topologies that we can geocode.
# To run: time ./generate_all.sh > generate_all_log &
# To view: tail -n20 -f generate_all_log
TOPO=os3e
EXT=pdf
#MAX=5  # add --max $MAX at the end of generate.py to debug only a few topos. 
#MAX='--max 2'
CS='4'
FORCE='-f'
MP='--no-multiprocess'
MP='--processes 4'
OPS='--operation_list metrics'
# Everything except metrics:
#OPS='--operation_list cdfs,ranges,pareto,cloud'
TOPOS='--all_topos'
#TOPOS='--topo Iris'

for C in ${CS}
do
  echo "writing all for num controllers ${C}"
  echo "*********************"
  ./generate.py ${TOPOS} --from_start ${C} --lat_metrics -w --write_dist --write_combos -w -e ${EXT} ${FORCE} ${MP} ${OPS} ${MAX}
done