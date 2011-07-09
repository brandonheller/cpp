#!/bin/sh
# Generate everything for all topologies that we can geocode.
TOPO=os3e
C=3
EXT=pdf
P=8
MAX=5  # add --max $MAX at the end of generate.py to debug only a few topos. 
CS='3 4'
for C in ${CS}
do
  echo "writing all for num controllers ${C}"
  ./generate.py --all_topos --from_start ${C} --lat_metrics -w --write_dist --write_combos -w -e ${EXT} --max ${MAX} --processes 8
done