#!/bin/sh
# Generate all OS3E graphs:

C=5
EXT=pdf
# Add FORCE to forcibly regenerate metrics.
# Only needed when the data schema or set of input topos changes.
#FORCE='-f'

# Generate all latency metrics data for OS3E topology
TOPO=os3e
./generate.py --topo ${TOPO} --from_start ${C} --lat_metrics -w --write_dist --write_combos -w -e ${EXT} ${FORCE}
./plot_cdfs.py -i data_out/${TOPO}/${C}_to_0.json --from_start ${C} -w --lat_metrics -e ${EXT}

# For now, change TICK_LABELSIZE to 18 in plot.py before generating these two.
./plot_pareto.py -i data_out/${TOPO}/${C}_to_0.json --from_start ${C} -w --lat_metrics -e ${EXT}
./plot_cloud.py -i data_out/${TOPO}/${C}_to_0.json --from_start ${C} -w --lat_metrics -e png

# Generate mini topology images for OS3 topology
./map_combos.py -i data_out/${TOPO}/${C}_to_0.json --from_start ${C} --lat_metrics -w --write_dist --write_combos -e ${EXT}

# Generate special big ones for OS3E
# BIG job (on Rhone)
#time ./metrics.py --from_start 12 --from_end 12 --lat_metrics --weighted -w
./plot_ranges.py -i data_out/os3e/12_to_12.json -w --lat_metrics --maxx 12 --maxy 1  -e ${EXT}

# Requires all output from Rhone for up to k = 4.  To get such output,
# from the cc/src dir:
#   rsync_rhone.sh
# Don't use multiprocessing; MPL backend is not thread-safe at the moment.
MP='--no-multiprocess'
# Doesn't actually do anything in generate_merged, but prevents metrics from getting built.
OPS='--operation_list pareto, ranges'

# Generate all ranges plots
PLOT_LIST='--plot_list ranges_lowest,ratios_all,ratios_mean,bc_rel'
CDF_PLOT_LIST='--cdf_plot_list latency'
# For now, only go up to 8.
C=8
TABLE='--gen_1ctrl_table'
./generate_merged.py --all_topos --from_start ${C} --lat_metrics -w -e ${EXT} ${FORCE} ${MP} ${OPS} ${PLOT_LIST} ${CDF_PLOT_LIST} ${TABLE}

# Generate tradeoffs output
# Only go up to 4, because going to 5 requires > 1 GB of RAM.
C=4
PLOT_LIST='--plot_list pareto_max,pareto_max_bw'
CDF_PLOT_LIST='--cdf_plot_list pareto'
./generate_merged.py --all_topos --from_start ${C} --lat_metrics -w -e ${EXT} ${FORCE} ${MP} ${OPS} ${PLOT_LIST} ${CDF_PLOT_LIST}
