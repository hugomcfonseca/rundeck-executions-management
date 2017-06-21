#!/usr/bin/python

import requests
import time
import json
import sys
import argparse

def main():
    '''Control all script flow'''

    global URL
    global HEADERS

    parser = argparse.ArgumentParser(description='Delete old and/or obsolete executions on Rundeck')
    parser.add_argument('-h', '--host', metavar='Host', type=str, default='localhost', \
                        help='IP address or domain of Rundeck')
    parser.add_argument('-p', '--port', metavar='Port', type=int, default=4440, \
                        help='Port of Rundeck')
    parser.add_argument('-t', '--token', metavar='Token', type=str, required=True, \
                        help='API token with correct permissions')
    parser.add_argument('--api-version', metavar='Version', type=int, default=19, \
                        help='API version of Rundeck')
    parser.add_argument('--search-time', metavar='Seconds', type=int, default=60, \
                        help='Time to expire search queries')
    parser.add_argument('--delete-time', metavar='Seconds', type=int, default=1200, \
                        help='Time to expire delete queries')
    parser.add_argument('--keeping-days', metavar='Days', type=int, default=21, \
                        help='Number of days to keep logs')
    parser.add_argument('--delete-size', metavar='N', type=int, default=1000, \
                        help='Number of executions to delete by cycle')
    parser.add_argument('--over-ssl', type=bool, default=False, \
                        help='Used when Rundeck is server over HTTPS')
    parser.add_argument('--delete-execution', type=int, default=5000, \
                        help='Used when Rundeck is server over HTTPS')

    args = parser.parse_args()

    return 1

def check_token_permissions():
    '''Used to validate API token deleting permissions'''

    return True

def get_all_projects():

    return True

def get_jobs_by_project(project_name):

    return True

def get_executions_by_job(job_id):

    return True

def get_executions_by_project(project_name):

    return True

def check_execution_date(execution_date):

    return True

def delete_executions(executions_ids):

    return True

# Calling main
main()