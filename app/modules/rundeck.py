#!/usr/bin/python

from json import dumps
from requests import get, post, exceptions


class RundeckApi(object):
    '''
    This class provides multiple functions to manage projects, jobs or executions from
    Rundeck.

    To do it so, it uses Rundeck API endpoints, but also a connector to Rundeck database
    and complements deleting executions' data from workflow tables.
    '''

    def __init__(self, url, headers, db_conn, chunk_size=200, keep_time='30d', ssl=False, search_time=60, del_time=300):
        '''Initialization of global variables'''
        self._url = url
        self._headers = headers
        self._db = db_conn
        self._chunk_size = chunk_size
        self._keep_time = keep_time
        self._check_ssl = ssl
        self._search_time = search_time
        self._del_time = del_time

    def get(self, endpoint, parameters=''):
        '''GET requests in Rundeck API endpoints'''
        status = False
        data = ''

        if not endpoint:
            status = False
            data = 'No valid endpoint.'
            return status, data

        try:
            response = get(endpoint, params=parameters, headers=self._headers,
                           verify=self._check_ssl, timeout=self._search_time)
            if response.ok:
                status = True
                data = response
            else:
                status = False
                data = 'Failing accessing API endpoint with http code: {0}'.format(
                    response.status_code)
        except exceptions.RequestException as exception:
            data = exception

        return status, data

    def post(self, endpoint, parameters=''):
        '''POST requests in Rundeck API endpoints'''
        status = False
        data = ''

        if not endpoint:
            status = False
            data = 'No valid endpoint.'
            return status, data

        try:
            response = post(endpoint, data=parameters, headers=self._headers,
                            verify=self._check_ssl, timeout=self._del_time)
            if response.ok:
                status = True
                data = response
            else:
                status = False
                data = 'Failing accessing API endpoint with http code: {0}'.format(
                    response.status_code)
        except exceptions.RequestException as exception:
            data = exception

        return status, data

    def parse_json_response(self, response, filter_by='', appender=''):
        '''...'''
        parsed_response = []

        try:
            res = response.json()
        except ValueError:
            return False

        res = res[filter_by] if filter_by else res

        if isinstance(res, list):
            for data in res:
                if appender is not None:
                    parsed_response.append(data[appender])
                else:
                    parsed_response.append(data)
        else:
            parsed_response = res[appender] if appender else res

        return parsed_response

    def get_projects(self, only_names=True):
        '''Retrieve info about existing projects'''
        endpoint = '{0}/projects'.format(self._url)
        status = False
        data = ''

        status, response = self.get(endpoint)

        if only_names and status:
            status = True
            data = self.parse_json_response(response, None, 'name')
        elif status and not only_names:
            status = True
            data = self.parse_json_response(response)
        else:
            status = False
            data = response

        if not data:
            data = 'Response is not a JSON'

        return status, data

    def get_jobs_by_project(self, project_name, only_ids=True):
        '''Retrieve info about all jobs by project'''
        endpoint = '{0}/project/{1}/jobs'.format(self._url, project_name)
        status = False
        data = ''

        status, response = self.get(endpoint)

        if only_ids and status:
            status = True
            data = self.parse_json_response(response, None, 'id')
        elif status and not only_ids:
            status = True
            data = self.parse_json_response(response)
        else:
            status = False
            data = response

        if not data:
            data = 'Response is not a JSON'

        return status, data

    def get_executions(self, identifier, page, jobs=True, only_ids=True, running=False):
        '''Get executions older than a given number of days by job or project'''

        status = False
        search_type = 'job' if jobs else 'project'
        endpoint = '{0}/{1}/{2}/executions'.format(
            self._url, search_type, identifier)

        if jobs:
            parameters = {
                'max': self._chunk_size,
                'offset': page * self._chunk_size,
            }
        else:
            parameters = {
                'max': self._chunk_size,
                'olderFilter': str(self._keep_time)
            }

        if running:
            endpoint = endpoint + '/running'

        status, response = self.get(endpoint, parameters)

        if only_ids and status:
            status = True
            data = self.parse_json_response(response, 'executions', 'id')
        elif status and not only_ids:
            status = True
            data = self.parse_json_response(response, 'executions')
        else:
            status = False
            data = response

        if not data:
            data = 'Response is not a JSON'

        return status, data

    def get_total_executions(self, identifier, jobs=True):
        '''Get executions counter by project or job'''

        status = False
        search_type = 'job' if jobs else 'project'
        endpoint = '{0}/{1}/{2}/executions'.format(
            self._url, search_type, identifier)
        parameters = {
            'olderFilter': str(self._keep_time),
            'max': 1
        }

        status, response = self.get(endpoint, parameters)

        if status:
            status = True
            data = self.parse_json_response(response, 'paging', 'total')
        else:
            status = False
            data = response if data else 'Response is not a JSON'

        return status, data

    def get_workflow_ids(self, executions_ids):
        '''Return IDs from workflow and related tables'''
        self._db.open()

        # Convert execution list to a comma-separated string
        executions_ids = ','.join(map(str, executions_ids))
        workflow_ids = ''
        workflow_step_ids = ''

        # Return workflow IDs
        workflow_stmt = 'SELECT workflow_id FROM execution WHERE id IN ({0})'.format(
            executions_ids)
        query_res = self._db.query(workflow_stmt)

        for workflow_id in query_res:
            workflow_ids = workflow_ids + ',' + str(workflow_id[0])

        workflow_ids = workflow_ids.strip(',')

        # Return workflow step IDs
        if workflow_ids:
            workflow_step_stmt = 'SELECT workflow_step_id FROM workflow_workflow_step WHERE workflow_commands_id IN ({0})'.format(
                workflow_ids)
            query_res = self._db.query(workflow_step_stmt)

            for workflow_step_id in query_res:
                workflow_step_ids = workflow_step_ids + \
                    ',' + str(workflow_step_id[0])

            workflow_step_ids = workflow_step_ids.strip(',')

        self._db.close()

        return workflow_ids, workflow_step_ids, ''

    def delete_executions(self, executions_ids):
        '''Bulk deletions of Rundeck executions'''

        endpoint = '{0}/executions/delete'.format(self._url)
        data = dumps(executions_ids)
        status = False
        msg = ''

        status, response = self.post(endpoint, data)

        if status:
            all_succedeed = self.parse_json_response(response, 'allsuccessful')
            if all_succedeed:
                status = True
            else:
                status = False

        return status, msg

    def delete_workflows(self, workflow_ids, workflow_step_ids, unoptimized=False):
        '''Bulk deletions of Rundeck workflow tables'''
        self._db.open()

        if workflow_ids and unoptimized:
            work_workflow_delete = 'DELETE FROM workflow_workflow_step WHERE workflow_commands_id IN ({0})'.format(
                workflow_ids)
            self._db.query(work_workflow_delete)

        if workflow_step_ids:
            workflow_step_delete = 'DELETE FROM workflow_step WHERE id IN ({0})'.format(
                workflow_step_ids)
            self._db.query(workflow_step_delete)

        if workflow_ids:
            workflow_delete = 'DELETE FROM workflow WHERE id IN ({0})'.format(
                workflow_ids)
            self._db.query(workflow_delete)

        self._db.apply()
        self._db.close()

        return True, ''
