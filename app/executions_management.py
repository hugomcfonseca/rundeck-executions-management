#!/usr/bin/python3

from os import environ
from signal import signal, SIGINT

import modules.base as base
from modules.db import DatabaseConn
from modules.logger import Logger
from modules.rundeck import RundeckApi


if __name__ == '__main__':
    signal(SIGINT, base.sigint_handler)

    # Parse configuration file w/ mandatory parameters to the script
    CONF = base.parse_args('Rundeck manager - listing and maintenance of executions data')
    # Initialization of class objects
    LOG = Logger(level=1) if CONF.debug else Logger()

    # Validate configuration parameters
    if not base.validate_configs(CONF):
        LOG.write('Error on passed parameters. Exiting without success...', 5)
        exit(1)

    # Set up global variables
    DB_HOST = environ['DATASOURCE_HOST'] if 'DATASOURCE_HOST' in environ else CONF.db_host
    DB_NAME = environ['DATASOURCE_DBNAME'] if 'DATASOURCE_DBNAME' in environ else CONF.db_name
    DB_USER = environ['DATASOURCE_USER'] if 'DATASOURCE_USER' in environ else CONF.db_user
    DB_PORT = CONF.db_port

    if 'DATASOURCE_PASSWORD' in environ:
        DB_PASS = environ['DATASOURCE_PASSWORD']
    elif CONF.db_pass != '' and not 'DATASOURCE_PASSWORD' in environ:
        DB_PASS = CONF.db_pass
    else:
        LOG.write('Missing database password.')
        exit(1)

    # Set up global variables
    PROTOCOL = 'https' if CONF.ssl_enabled else 'http'
    URL = '{0}://{1}:{2}/api/{3}'.format(PROTOCOL,
                                         CONF.host, CONF.port, CONF.api_version)
    HEADERS = {
        'X-Rundeck-Auth-Token': CONF.auth,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    DB_CONN = DatabaseConn(DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT)
    RDECK = RundeckApi(URL, HEADERS, DB_CONN, LOG, CONF.chunk_size, CONF.keep_time,
                       CONF.ssl_enabled, CONF.search_timeout, CONF.delete_timeout)

    # Start execution from available modes
    if CONF.execution_mode == 'cleanup':
        STATUS, MSG = RDECK.clean_executions(CONF.filtered_project, CONF.executions_by_project,
                                             CONF.retries, CONF.retry_delay, CONF.unoptimized)
    elif CONF.execution_mode == 'listing':
        STATUS, MSG = RDECK.list_executions(CONF.filtered_project, CONF.filtered_job, CONF.running)
    else:
        LOG.write('No execution mode matching {0}'.format(CONF.execution_mode), 3)

    if not STATUS:
        LOG.write('Exiting without success...', 4)

    exit(not STATUS)
