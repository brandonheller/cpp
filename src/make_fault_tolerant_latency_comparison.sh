#!/bin/sh
# Generate all OS3E graphs, to understand the costs of optimizing for the
# nth-closest controller.

C=5
EXT=pdf
# Add FORCE to forcibly regenerate metrics.
# Only needed when the data schema or set of input topos changes.
FORCE='-f'
# Define metrics
METRICS='--metric_list latency,wc_latency,latency_2,wc_latency_2'
# Define operations
OPERATIONS='--operation_list metrics'


# Generate all latency metrics data for OS3E topology
TOPO=os3e
#./generate.py --topo ${TOPO} --from_start ${C} ${METRICS} -w --write_dist --write_combos -w -e ${EXT} ${FORCE} ${OPERATIONS}

PLOT_LIST='--plot_list ft_cost'
for metric in latency wc_latency latency_2 wc_latency_2
do
	./plot_ranges.py -i data_out/${TOPO}/${C}_to_0.json --from_start ${C} -w --metric_list ${metric} -e ${EXT} ${PLOT_LIST}
done
exit

for metrics in 'latency,latency_2' 'wc_latency,wc_latency_2'
do
	./plot_cdfs.py -i data_out/${TOPO}/${C}_to_0.json --from_start ${C} -w --metric_list ${metrics} -e ${EXT}
done

for metrics in 'latency,latency_2' 'wc_latency,wc_latency_2' 'latency,wc_latency' 'latency_2,wc_latency_2'
do
	echo "Generating for metrics: ${metrics}"
	./plot_pareto.py -i data_out/${TOPO}/${C}_to_0.json --from_start ${C} -w --metric_list ${metrics} -e ${EXT}
	./plot_cloud.py -i data_out/${TOPO}/${C}_to_0.json --from_start ${C} -w --metric_list ${metrics} -e png
	./map_combos.py -i data_out/${TOPO}/${C}_to_0.json --from_start ${C} -w --metric_list ${metrics} --write_dist --write_combos -e ${EXT}	
done

## Generate mini topology images for OS3 topology

## Generate tradeoffs output
## Only go up to 4, because going to 5 requires > 1 GB of RAM.
#C=4
#PLOT_LIST='--plot_list pareto_max,pareto_max_bw'
#CDF_PLOT_LIST='--cdf_plot_list pareto'
#./generate_merged.py --all_topos --from_start ${C} ${METRICS} -w -e ${EXT} ${FORCE} ${MP} ${OPS} ${PLOT_LIST} ${CDF_PLOT_LIST}
