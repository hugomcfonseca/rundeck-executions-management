#!/usr/bin/python

from json import dumps
from time import sleep
from requests import get, post, exceptions
from .base import get_num_pages


class RundeckApi(object):
    '''
    This class provides multiple functions to manage projects, jobs or executions from
    Rundeck.

    To do it so, it uses Rundeck API endpoints, but also a connector to Rundeck database
    and complements deleting executions' data from workflow tables.
    '''

    def __init__(self, url, headers, db_conn, log, chunk_size=200, keep_time='30d', ssl=False, search_time=60, del_time=300):
        '''Initialization of global variables'''
        self._url = url
        self._headers = headers
        self._db = db_conn
        self._log = log
        self._chunk_size = chunk_size
        self._keep_time = keep_time
        self._check_ssl = ssl
        self._search_time = search_time
        self._del_time = del_time

    def __get(self, endpoint, parameters=''):
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

    def __post(self, endpoint, parameters=''):
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

    def __delete_executions_data(self, identifier, executions, page, retries=5, backoff=5, unoptimized=False):
        '''Private function to delete both executions and workflows'''
        n_retries = 0
        interval = [page * self._chunk_size, page * self._chunk_size + len(executions)]
        msg = '[{0}]: Deleting range {1} to {2}'.format(identifier, interval[0], interval[1])
        self._log.write(msg)

        for _ in range(0, retries):
            n_retries += 1
            workflows, steps, err_wf = self.get_workflow_ids(executions)

            if not workflows or not steps:
                return False, err_wf

            msg = '[{0}] Removing following executions -> {1}'.format(identifier, executions)
            self._log.write(msg, 1)
            msg = '[{0}] Removing following workflows -> {1}'.format(identifier, workflows)
            self._log.write(msg, 1)
            msg = '[{0}] Removing following workflow steps -> {1}'.format(identifier, steps)
            self._log.write(msg, 1)

            status_exec, _ = self.delete_executions(executions)
            status_wf, _ = self.delete_workflows(workflows, steps, unoptimized)

            if status_exec and status_wf:
                break
            elif not (status_exec or status_wf) and n_retries <= retries:
                sleep(backoff)
                msg = '[{0}] #{1} try not succeeded. Trying again in {2} seconds.'.format(identifier, retries, backoff)
                self._log.write(msg, 1)
                continue
            else:
                msg = '[{0}]: Error deleting executions.'.format(identifier)
                return False, msg

        return True, ''

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
                if appender:
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

        status, response = self.__get(endpoint)

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
            data = 'Error parsing JSON response.'

        return status, data

    def get_jobs_by_project(self, project_name, only_ids=True):
        '''Retrieve info about all jobs by project'''
        endpoint = '{0}/project/{1}/jobs'.format(self._url, project_name)
        status = False
        data = ''

        status, response = self.__get(endpoint)

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
            data = 'Error parsing JSON response.'

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
            endpoint = '{0}/running'.format(endpoint)

        status, response = self.__get(endpoint, parameters)

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
            data = 'Error parsing JSON response.'

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

        status, response = self.__get(endpoint, parameters)

        if status:
            status = True
            data = self.parse_json_response(response, 'paging', 'total')
        else:
            status = False
            data = response if response else 'Error parsing JSON response.'

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
            workflow_ids = '{0},{1}'.format(workflow_ids, str(workflow_id[0]))

        workflow_ids = workflow_ids.strip(',')

        # Return workflow step IDs
        if workflow_ids:
            workflow_step_stmt = 'SELECT workflow_step_id FROM workflow_workflow_step WHERE workflow_commands_id IN ({0})'.format(
                workflow_ids)
            query_res = self._db.query(workflow_step_stmt)

            for workflow_step_id in query_res:
                workflow_step_ids = '{0},{1}'.format(workflow_step_ids, str(workflow_step_id[0]))

            workflow_step_ids = workflow_step_ids.strip(',')

        self._db.close()

        return workflow_ids, workflow_step_ids, ''

    def get_inconsistent_data(self, unoptimized=False):
        '''Return all inconsistent data from workflow and related tables'''
        self._db.open()

        workflow_ids = ''
        workflow_step_ids = ''
        w_workflow_step_ids = ''

        workflow_stmt = '''
            SELECT id
            FROM workflow
            WHERE
                id < (
                    SELECT MIN(workflow_id)
                    FROM execution
                )
            AND
                id NOT IN (
                    SELECT workflow_id
                    FROM scheduled_execution
                )
        '''

        query_res = self._db.query(workflow_stmt)

        for workflow_id in query_res:
            workflow_ids = '{0},{1}'.format(workflow_ids, str(workflow_id[0]))

        workflow_ids = workflow_ids.strip(',')

        workflow_step_stmt = '''
            SELECT id
            FROM workflow_step
            WHERE id IN (
                SELECT workflow_step_id
                FROM workflow_workflow_step
                WHERE
                    workflow_commands_id < (
                        SELECT MIN(workflow_id)
                        FROM execution
                    )
                AND
                    workflow_commands_id NOT IN (
                        SELECT workflow_id
                        FROM scheduled_execution
                    )
            )
        '''

        query_res = self._db.query(workflow_step_stmt)

        for workflow_step_id in query_res:
            workflow_step_ids = '{0},{1}'.format(workflow_step_ids, str(workflow_step_id[0]))

        workflow_step_ids = workflow_step_ids.strip(',')

        w_workflow_step_stmt = '''
            SELECT workflow_commands_id
            FROM workflow_workflow_step
            WHERE
                workflow_commands_id < (
                    SELECT MIN(workflow_id)
                    FROM execution
                )
            AND
                workflow_commands_id NOT IN (
                    SELECT workflow_id
                    FROM scheduled_execution
                )
        '''

        query_res = self._db.query(w_workflow_step_stmt)

        if unoptimized:
            for w_workflow_step_id in query_res:
                w_workflow_step_ids = '{0},{1}'.format(w_workflow_step_ids, str(w_workflow_step_id[0]))

            w_workflow_step_ids = w_workflow_step_ids.strip(',')

        return workflow_ids, workflow_step_ids, w_workflow_step_ids


    def delete_executions(self, executions_ids):
        '''Bulk deletions of Rundeck executions'''

        endpoint = '{0}/executions/delete'.format(self._url)
        data = dumps(executions_ids)
        status = False
        msg = ''

        status, response = self.__post(endpoint, data)

        if status:
            all_succeeded = self.parse_json_response(response, 'allsuccessful')
            if all_succeeded:
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

    def delete_inconsistent_data(self, workflow_ids, workflow_step_ids, w_workflow_step_ids, unoptimized=False):
        '''Deletion of inconsistent data from workflow and related tables'''
        self._db.open()

        if w_workflow_step_ids and unoptimized:
            work_workflow_delete = 'DELETE FROM workflow_workflow_step WHERE workflow_commands_id IN ({0})'.format(
                workflow_step_ids)
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

    def clean_project_executions(self, project, retries=5, backoff=5, unoptimized=False):
        '''Clean executions older than a given time by from a project'''
        status, total = self.get_total_executions(project, False)
        pages = 0

        if not status:
            msg = "[{0}]: Error returning executions counter.".format(project)
            return False, msg
        else:
            if total > 0:
                msg = "[{0}]: There are {1} executions to delete.".format(project, total)
                self._log.write(msg)
                pages = get_num_pages(total, self._chunk_size)
                msg = "Processing deleting in {0} cycles.".format(pages)
                self._log.write(msg)
            else:
                msg = "[{0}]: No available executions for deleting.".format(project)
                self._log.write(msg)

            for page in range(0, pages):
                status, executions = self.get_executions(project, page, False)

                if status:
                    success, msg = self.__delete_executions_data(project, executions, page, retries, backoff, unoptimized)

                    if not success:
                        return False, msg
                else:
                    msg = '[{0}]: Error getting executions.'.format(project)
                    return False, msg

            workflows, steps, w_steps = self.get_inconsistent_data(unoptimized)
            status, err_u_wf = self.delete_inconsistent_data(workflows, steps, w_steps, unoptimized)

            if not status:
                return False, err_u_wf

        return True, total

    def clean_job_executions(self, job, retries=5, backoff=5, unoptimized=False):
        '''...'''
        status, total = self.get_total_executions(job)
        pages = 0

        if not status:
            msg = "[{0}]: Error returning executions counter.".format(job)
            return False, msg
        else:
            if total > 0:
                msg = "[{0}]: There are {1} executions to delete.".format(job, total)
                self._log.write(msg)
                pages = get_num_pages(total, self._chunk_size)
                msg = "Processing deleting in {0} cycles.".format(pages)
                self._log.write(msg)
            else:
                msg = "[{0}]: No available executions for deleting.".format(job)
                self._log.write(msg)

            for page in range(0, pages):
                executions = self.get_executions(job, page)

                if status:
                    success, msg = self.__delete_executions_data(job, executions, page, retries, backoff, unoptimized)

                    if not success:
                        return False, msg
                else:
                    msg = '[{0}]: Error getting executions.'.format(job)
                    return False, msg

            workflows, steps, w_steps = self.get_inconsistent_data(unoptimized)
            msg = 'Deleting wxisting inconsistent data.'
            self._log.write(msg)
            status, err_u_wf = self.delete_inconsistent_data(workflows, steps, w_steps, unoptimized)

            if not status:
                return False, err_u_wf

        return True, total

    def clean_executions(self, project=None, project_order=True, retries=5, backoff=5, unoptimized=False):
        '''Clean all executions data older than a given time'''
        stats_total = 0
        project_filter = True if project else False

        if project_filter:
            projects = project
        else:
            status, projects = self.get_projects()

        if not status:
            return status, projects

        for proj in projects:
            if not project_filter or proj == project:
                if project_order:
                    status, data = self.clean_project_executions(proj, retries, backoff, unoptimized)
                else:
                    status, jobs = self.get_jobs_by_project(project)

                    if status:
                        for job in jobs:
                            status, data = self.clean_job_executions(job, retries, backoff, unoptimized)

                if not status:
                    self._log.write(data, 4)
                    return False
                else:
                    msg = '[{0}] statistics: {1} old executions deleted.'.format(proj, int(data))
                    self._log.write(msg)
                    stats_total += int(data)

        msg = 'Global statistics: {0} old executions deleted.'.format(stats_total)
        self._log.write(msg)

        return True, ''

    def list_executions(self, project=None, job=None, only_running=False):
        '''List executions by job/project'''
        status = True
        filter_job = True if job else False

        if not filter_job:
            if project:
                data = project
            else:
                status, data = self.get_projects()
        else:
            data = job

        if not status:
            return False, data

        for row in data:
            status, executions = self.get_executions(row, 0, False, False, only_running)

            if not status:
                err_msg = '[{0}] Error getting executions.'.format(row)
                return False, err_msg

            for ex in executions:
                if filter_job and ex['job']['name'] == job:
                    msg = '[{0}] - \'{1}\'  {2}'.format(ex['project'], ex['job']['name'], ex['status'])
                    self._log.write(msg)
                elif not filter_job:
                    msg = '[{0}] - \'{1}\' is {2}'.format(ex['project'], ex['job']['name'], ex['status'])
                    self._log.write(msg)

        return True, ''
