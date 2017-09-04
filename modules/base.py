#!/usr/bin/python

import argparse
import math
import json


def parse_args(message=None):
    '''Initialization of global variables'''

    parser = argparse.ArgumentParser(description=message)
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

    return int(math.ceil(n_executions / float(divider)))


def validate_keeping_time(keep_time):
    '''Check if keep_time has the required nomenclature: number of days followed by the time unit'''

    number = keep_time[:-1]
    unit = keep_time[-1:]

    if number.isdigit() and unit in ['h', 'd', 'w', 'm', 'y']:
        return True

    return False

def parse_json_response(http_response, filter_by=None, append_by=None):
    '''...'''
    data_info = []

    if http_response.ok:
        json_response = http_response.json()
    
        if filter_by: 
            response_filtered = json_response[filter_by]
        else:
            response_filtered = json_response

        if isinstance(response_filtered, list):
            for data in response_filtered:
                if append_by is not None:
                    data_info.append(data[append_by])
                else:
                    data_info.append(data)
        else:
            data_info = response_filtered

        return True, data_info 

    return False, http_response.status_code


def sigint_handler(signum, frame):
    '''...'''
    try:
        if raw_input("\nReally quit? (y/n)> ").lower().startswith('y'):
            exit(1)
    except KeyboardInterrupt:
        print("Quitting...")
        exit(1)
