#!/usr/bin/python

from argparse import ArgumentParser
from math import ceil


def parse_args(message=None):
    '''Initialization of global variables'''
    parser = ArgumentParser(description=message)
    parser.add_argument('-a', '--auth', metavar='Token', type=str, required=True,
                        help='Rundeck token')
    parser.add_argument('-t', '--host', metavar='Domain', type=str, default="localhost",
                        help='Rundeck host or domain (default: localhost)')
    parser.add_argument('-p', '--port', metavar='Port', type=int, default=4440,
                        help='Rundeck port (default: 4440)')
    parser.add_argument('-m', '--execution-mode', metavar='Mode', type=str, default='cleanup',
                        help='Select operation to run this project (default: cleanup)')
    parser.add_argument('--db-host', metavar='Host', type=str, default="mysql-host",
                        help='Rundeck database host (default: mysql-host)')
    parser.add_argument('--db-port', metavar='Port', type=str, default=3306,
                        help='Rundeck database port (default: 3306)')
    parser.add_argument('--db-name', metavar='Database', type=str, default="rundeck",
                        help='Rundeck database name (default: rundeck)')
    parser.add_argument('--db-user', metavar='User', type=str, default="rundeck",
                        help='Rundeck database user (default: rundeck)')
    parser.add_argument('--db-pass', metavar='Password', type=str,
                        help='Rundeck database password')
    parser.add_argument('--filtered-project', metavar='Project', type=str, default=None,
                        help='Filter by a given project')
    parser.add_argument('--api-version', metavar='Version', type=int, default=19,
                        help='Rundeck API version (default: 19)')
    parser.add_argument('--search-timeout', metavar='Seconds', type=int, default=60,
                        help='Timeout to expire HTTP GET requests (default: 60)')
    parser.add_argument('--delete-timeout', metavar='Seconds', type=int, default=300,
                        help='Timeout to expire HTTP POST requests (default: 300)')
    parser.add_argument('--keep-time', metavar='Time', type=str, default="30d",
                        help='Period of time to keep executions records (default: 30d)')
    parser.add_argument('--chunk-size', type=int, metavar='Size', default=200,
                        help='Size of each delete iteration (default: 200)')
    parser.add_argument('--retries', type=int, metavar='Number', default=5,
                        help='Number of retries when some error occur (default: 5)')
    parser.add_argument('--retry-delay', type=int, metavar='Seconds', default=5,
                        help='Delay to start next retry (default: 5)')
    parser.add_argument('--ssl-enabled', action='store_true', default=False,
                        help='Rundeck is served over SSL (default: false)')
    parser.add_argument('--executions-by-project', action='store_true', default=True,
                        help='Filter executions by project (default: true)')
    parser.add_argument('--debug', default=False, action='store_true',
                        help='Print all operations (default: false)')
    args = parser.parse_args()

    return args


def get_num_pages(n_executions, divider=200):
    '''...'''

    return int(ceil(n_executions / float(divider)))


def validate_configs(configs):
    '''Validate each parameter of the configurations'''

    if not (configs.port >= 1024 and configs.port <= 65535):
        return False, "Invalid port number."

    if configs.api_version not in range(1, 21):
        return False, "Invalid API version."

    if configs.search_timeout <= 0:
        return False, "Invalid searching timeout value."

    if configs.delete_timeout <= 0:
        return False, "Invalid deleting timeout value."

    if configs.chunk_size <= 0:
        return False, "Invalid chunk size value."

    number = configs.keep_time[:-1]
    unit = configs.keep_time[-1:]

    if not number.isdigit() or unit not in ['h', 'd', 'w', 'm', 'y']:
        return False, "Invalid time to keep old records."

    return True, ""


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
