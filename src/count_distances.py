#!/usr/bin/env python
"""Explore the behavior of the random distance absolute list difference
function for a range of values.  Reaches a limit of 1/3. 

Much of the computation looks like magic, but it comes from manually
computing list difference totals for a bunch of smaller lists, then
looking at the gap between the answers.

TODO: replace permutations_len_total_diff with a more efficient
version that uses the technique here.
"""
import math

from cc import compare_lists, permutations_len_total_diff

MAX_LIST_SIZE = 9

x = [] # manually computed list distance total
y = [] # manually computed list distance per permutation
gaps = [] # manually computed function from looking at datat
check = []
brute_forced_values = {}
for i in range(2, MAX_LIST_SIZE):
    total = permutations_len_total_diff(i)
    x.append(float(total))
    perm = math.factorial(i)
    y.append(float(total) / perm)
    gap = (1.0 / 3) + ((i - 1) * (2.0 / 3))
    gaps.append(gap)
    check.append(gap * perm)
    brute_forced_values[i] = total
print x
print y
print gaps
#print brute_forced_values
#print check

def create_random_distances(highest):
    x = {}
    x[0] = 0
    x[1] = 0
    dist = {}
    for i in range(2, highest):
        # Increments for total dist / permutations form an arithmetic series
        inc = 1.0 / 3 + (i - 1) * (2.0 / 3)
        x[i] = inc + x[i - 1]
        dist[i] = int(x[i] * math.factorial(i))
    return dist

data = create_random_distances(MAX_LIST_SIZE)
# data (computed with the gap function) should match what we brute-force
# computed above.
print data
print brute_forced_values


for i, d in data.iteritems():
    # this is the average distance a node is from where they should be,
    # overall all permutations.
    print i, float(d) / math.factorial(i) / i / i

# interesting!  fraction by which a node is off goes to 1/3 over time
# just divide the above output by i again to get the fraction.