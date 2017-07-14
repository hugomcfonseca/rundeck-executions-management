#!/usr/bin/python

import json
import requests

from modules.base import get_num_pages
from modules.logger import Logger


class RundeckApi:
    '''...'''

    def __init__(self, configs, mode='cleanup'):

        self.url = configs.URL
        self.headers = configs.headers
        self.ssl = configs.SSL
        self.token = configs.token
        self.max = configs.max
        self.read_time = configs.read_time
        self.verbose = configs.verbose
        self.debug = configs.debug

        if mode == "listing":
            self.status = configs.execution_status
            self.filter_project = configs.filter_project
        else:
            self.keeping_time = configs.keeping_time
            self.write_time = configs.write_time

        self.logger = Logger()

    def check_my_token(self, token):
        '''...'''
        print(token)  # delete me

        return False

    def get_all_projects(self, only_names=True):
        '''Get every project info and returns only their names'''

        endpoint = self.url + 'projects'
        project_info = []

        try:
            response = requests.get(endpoint, headers=self.headers,
                                    verify=self.ssl, timeout=self.read_time)
            projects_data = response.json()

            for project_data in projects_data:
                if only_names:
                    project_info.append(project_data['name'])
                else:
                    project_info.append(project_data)
        except requests.exceptions.RequestException as exception:
            if self.debug:
                self.logger.write_to_log(exception)
            return None

        return project_info

    def get_jobs_by_project(self, project_name, only_ids=True):
        '''Get jobs by a given project '''

        endpoint = self.url + 'project/' + project_name + '/jobs'
        job_info = []

        try:
            response = requests.get(endpoint, headers=self.headers,
                                    verify=self.ssl, timeout=self.read_time)
            jobs_data = response.json()

            for job_data in jobs_data:
                if only_ids:
                    job_id = job_data.get('id')
                    job_info.append(job_id)
                else:
                    job_info.append(job_data)
        except requests.exceptions.RequestException as exception:
            if self.debug:
                self.logger.write_to_log(exception)
            return False

        return job_info

    def get_executions(self, job_id, page, job_filter=True, only_ids=True):
        '''Get executions older than a given number of days by job or project '''

        execution_info = []

        if job_filter:
            endpoint = self.url + 'job/' + job_id + '/executions'
        else:
            endpoint = self.url + 'project/' + job_id + '/executions'

        parameters = {
            'max': self.max,
            'offset': page * self.max,
            'olderFilter': self.keeping_time
        }

        try:
            response = requests.get(endpoint, params=parameters, headers=self.headers,
                                    verify=self.ssl, timeout=self.read_time)
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
            if self.debug:
                self.logger.write_to_log(exception)
            return None

        return execution_info

    def get_executions_total(self, id, job_filter=True):
        '''Get executions counter by project '''

        executions_count = 0

        if job_filter:
            endpoint = self.url + 'job/' + id + '/executions'
        else:
            endpoint = self.url + 'project/' + id + '/executions'

        parameters = {
            'olderFilter': self.keeping_time
        }

        try:
            response = requests.get(endpoint, params=parameters, headers=self.headers,
                                    verify=self.ssl, timeout=self.read_time)
            executions_data = response.json()
            executions_count = executions_data['paging']['total']
        except requests.exceptions.RequestException as exception:
            if self.debug:
                self.logger.write_to_log(exception)
            return None

        return executions_count

    def delete_executions(self, executions_ids):
        '''Bulk deletions of Rundeck executions'''

        endpoint = self.url + 'executions/delete'
        data = json.dumps(executions_ids)

        try:
            request = requests.post(endpoint, headers=self.headers,
                                    data=data, verify=self.ssl, timeout=self.write_time)
            response = request.json()

            if response['allsuccessful']:
                self.logger.write_to_log("All requested executions were successful deleted (total of {0})".
                                         format(response['successCount']))
                return True
            else:
                self.logger.write_to_log("Errors on deleting requested executions ({0}/{1} failed)".
                                         format(response['failedCount'], response['requestCount']))
                return False
        except requests.exceptions.RequestException as exception:
            if self.debug:
                self.logger.write_to_log(exception)
            return False

    def delete_old_logs(self, ):
        '''...'''

        projects = self.get_all_projects()

        for project in projects:
            page_number = 0

            if CONFIGS['execs_by_project']:
                count_execs = self.get_executions_total(project, False)
                total_pages = get_num_pages(count_execs)

                for actual_page in range(page_number, total_pages):
                    executions = self.get_executions(
                        project, actual_page, False)

                    if executions:
                        success = self.delete_executions(executions)
                    elif not executions or not success:
                        break
            else:
                jobs = self.get_jobs_by_project(project)
                for job in jobs:
                    executions = self.get_executions(job, page_number, True)

    def listing_running_jobs(self):
        '''...'''

        projects = self.get_all_projects()
