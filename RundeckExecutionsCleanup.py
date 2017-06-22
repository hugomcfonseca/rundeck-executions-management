#!/usr/bin/python

import argparse
import json
import time

import requests


def init_global_vars():
    '''Initialization of global variables'''

    parser = argparse.ArgumentParser(
        description='Delete old and/or obsolete executions on Rundeck')
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
        return json.load(args.config_file)
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


def check_token_permissions():
    '''Used to validate API token deleting permissions'''

    endpoint = ''

    return True


def get_all_projects():
    '''Get every project info and returns only their names'''

    endpoint = URL + 'projects'
    project_names = []

    try:
        response = requests.get(endpoint, headers=HEADERS,
                                verify=False, timeout=3600)
        projects = response.json()

        for project in projects:
            project_names.append(project)
    except requests.exceptions.RequestException as exception:
        if CONFIGS['debug']:
            print exception
        return False

    return project_names


def get_jobs_by_project(project_name):
    '''...'''

    endpoint = URL + 'project/' + project_name + '/jobs'
    jobs_ids = []

    try:
        response = requests.get(endpoint, headers=HEADERS,
                                verify=False, timeout=3600)
        jobs = response.json()

        for job in jobs:
            jobs_ids.append(job)
    except requests.exceptions.RequestException as exception:
        if CONFIGS['debug']:
            print exception
        return False

    return jobs_ids


def get_executions_by_job(job_id, page):
    '''...'''

    endpoint = URL + 'job/' + job_id + '/executions'
    params = {
        'max': CONFIGS['delete_size'],  # CHANGE ME
        'offset': page * CONFIGS['delete_size']  # CHANGE ME
    }

    # Filter running and scheduled execs

    return True


def get_executions_by_project(project_name, page):
    '''...'''

    endpoint = URL + 'project/' + project_name + '/executions'
    params = {
        'olderFilter': CONFIGS['keeping_days'] + 'd'
    }

    return True


def check_execution_date(execution_date):
    '''...'''

    today_seconds = time.time()

    return True


def delete_executions(executions_ids):
    '''Bulk deletions of Rundeck executions'''

    endpoint = URL + 'executions/delete'
    data = json.dumps(executions_ids)

    try:
        request = requests.post(
            endpoint, headers=HEADERS, data=data, verify=False, timeout=3600)
        response = request.json()

        if response['allsuccessful']:
            print "All requested executions were successful deleted (total of {0})". \
                format(response['successCount'])
            return True
        else:
            print "Errors on deleting requested executions ({0}/{1} failed)". \
                format(response['failedCount'], response['requestCount'])
            return False
    except requests.exceptions.RequestException as exception:
        if CONFIGS['debug']:
            print exception
        return False


# Calling main
if __name__ == "__main__":

    CONFIGS = init_global_vars()

    proto = 'https' if CONFIGS["over_ssl"] else 'http'

    URL = '{0}://{1}:{2}/api/{3}/'.format(
        proto, CONFIGS["hostname"], CONFIGS["port"], CONFIGS["api_version"])
    HEADERS = {
        'Content-Type': 'application/json',
        'X-RunDeck-Auth-Token': CONFIGS['token'],
        'Accept': 'application/json'
    }
