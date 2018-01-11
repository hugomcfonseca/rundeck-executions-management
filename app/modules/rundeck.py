#!/usr/bin/python

from json import dumps, loads
from requests import get, post, exceptions

from modules.logger import Logger


class RundeckApi:
    '''...'''

    def __init__(self, token, url, headers, db, chunk_size=200, keep_time='30d', ssl=False, search_time=60, del_time=300):
        '''...'''
        self.token = token
        self.url = url
        self.headers = headers
        self.db = db
        self.chunk_size = chunk_size
        self.keep_time = keep_time
        self.check_ssl = ssl
        self.search_time = search_time
        self.del_time = del_time

    def get(self, endpoint, parameters=''):
        '''...'''
        status = False
        data = ''

        if not endpoint:
            status = False
            data = 'No valid endpoint.'
            return status, data

        try:
            response = get(endpoint, params=parameters, headers=self.headers,
                           verify=self.check_ssl, timeout=self.search_time)
            if response.ok:
                status = True
                data = response
            else:
                status = False
                data = 'Failing accessing API endpoint with http code: {0}'.format(
                    response.status_code)
        except exceptions.RequestException as exception:
            print(exception)

        return status, data

    def post(self, endpoint, parameters=''):
        '''...'''
        status = False
        data = ''

        if not endpoint:
            status = False
            data = 'No valid endpoint.'
            return status, data

        try:
            response = post(endpoint, data=parameters, headers=self.headers,
                            verify=self.check_ssl, timeout=self.del_time)
            if response.ok:
                status = True
                data = response
            else:
                status = False
                data = 'Failing accessing API endpoint with http code: {0}'.format(
                    response.status_code)
        except exceptions.RequestException as exception:
            print(exception)

        return status, data

    def parse_json_response(self, response, filter_by='', append_by=''):
        '''...'''
        data = []

        try:
            res_json = response.json
        except ValueError, e:
            msg = ''
            return False

        if filter_by:
            result = res_json[filter_by]
        else:
            result = res_json

        if isinstance(result, list):
            for data in result:
                if append_by is not None:
                    data.append(data[append_by])
                else:
                    data.append(data)
        else:
            data = result

        return data

    def get_projects(self, only_names=True):
        '''Retrieve info about existing projects'''
        endpoint = '{0}/projects'.format(self.url)
        status = False
        data = ''

        status, response = self.get(endpoint)

        if only_names and status:
            status = True
            data = parse_json_response(response, None, 'name')
        else if status and not only_names:
            status = True
            data = parse_json_response(response)
        else:
            status = False
            data = response

        if not data:
            data = 'Response is not a JSON'

        return status, data

    def get_jobs_by_project(self, project_name, only_ids=True):
        '''Retrieve info about all jobs by project'''
        endpoint = '{0}/project/{1}/jobs'.format(self.url, project_name)
        status = False
        data = ''

        status, response = self.get(endpoint)

        if only_ids and status:
            status = True
            data = parse_json_response(response, None, 'id')
        else if status and not only_ids:
            status = True
            data = parse_json_response(response)
        else:
            status = False
            data = response

        if not data:
            data = 'Response is not a JSON'

        return status, data

    def get_executions(self, job_id, page, job_filter=True, only_ids=True, only_running=False):
        '''Get executions older than a given number of days by job or project'''

        status = False
        search_type = 'job' if job_filter else 'project'
        endpoint = '{0}/{1}/{2}/executions'.format(
            self.url, search_type, identifier)

        if job_filter:
            parameters = {
                'max': self.chunk_size,
                'offset': page * self.chunk_size,
            }
        else:
            parameters = {
                'max': self.chunk_size,
                'olderFilter': str(self.keep_time)
            }

        if only_running:
            endpoint = endpoint + '/running'

        status, response = self.get(endpoint, parameters)

        if only_ids and status:
            status = True
            data = parse_json_response(response, 'executions', 'id')
        else if status and not only_ids:
            status = True
            data = parse_json_response(response, 'executions')
        else:
            status = False
            data = response

        if not data:
            data = 'Response is not a JSON'

        return status, data

    def get_total_executions(self, identifier, job_filter=True):
        '''Get executions counter by project or job'''

        status = False
        search_type = 'job' if job_filter else 'project'
        endpoint = '{0}/{1}/{2}/executions'.format(
            self.url, search_type, identifier)
        parameters = {
            'olderFilter': str(self.keep_time),
            'max': 1
        }

        status, response = self.get(endpoint, parameters)

        if status:
            status = True
            data = parse_json_response(response, 'paging', 'total')
        else:
            status = False
            data = response

        if not data:
            data = 'Response is not a JSON'

        return status, data

    # @todo: Improve error handling on it
    def get_workflow_ids(self, executions_ids):
        '''...'''
        mysql_client = self.db.cursor()

        # Convert execution list to a comma-separated string
        executions_ids = ','.join(map(str, executions_ids))
        workflow_ids = ''
        workflow_step_ids = ''

        # Return workflow IDs
        workflow_stmt = 'SELECT workflow_id FROM execution WHERE id IN ({0})'.format(
            executions_ids)
        mysql_client.execute(workflow_stmt)

        for workflow_id in mysql_client:
            workflow_ids = workflow_ids + ',' + str(workflow_id[0])

        workflow_ids = workflow_ids.strip(',')

        # Return workflow step IDs
        if workflow_ids:
            workflow_step_stmt = 'SELECT workflow_step_id FROM workflow_workflow_step WHERE workflow_commands_id IN ({0})'.format(
                workflow_ids)
            mysql_client.execute(workflow_step_stmt)

            for workflow_step_id in mysql_client:
                workflow_step_ids = workflow_step_ids + \
                    ',' + str(workflow_step_id[0])

            workflow_step_ids = workflow_step_ids.strip(',')

        mysql_client.close()
        self.db.close()

        return workflow_ids, workflow_step_ids, ''

    def delete_executions(executions_ids):
        '''Bulk deletions of Rundeck executions'''

        endpoint = '{0}/executions/delete'.format(self.url)
        data = dumps(executions_ids)
        status = False
        msg = ''

        status, response = self.post(endpoint, data)

        if status:
            all_successed = parse_json_response(response, 'allsuccessful')
            if all_successed:
                status = True
            else:
                status = False

        return status, msg

    # @todo: Improve error handling on it
    def delete_workflows(workflow_ids, workflow_step_ids):
        '''...'''
        mysql_client = self.db.cursor()

        # Prepare statement queries
        if workflow_ids and CONFIGS.unoptimized:
            work_workflow_delete = "DELETE FROM workflow_workflow_step WHERE workflow_commands_id IN ({0})".format(
                workflow_ids)
            mysql_client.execute(work_workflow_delete)

        if workflow_step_ids:
            workflow_step_delete = "DELETE FROM workflow_step WHERE id IN ({0})".format(
                workflow_step_ids)
            mysql_client.execute(workflow_step_delete)

        if workflow_ids:
            workflow_delete = "DELETE FROM workflow WHERE id IN ({0})".format(
                workflow_ids)
            mysql_client.execute(workflow_delete)

        self.db.commit()

        mysql_client.close()
        self.db.close()

        return True
