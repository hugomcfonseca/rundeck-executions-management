#!/usr/bin/python

import argparse
import math
import json

def parse_args(message=None):
    '''Initialization of global variables'''

    parser = argparse.ArgumentParser(
        description='Listing running jobs and delete old logs from your Rundeck server.')
    parser.add_argument('-c', '--config-file', metavar='File', type=str, required=True,
                        help='JSON file with configurations')
    parser.add_argument('-m', '--mode', metavar='Mode', type=str, default='cleanup',
                        help='')
    parser.add_argument('--debug', default=False, action='store_true',
                        help='Used to print executed operations')
    args = parser.parse_args()

    if args.config_file != None:
        with open(args.config_file, 'r') as properties:
            return json.load(properties)


def get_num_pages(n_executions, divider=200):
    '''...'''
    
    return int(math.ceil(total / float(200)))

