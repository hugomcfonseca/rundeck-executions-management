#!/usr/bin/python

from os import environ
from signal import signal, SIGINT
from time import sleep

import modules.base as base
from modules.db import DatabaseConn
from modules.logger import Logger
from modules.rundeck import RundeckApi


def executions_cleanup(project_name=None):
    '''...'''
    del_executions = 0
    filter_project = True if project_name else False

    status, projects = RUNDECK_API.get_projects()

    if not status:
        msg = 'Error getting projects\' listing.'
        return False, msg

    for project in projects:
        page_number = 0
        total_pages = 0

        if not filter_project or project == project_name:
            if CONFIGS.executions_by_project:
                status, n_executions = RUNDECK_API.get_total_executions(
                    project, False)

                if status:
                    if n_executions > 0:
                        total_pages = base.get_num_pages(
                            n_executions, CONFIGS.chunk_size)
                        LOG.write('[{0}]: There are {1} old deletable executions.'.format(
                            project, n_executions))
                        LOG.write('[{0}]: Processing logs deleting in {1} cycles.'.format(
                            project, total_pages))
                        del_executions = del_executions + n_executions
                    else:
                        LOG.write(
                            '[{0}]: There are no deletable executions.'.format(project))
                        continue
                else:
                    msg = '[{0}]: Error getting counter of executions'.format(
                        project)
                    return False, msg

                for actual_page in range(page_number, total_pages):
                    retries = 0
                    status, executions = RUNDECK_API.get_executions(
                        project, actual_page, False)

                    if status:
                        interval = [actual_page * CONFIGS.chunk_size,
                                    actual_page * CONFIGS.chunk_size + len(executions)]
                        LOG.write('[{0}]: Deleting range {1} to {2}'.format(
                            project, interval[0], interval[1]))
                        for retry in range(0, CONFIGS.retries):
                            retries = retry + 1
                            workflows, workflow_steps, err_workflow = RUNDECK_API.get_workflow_ids(
                                executions)

                            if not workflows or not workflow_steps:
                                return False, err_workflow

                            if CONFIGS.debug:
                                LOG.write(
                                    '[{0}] Removing following executions -> {1}'.format(project, executions))
                                LOG.write(
                                    '[{0}] Removing following workflows -> {1}'.format(project, workflows))

                            res_exec, msg_exec = RUNDECK_API.delete_executions(
                                executions)
                            res_wf, msg_wf = RUNDECK_API.delete_workflows(
                                workflows, workflow_steps)

                            if res_exec and res_wf:
                                break
                            elif not (res_exec or res_wf) and retries <= CONFIGS.retries:
                                LOG.write('[{0}] #{1} try not succeded. Trying again in {2} seconds...'.format(
                                    project, retries, CONFIGS.retry_delay))
                                sleep(CONFIGS.retry_delay)
                                continue
                            else:
                                msg = '[{0}]: Error deleting executions.'.format(
                                    project)
                                return False, msg
                    else:
                        msg = '[{0}]: Error getting executions.'.format(
                            project)
                        return False, msg
            else:
                # temporary - do not use this mode
                jobs = RUNDECK_API.get_jobs_by_project(project)
                for job in jobs:
                    status, n_executions = RUNDECK_API.get_total_executions(
                        job)
                    total_pages = base.get_num_pages(
                        n_executions, CONFIGS.chunk_size)

                    if status:
                        if n_executions > 0:
                            total_pages = base.get_num_pages(
                                n_executions, CONFIGS.chunk_size)
                            LOG.write('[{0}]: There are {1} old deletable executions.'.format(
                                project, n_executions))
                            LOG.write('[{0}]: Processing logs deleting in {1} cycles.'.format(
                                project, total_pages))
                            del_executions = del_executions + n_executions
                        else:
                            LOG.write(
                                '[{0}]: There are no deletable executions.'.format(project))
                            continue
                    else:
                        msg = '[{0}]: Error getting counter of executions'.format(
                            project)
                        return False, msg

                    for actual_page in range(page_number, total_pages + 1):
                        executions = RUNDECK_API.get_executions(
                            job, actual_page)

                        if executions:
                            success = delete_executions(executions)
                        elif not executions or not success:
                            break

    LOG.write('Statistics: {0} old executions deleted.'.format(
        del_executions))

    return True, ''


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
            err_msg = '[{0}] Error getting executions.'.format(proj)
            return False, err_msg

        for execution in executions:
            if filter_by_jobname:
                if execution['job']['name'] == job:
                    LOG.write('[{0}] - Job \'{1}\' is {2}'.format(execution['project'],
                                                                  execution['job']['name'], execution['status']))
            else:
                LOG.write('[{0}] - Job \'{1}\' is {2}'.format(execution['project'],
                                                              execution['job']['name'], execution['status']))

    return True, ''


# Calling main
if __name__ == '__main__':
    signal(SIGINT, base.sigint_handler)

    # Initialization of class objects
    LOG = Logger(level=2)

    # Parse configuration file w/ mandatory parameters to the script
    CONFIGS = base.parse_args(
        'Listing running jobs and delete old logs from your Rundeck server.')

    # Validate configuration parameters
    if not base.validate_configs(CONFIGS):
        LOG.write('Error on passed parameters. Exiting without success...')
        exit(1)

    # Set up global variables
    RUNDECK_DB_HOST = environ['DATASOURCE_HOST'] if 'DATASOURCE_HOST' in environ else CONFIGS.db_host
    RUNDECK_DB_NAME = environ['DATASOURCE_DBNAME'] if 'DATASOURCE_DBNAME' in environ else CONFIGS.db_name
    RUNDECK_DB_USER = environ['DATASOURCE_USER'] if 'DATASOURCE_USER' in environ else CONFIGS.db_user
    RUNDECK_DB_PORT = CONFIGS.db_port

    if 'DATASOURCE_PASSWORD' in environ:
        RUNDECK_DB_PASS = environ['DATASOURCE_PASSWORD']
    elif CONFIGS.db_pass != '' and not 'DATASOURCE_PASSWORD' in environ:
        RUNDECK_DB_PASS = CONFIGS.db_pass
    else:
        print('Missing database password.')
        exit(1)

    # Set up global variables
    PROTOCOL = 'http'
    if CONFIGS.ssl_enabled:
        PROTOCOL = 'https'

    URL = '{0}://{1}:{2}/api/{3}'.format(PROTOCOL,
                                         CONFIGS.host, CONFIGS.port, CONFIGS.api_version)
    HEADERS = {
        'Content-Type': 'application/json',
        'X-Rundeck-Auth-Token': CONFIGS.auth,
        'Accept': 'application/json'
    }

    DB_CONNECTOR = DatabaseConn(CONFIGS.db_name, CONFIGS.db_user,
                                CONFIGS.db_pass, CONFIGS.db_host, CONFIGS.db_port)
    RUNDECK_API = RundeckApi(URL, HEADERS, DB_CONNECTOR,
                             CONFIGS.chunk_size, CONFIGS.keep_time, CONFIGS.ssl_enabled)

    # Start execution from available modes
    if CONFIGS.execution_mode == 'cleanup':
        STATUS, ERROR_MSG = executions_cleanup(CONFIGS.filtered_project)
    elif CONFIGS.execution_mode == 'listing':
        STATUS, ERROR_MSG = listing_executions(
            CONFIGS.filtered_project, CONFIGS.filtered_job, CONFIGS.only_running)
    else:
        LOG.write('No execution mode matching {0}'.format(
            CONFIGS.execution_mode))

    if not STATUS:
        LOG.write(ERROR_MSG + ' Exiting without success...')

    exit(not STATUS)
