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
    json_file = open(filename + ".json", 'w')
    json.dump(data, json_file)

def read_json_file(filename):
    input_file = open(filename, 'r')
    return json.load(input_file)

def write_csv_file(filename, data, exclude):
    '''Given JSON data, convert to CSV and write to file.'''
    csv_file = open(filename + ".csv", 'w')
    field_names = flatten(data[data.keys()[0]], exclude).keys()
    #print field_names
    csv_file.write(tab_sep(["i"] + field_names) + '\n')
    for i in sorted(data.keys()):
        flattened_data = flatten(data[i], exclude)
        row_data = [flattened_data.get(field, 0) for field in field_names]
        csv_file.write(tab_sep(["%s" % val for val in ([i] + row_data)]) + '\n')
