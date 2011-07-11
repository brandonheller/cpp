#!/bin/sh
TOPO=Bandcon
C=3
EXT=pdf
#BLACKLIST='Bandcon'
./generate.py --topo ${TOPO} --from_start ${C} --lat_metrics -w --write_dist --write_combos -w -e ${EXT} --no-multiprocess
#--topo_blacklist ${BLACKLIST}
