#!/usr/bin/python3

import json
import requests
import signal
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import modules.base
from modules.logger import Logger
#from modules.rundeck import RundeckApi


def get_all_projects(only_names=True):
    '''Get every project info and returns only their names'''

    endpoint = URL + 'projects'

    try:
        response = requests.get(endpoint, headers=HEADERS,
                                verify=False, timeout=CONFIGS['SEARCH_TIMEOUT'])
        if only_names:
            _, project_info = modules.base.parse_json_response(response, None, 'name')
        else:
            _, project_info = modules.base.parse_json_response(response)
    except requests.exceptions.RequestException as exception:
        if CONFIGS['VERBOSE']:
            print(exception)
        return False

    return project_info


def get_jobs_by_project(project_name, only_ids=True):
    '''Get jobs by a given project '''

    endpoint = URL + 'project/' + project_name + '/jobs'

    try:
        response = requests.get(endpoint, headers=HEADERS,
                                verify=False, timeout=CONFIGS['SEARCH_TIMEOUT'])
        if only_ids:
            _, job_info = modules.base.parse_json_response(response, None, 'id')
        else:
            _, job_info = modules.base.parse_json_response(response)
    except requests.exceptions.RequestException as exception:
        if CONFIGS['VERBOSE']:
            print(exception)
        return False

    return job_info


def get_executions(job_id, page, job_filter=True, only_ids=True):
    '''Get executions older than a given number of days by job or project '''

    if job_filter:
        endpoint = URL + 'job/' + job_id + '/executions'
        parameters = {
            'max': CONFIGS['CHUNK_SIZE'],
            'offset': page * CONFIGS['CHUNK_SIZE'],
        }
    else:
        endpoint = URL + 'project/' + job_id + '/executions'
        parameters = {
            'max': CONFIGS['CHUNK_SIZE'],
            'olderFilter': str(CONFIGS['RECORDS_KEEP_TIME'])
        }

    try:
        response = requests.get(endpoint, params=parameters, headers=HEADERS,
                                verify=False, timeout=CONFIGS['SEARCH_TIMEOUT'])
        if only_ids:
            _, execution_info = modules.base.parse_json_response(response, 'executions', 'id')
        else:
            _, execution_info = modules.base.parse_json_response(response, 'executions')
    except requests.exceptions.RequestException as exception:
        if CONFIGS['VERBOSE']:
            print(exception)
        return None

    return execution_info


def get_executions_total(identifier, job_filter=True):
    '''Get executions counter by project or job'''

    executions_count = 0

    if job_filter:
        endpoint = URL + 'job/' + identifier + '/executions'
    else:
        endpoint = URL + 'project/' + identifier + '/executions'

    parameters = {
        'olderFilter': str(CONFIGS['RECORDS_KEEP_TIME']),
        'max': 1
    }

    try:
        response = requests.get(endpoint, params=parameters, headers=HEADERS,
                                verify=False, timeout=CONFIGS['SEARCH_TIMEOUT'])
        _, executions_paging = modules.base.parse_json_response(response, 'paging')
        executions_count = executions_paging['total']
    except requests.exceptions.RequestException as exception:
        if CONFIGS['VERBOSE']:
            print(exception)
        return False

    return executions_count


def delete_executions(executions_ids):
    '''Bulk deletions of Rundeck executions'''

    endpoint = URL + 'executions/delete'
    data = json.dumps(executions_ids)

    try:
        request = requests.post(
            endpoint, headers=HEADERS, data=data, verify=False, timeout=CONFIGS['DELETE_TIMEOUT'])
        _, response = modules.base.parse_json_response(request)

        if response['allsuccessful']:
            print("All requested executions were successfully deleted (total of {0})".
                  format(response['successCount']))
            return True
        else:
            print("Errors on deleting requested executions ({0}/{1} failed)".
                  format(response['failedCount'], response['requestCount']))
            return False
    except requests.exceptions.RequestException as exception:
        if CONFIGS['VERBOSE']:
            print(exception)
        return False


# Calling main
if __name__ == "__main__":
    signal.signal(signal.SIGINT, modules.base.sigint_handler)

    CONFIGS = modules.base.parse_args(
        'Listing running jobs and delete old logs from your Rundeck server.')
    LOGGING = Logger(level=2)

    if not modules.base.validate_keeping_time(CONFIGS['RECORDS_KEEP_TIME']):
        LOGGING.write_to_log("Invalid parameter \'RECORDS_KEEP_TIME\'. Exiting...")
        exit(1)

    if CONFIGS['SSL_ENABLED']:
        proto = 'https'
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    else:
        proto = 'http'

    URL = '{0}://{1}:{2}/api/{3}/'.format(
        proto, CONFIGS["HOST"], CONFIGS["PORT"], CONFIGS["API_VERSION"])
    HEADERS = {
        'Content-Type': 'application/json',
        'X-Rundeck-Auth-Token': CONFIGS['TOKEN'],
        'Accept': 'application/json'
    }

    projects = get_all_projects()

    if projects is None:
        LOGGING.write_to_log("Error on reading Rundeck projects. Exiting...")
        exit(1)

    for project in projects:
        page_number = 0

        if CONFIGS['EXECUTIONS_BY_PROJECT']:
            count_execs = get_executions_total(project, False)

            if count_execs is None:
                LOGGING.write_to_log("Error on reading counter of Rundeck executions. Exiting...")
                exit(1)

            total_pages = modules.base.get_num_pages(
                count_execs, CONFIGS["CHUNK_SIZE"])

            if count_execs > 0:
                LOGGING.write_to_log("[" + str(project) + "]: There are " + str(count_execs) +
                                     " old deletable executions", log_level=2)
                LOGGING.write_to_log("[" + str(project) + "]: Processing executions deleting in " +
                                     str(total_pages) + " cycles.", log_level=2)
            else:
                LOGGING.write_to_log("[" + str(project) + "]: There are no deletable executions",
                                     log_level=2)

            for actual_page in range(page_number, total_pages + 1):
                executions = get_executions(project, actual_page, False)

                if executions is None:
                    LOGGING.write_to_log("Error on reading Rundeck executions. Exiting...")
                    exit(1)
                else:
                    success = delete_executions(executions)
        else:
            jobs = get_jobs_by_project(project)
            for job in jobs:
                count_execs = get_executions_total(job)
                total_pages = modules.base.get_num_pages(
                    count_execs, CONFIGS["CHUNK_SIZE"])

                if count_execs > 0:
                    LOGGING.write_to_log("[" + str(project) + "]: There are " + str(count_execs) +
                                         " old deletable executions", log_level=2)
                    LOGGING.write_to_log("[" + str(project) + "]: Processing executions deleting in " +
                                         str(total_pages) + " cycles.", log_level=2)
                else:
                    LOGGING.write_to_log("[" + str(project) + "]: There are no deletable executions",
                                         log_level=2)
                    break

                for actual_page in range(page_number, total_pages + 1):
                    executions = get_executions(job, actual_page)

                    if executions:
                        success = delete_executions(executions)
                    elif not executions or not success:
                        break

    exit(0)
    