#!/usr/bin/env python
'''
Library functions for working w/lists.
'''
import itertools
import logging


def compare_lists(one, two):
    '''Compare two ordered lists.  One must be a permutation of the other.

    @param one: list
    @param two: list
    @return sum: value representing avg absolute distance between pairs
    '''
    # two_dict[element] = pos in array two
    two_dict = {}
    for i, e in enumerate(two):
        two_dict[e] = i
    sum = 0
    for i, e in enumerate(one):
        sum += abs(i - two_dict[e])
    return sum


def permutations_len_total_diff(size):
    '''Given list length, add up list distances for all permutations.'''
    return permutations_total_diff([a for a in range(size)])


def permutations_total_diff(a):
    '''Given a list, add up list distances for all permutations.'''
    sum = 0
    for p in itertools.permutations(a):
        d = compare_lists(a, p)
        logging.debug("distance between %s and %s is %s" % (a, p, d))
        sum += d
    return sum