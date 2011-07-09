#!/bin/sh
TOPO=Abilene
C=3
EXT=pdf
./generate.py --topo ${TOPO} --from_start ${C} --lat_metrics -w --write_dist --write_combos -w -e ${EXT}
