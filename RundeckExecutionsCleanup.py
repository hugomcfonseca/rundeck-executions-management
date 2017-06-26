#!/usr/bin/python3

import argparse
import json

import logging
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


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


def get_page_count(total):
    '''...'''

    counter = int(total / 200)

    if total % 200 > 0:
        counter += 1

    return counter


def check_token_permissions():
    '''Used to validate API token deleting permissions'''

    endpoint = ''

    return True


def get_all_projects(only_names=True):
    '''Get every project info and returns only their names'''

    endpoint = URL + 'projects'
    project_info = []

    try:
        response = requests.get(endpoint, headers=HEADERS,
                                verify=False, timeout=CONFIGS['search_time'])
        projects_data = response.json()

        for project_data in projects_data:
            if only_names:
                project_info.append(project_data['name'])
            else:
                project_info.append(project_data)
    except requests.exceptions.RequestException as exception:
        if CONFIGS['debug']:
            print(exception)
        return None

    return project_info


def get_jobs_by_project(project_name, only_ids=True):
    '''Get jobs by a given project '''

    endpoint = URL + 'project/' + project_name + '/jobs'
    job_info = []

    try:
        response = requests.get(endpoint, headers=HEADERS,
                                verify=False, timeout=CONFIGS['search_time'])
        jobs_data = response.json()

        for job_data in jobs_data:
            if only_ids:
                job_id = job_data.get('id')
                job_info.append(job_id)
            else:
                job_info.append(job_data)
    except requests.exceptions.RequestException as exception:
        if CONFIGS['debug']:
            print(exception)
        return False

    return job_info


def get_executions(job_id, page, job_filter=True, only_ids=True):
    '''Get executions older than a given number of days by job or project '''

    execution_info = []

    if job_filter:
        endpoint = URL + 'job/' + job_id + '/executions'
    else:
        endpoint = URL + 'project/' + job_id + '/executions'

    parameters = {
        'max': CONFIGS['delete_size'],
        'offset': page * CONFIGS['delete_size'],
        'olderFilter': str(CONFIGS['keeping_days']) + 'd'
    }

    try:
        response = requests.get(endpoint, params=parameters, headers=HEADERS,
                                verify=False, timeout=CONFIGS['search_time'])
        executions_data = response.json()

        for execution_data in executions_data['executions']:
            status = execution_data.get('status')

            if status != "running":
                if only_ids:
                    execution_id = execution_data.get('id')
                    execution_info.append(execution_id)
                else:
                    execution_info.append(execution_data)
    except requests.exceptions.RequestException as exception:
        if CONFIGS['debug']:
            print(exception)
        return None

    return execution_info


def get_executions_total(id, job_filter=True):
    '''Get executions counter by project '''

    executions_count = 0

    if job_filter:
        endpoint = URL + 'job/' + id + '/executions'
    else:
        endpoint = URL + 'project/' + id + '/executions'

    parameters = {
        'olderFilter': str(CONFIGS['keeping_days']) + 'd'
    }

    try:
        response = requests.get(endpoint, params=parameters, headers=HEADERS,
                                verify=False, timeout=CONFIGS['search_time'])
        executions_data = response.json()
        executions_count = executions_data['paging']['total']
    except requests.exceptions.RequestException as exception:
        if CONFIGS['debug']:
            print(exception)
        return None

    return executions_count


def delete_executions(executions_ids):
    '''Bulk deletions of Rundeck executions'''

    endpoint = URL + 'executions/delete'
    data = json.dumps(executions_ids)

    try:
        request = requests.post(
            endpoint, headers=HEADERS, data=data, verify=False, timeout=CONFIGS['delete_time'])
        response = request.json()

        if response['allsuccessful']:
            print("All requested executions were successful deleted (total of {0})".
                  format(response['successCount']))
            return True
        else:
            print("Errors on deleting requested executions ({0}/{1} failed)".
                  format(response['failedCount'], response['requestCount']))
            return False
    except requests.exceptions.RequestException as exception:
        if CONFIGS['debug']:
            print(exception)
        return False


# Calling main
if __name__ == "__main__":

    CONFIGS = init_global_vars()

    if CONFIGS['over_ssl']:
        proto = 'https'
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    else:
        proto = 'http'

    URL = '{0}://{1}:{2}/api/{3}/'.format(
        proto, CONFIGS["hostname"], CONFIGS["port"], CONFIGS["api_version"])
    HEADERS = {
        'Content-Type': 'application/json',
        'X-RunDeck-Auth-Token': CONFIGS['token'],
        'Accept': 'application/json'
    }

    projects = get_all_projects()

    for project in projects:
        page_number = 0

        if CONFIGS['execs_by_project']:
            count_execs = get_executions_total(project, False)
            total_pages = get_page_count(count_execs)

            for actual_page in range(page_number, total_pages):
                executions = get_executions(project, actual_page, False)
                success = delete_executions(executions)

                if not success:
                    break
        else:
            jobs = get_jobs_by_project(project)
            for job in jobs:
                executions = get_executions(job, page_number, True)
