#!/usr/bin/env python
from operator import itemgetter

def sort_by_val(input_dict, reverse = True):
    # Returns list of key, val pairs sorted by val
    tuples = [(key, val) for key, val in input_dict.iteritems()]
    return sorted(tuples, key = itemgetter(1), reverse = reverse)