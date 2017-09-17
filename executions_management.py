#!/usr/bin/python

from json import dumps
from signal import signal, SIGINT
from time import sleep
from requests import get, post, exceptions

import modules.base as base
from modules.logger import Logger
#from modules.rundeck import RundeckApi


def get_all_projects(only_names=True):
    '''Get every project info and returns only their names'''

    endpoint = URL + 'projects'
    status = False

    try:
        response = get(endpoint, headers=HEADERS,
                       verify=False, timeout=CONFIGS.search_timeout)
        if only_names:
            status, project_info = base.parse_json_response(
                response, None, 'name')
        else:
            status, project_info = base.parse_json_response(response)

        if status:
            return project_info
    except exceptions.RequestException as exception:
        if CONFIGS.debug:
            LOG.write(exception)

    return False


def get_jobs_by_project(project_name, only_ids=True):
    '''Get jobs by a given project '''

    endpoint = URL + 'project/' + project_name + '/jobs'
    status = False

    try:
        response = get(endpoint, headers=HEADERS,
                       verify=False, timeout=CONFIGS.search_timeout)
        if only_ids:
            status, job_info = base.parse_json_response(response, None, 'id')
        else:
            status, job_info = base.parse_json_response(response)

        if status:
            return job_info
    except exceptions.RequestException as exception:
        if CONFIGS.debug:
            LOG.write(exception)

    return False


def get_executions(job_id, page, job_filter=True, only_ids=True, only_running=False):
    '''Get executions older than a given number of days by job or project '''

    status = False

    if job_filter:
        endpoint = URL + 'job/' + job_id + '/executions'
        parameters = {
            'max': CONFIGS.chunk_size,
            'offset': page * CONFIGS.chunk_size,
        }
    else:
        endpoint = URL + 'project/' + job_id + '/executions'
        parameters = {
            'max': CONFIGS.chunk_size,
            'olderFilter': str(CONFIGS.keep_time)
        }

    if only_running:
        endpoint = endpoint + "/running"

    try:
        response = get(endpoint, params=parameters, headers=HEADERS,
                       verify=False, timeout=CONFIGS.search_timeout)
        if only_ids:
            status, execution_info = base.parse_json_response(
                response, 'executions', 'id')
        else:
            status, execution_info = base.parse_json_response(
                response, 'executions')

        if status:
            return execution_info
    except exceptions.RequestException as exception:
        if CONFIGS.debug:
            LOG.write(exception)

    return False


def get_executions_total(identifier, job_filter=True):
    '''Get executions counter by project or job'''

    status = False

    if job_filter:
        endpoint = URL + 'job/' + identifier + '/executions'
    else:
        endpoint = URL + 'project/' + identifier + '/executions'

    parameters = {
        'olderFilter': str(CONFIGS.keep_time),
        'max': 1
    }

    try:
        response = get(endpoint, params=parameters, headers=HEADERS,
                       verify=False, timeout=CONFIGS.search_timeout)
        status, executions_paging = base.parse_json_response(
            response, 'paging')

        if status:
            return executions_paging['total']
    except exceptions.RequestException as exception:
        if CONFIGS.debug:
            LOG.write(exception)

    return False


def delete_executions(executions_ids):
    '''Bulk deletions of Rundeck executions'''

    endpoint = URL + 'executions/delete'
    data = dumps(executions_ids)
    status = False

    try:
        request = post(
            endpoint, headers=HEADERS, data=data, verify=False, timeout=CONFIGS.delete_timeout)
        status, response = base.parse_json_response(request)

        if status:
            if response['allsuccessful']:
                LOG.write("All requested executions were successfully deleted (total of {0})".
                          format(response['successCount']))
                return True
            else:
                LOG.write("Errors on deleting requested executions ({0}/{1} failed)".
                          format(response['failedCount'], response['requestCount']))
                return False
    except exceptions.RequestException as exception:
        if CONFIGS.debug:
            LOG.write(exception)

    return False


def executions_cleanup(project_name=None):
    '''...'''
    projects = get_all_projects()
    cleaned_executions = 0

    if not projects:
        msg = "Error getting projects' listing."
        return False, msg

    if project_name != None and project_name != "":
        filter_project = True
    else:
        filter_project = False

    for project in projects:
        page_number = 0
        total_pages = 0

        if not filter_project or project == project_name:
            if CONFIGS.executions_by_project:
                count_execs = get_executions_total(project, False)

                if count_execs > 0:
                    total_pages = base.get_num_pages(
                        count_execs, CONFIGS.chunk_size)
                    LOG.write("[{0}]: There are {1} old deletable executions.".format(
                        project, count_execs))
                    LOG.write("[{0}]: Processing logs deleting in {1} cycles.".format(
                        project, total_pages))
                    cleaned_executions = cleaned_executions + count_execs
                elif count_execs is False:
                    msg = "[{0}]: Error getting counter of executions".format(
                        project)
                    return False, msg
                elif count_execs == 0:
                    LOG.write(
                        "[{0}]: There are no deletable executions.".format(project))
                    continue

                for actual_page in range(page_number, total_pages):
                    retries = 0
                    executions = get_executions(project, actual_page, False)

                    if executions:
                        interval = [actual_page * CONFIGS.chunk_size,
                                    actual_page * CONFIGS.chunk_size + len(executions)]
                        LOG.write("[{0}]: Deleting range {1} to {2}".format(
                            project, interval[0], interval[1]))
                        for retry in range(0, CONFIGS.retries):
                            retries = retry + 1
                            success = delete_executions(executions)

                            if success:
                                break
                            elif not success and retries <= CONFIGS.retries:
                                LOG.write("[{0}] #{1} try not success. Trying again in {2} seconds...".format(
                                    project, retries, CONFIGS.retry_delay))
                                sleep(CONFIGS.retry_delay)
                                continue
                            else:
                                msg = "[{0}]: Error deleting executions.".format(
                                    project)
                                return False, msg
                    else:
                        msg = "[{0}]: Error getting executions.".format(
                            project)
                        return False, msg
            else:
                # temporary - do not use this mode
                jobs = get_jobs_by_project(project)
                for job in jobs:
                    count_execs = get_executions_total(job)
                    total_pages = base.get_num_pages(
                        count_execs, CONFIGS.chunk_size)

                    if count_execs > 0:
                        LOG.write("[{0}]: There are {1} old deletable executions.".format(
                            project, count_execs))
                        LOG.write("[{0}]: Processing logs deleting in {1} cycles.".format(
                            project, total_pages))
                    else:
                        LOG.write(
                            "[{0}]: There are no deletable executions.".format(project))

                    for actual_page in range(page_number, total_pages + 1):
                        executions = get_executions(job, actual_page)

                        if executions:
                            success = delete_executions(executions)
                        elif not executions or not success:
                            break

    LOG.write("Statistics: {0} old executions deleted.".format(
        cleaned_executions))

    return True, ""


def listing_executions(project=None, job=None, only_running=False):
    '''...'''

    filter_by_jobname = False

    if project != None:
        projects = project
    else:
        projects = get_all_projects()

    if job != None:
        filter_by_jobname = True

    for proj in projects:
        if only_running:
            executions = get_executions(proj, 0, False, False, True)
        else:
            executions = get_executions(proj, 0, False, False)

        if executions is False:
            err_msg = "[{0}] Error getting executions.".format(proj)
            return False, err_msg

        for execution in executions:
            if filter_by_jobname:
                if execution['job']['name'] == job:
                    LOG.write("[{0}] - Job \"{1}\" is {2}".format(execution['project'],
                                                                  execution['job']['name'], execution['status']))
            else:
                LOG.write("[{0}] - Job \"{1}\" is {2}".format(execution['project'],
                                                              execution['job']['name'], execution['status']))

    return True, ""


# Calling main
if __name__ == "__main__":
    signal(SIGINT, base.sigint_handler)

    # Initialization of class objects
    LOG = Logger(level=2)

    # Parse configuration file w/ mandatory parameters to the script
    CONFIGS = base.parse_args(
        'Listing running jobs and delete old logs from your Rundeck server.')

    # Validate configuration parameters
    if not base.validate_configs(CONFIGS):
        LOG.write("Error on passed parameters. Exiting without success...")
        exit(1)

    # Set up global variables
    PROTOCOL = "http"
    if CONFIGS.ssl_enabled:
        PROTOCOL = 'https'

    URL = '{0}://{1}:{2}/api/{3}/'.format(PROTOCOL,
                                          CONFIGS.host, CONFIGS.port, CONFIGS.api_version)
    HEADERS = {
        'Content-Type': 'application/json',
        'X-Rundeck-Auth-Token': CONFIGS.auth,
        'Accept': 'application/json'
    }

    # Start execution from available modes
    if CONFIGS.execution_mode == "cleanup":
        STATUS, ERROR_MSG = executions_cleanup(CONFIGS.filtered_project)
    elif CONFIGS.execution_mode == "listing":
        STATUS, ERROR_MSG = listing_executions(
            CONFIGS.filtered_project, CONFIGS.filtered_job, CONFIGS.only_running)
    else:
        LOG.write("No execution mode matching {0}".format(
            CONFIGS.execution_mode))

    if not STATUS:
        LOG.write(ERROR_MSG + " Exiting without success...")

    exit(not STATUS)
