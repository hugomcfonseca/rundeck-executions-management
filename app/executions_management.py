#!/usr/bin/python

from os import environ
from signal import signal, SIGINT

import modules.base as base
from modules.db import DatabaseConn
from modules.logger import Logger
from modules.rundeck import RundeckApi


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

    # Parse configuration file w/ mandatory parameters to the script
    CONFIGS = base.parse_args('Rundeck manager - listing and maintenance of executions data')
    # Initialization of class objects
    LOG = Logger(level=1) if CONFIGS.debug else Logger()

    # Validate configuration parameters
    if not base.validate_configs(CONFIGS):
        LOG.write('Error on passed parameters. Exiting without success...', 5)
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
    PROTOCOL = 'https' if CONFIGS.ssl_enabled else 'http'
    URL = '{0}://{1}:{2}/api/{3}'.format(PROTOCOL, CONFIGS.host, CONFIGS.port, CONFIGS.api_version)
    HEADERS = {
        'X-Rundeck-Auth-Token': CONFIGS.auth,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    DB_CONNECTOR = DatabaseConn(CONFIGS.db_name, CONFIGS.db_user, CONFIGS.db_pass, CONFIGS.db_host,
                                CONFIGS.db_port)
    RUNDECK_API = RundeckApi(URL, HEADERS, DB_CONNECTOR, LOG, CONFIGS.chunk_size, CONFIGS.keep_time,
                             CONFIGS.ssl_enabled, CONFIGS.search_timeout, CONFIGS.delete_timeout)

    # Start execution from available modes
    if CONFIGS.execution_mode == 'cleanup':
        STATUS = RUNDECK_API.clean_executions(CONFIGS.filtered_project, CONFIGS.executions_by_project,
                                              CONFIGS.retries, CONFIGS.retry_delay, CONFIGS.unoptimized)
    elif CONFIGS.execution_mode == 'listing':
        STATUS, ERROR_MSG = listing_executions(CONFIGS.filtered_project, CONFIGS.filtered_job,
                                               CONFIGS.only_running)
    else:
        LOG.write('No execution mode matching {0}'.format(CONFIGS.execution_mode), 3)

    if not STATUS:
        LOG.write('Exiting without success...', 4)

    exit(not STATUS)
