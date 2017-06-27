#!/usr/bin/python

import argparse
import math
import json

def parse_args(message=None):
    '''...'''

    parser = argparse.ArgumentParser(description=message)

    parser.add_argument('-c', '--config-file', metavar='File', type=str, default=None,
                        help='JSON file with configurations')
    parser.add_argument('--host', metavar='Host', type=str, default='localhost',
                        help='IP address or domain of Rundeck')
    parser.add_argument('--port', metavar='Port', type=int, default=4440,
                        help='Port of Rundeck')
    parser.add_argument('--auth', metavar='Token', type=str,
                        help='API token with correct permissions')
    parser.add_argument('--api-version', metavar='Version', type=int, default=19,
                        help='API version of Rundeck')
    parser.add_argument('--search-time', metavar='Seconds', type=int, default=60,
                        help='Time to expire search queries')
    parser.add_argument('--delete-time', metavar='Seconds', type=int, default=1200,
                        help='Time to expire delete queries')
    parser.add_argument('--keeping-days', metavar='Days', type=int, default=21,
                        help='Number of days to keep logs')
    parser.add_argument('--delete-size', metavar='N', type=int, default=1000,
                        help='Number of executions to delete by cycle')
    parser.add_argument('--over-ssl', default=False, action='store_true',
                        help='Used when Rundeck is server over HTTPS')
    parser.add_argument('--debug', default=False, action='store_true',
                        help='Used to print executed operations')
    parser.add_argument('--execs-by-project', default=False, action='store_true',
                        help='Either delete defined range of executions by jobs or projects')

    args = parser.parse_args()

    if args.config_file != None:
        with open(args.config_file, 'r') as props_file:
            return json.load(props_file)
    else:
        configs = {
            'hostname': args.host,
            'port': args.port,
            'token': args.auth,
            'api_version': args.api_version,
            'search_time': args.search_time,
            'delete_time': args.delete_time,
            'keeping_days': args.keeping_days,
            'delete_size': args.delete_size,
            'over_ssl': args.over_ssl,
            'debug': args.debug,
            'execs_by_project': args.execs_by_project
        }

    return configs


def get_num_pages(n_executions, divider=200):
    '''...'''
    n_pages = int(math.floor(n_executions / divider))

    if n_executions % divider > 0:
        n_pages += 1

    return n_pages

