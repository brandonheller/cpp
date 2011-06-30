#!/usr/bin/env python
'''Libraries to simplify data output.'''

import json
import string

def tab_sep(data):
    return string.join(data, '\t')

def flatten(data, exclude_list = [], connector = '_'):
    '''Given JSON data, flatten field and subfield names with connect
    
    @param data: JSON data with up to two levels.
    @param exclude_list: list of fields/subfields to exclude.
    @return flattened: flattened data, newline-separated
    '''
    flattened = {}
    for field in data.keys():
        if field not in exclude_list:
            #print data[field]
            for subfield in data[field].keys():
                if subfield not in exclude_list:
                    #print data, field, subfield
                    data_val = data[field][subfield]
                    flattened[field + connector + subfield] = data_val
    return flattened

def write_json_file(filename, data):
    '''Given JSON data, write to file.'''
    json_file = open(filename, 'w')
    json.dump(data, json_file, indent = 4)
    print "wrote %s" % filename

def read_json_file(filename):
    input_file = open(filename, 'r')
    return json.load(input_file)

def write_csv_file(filename, data, exclude):
    '''Given JSON data, convert to CSV and write to file.'''
    csv_file = open(filename + ".csv", 'w')
    # We assume that the lowest-indexed key has a full set of data.
    field_names = flatten(data[sorted(data.keys())[0]], exclude).keys()
    #print field_names
    csv_file.write(tab_sep(["i"] + field_names) + '\n')
    for i in sorted(data.keys()):
        flattened_data = flatten(data[i], exclude)
        row_data = [flattened_data.get(field, 0) for field in field_names]
        csv_file.write(tab_sep(["%s" % val for val in ([i] + row_data)]) + '\n')

    print "wrote %s" % filename + '.csv'


def write_dist_csv_file(filename, data, exclude):
    '''Given JSON data, convert to CSV and write distribution data to file.'''
    csv_file = open(filename + ".csv", 'w')
    # We assume that the lowest-indexed key has a full set of data.
    fields = data[sorted(data.keys())[0]]['distribution'][0].keys()
    fields = [f for f in fields if f not in exclude]
    csv_file.write(tab_sep(["i"] + fields) + '\n')
    for i in sorted(data.keys()):
        data_points = data[i]['distribution']
        for point in data_points:
            row_data = []
            for field in fields:
                if 'combo' not in field:
                    row_data.append("%s" % point.get(field, 0))
                else:
                    # Python doesn't like writing out tuples as strings,
                    # so use string instead.  Otherwise we get TypeErrors.
                    row_data.append(str(point.get(field, 0)))
            row_data.insert(0, "%s" % i)
            csv_file.write(tab_sep(row_data) + '\n')

    print "wrote %s" % filename + '.csv'