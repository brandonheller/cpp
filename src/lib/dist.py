# Conversion factor for dual-y-scale graphs
# Assume speed of light in fiber is 2/3 that in other media
# (1m / 0.00062137 miles) * (1 sec / 2e8 m) * (1000 ms /sec)
# Comes to 0.0080467354394322243 ms / mile
MILES_TO_MS = (1/0.00062137) * (1/2e8) * 1000

# Half the two-way totals, to compare to one-way latencies.
LATENCY_LINES = [[5, 'switch processing'],
                 [25, 'ring protection'],
                 [100, 'mesh restoration']]