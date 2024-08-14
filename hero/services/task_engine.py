import json

from ..url_map import URL_MAP
from ..lib import ServiceBase, decorate_all, log_errors, get_conf_from_collection, HeroRetryError

# @decorate_all(log_errors)
class TaskEngineService(ServiceBase):

    def _configure(self):
        '''
        Sets the API, adds task engine id and required scope
        '''
        self.task_engine_id = self.application_id
        self.client.add_scope('task-engine/user')
        self.base_url = get_conf_from_collection(URL_MAP, 'HERO_TASK_ENGINE_API_URL')

    def read_queues(self):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.task_engine_id}/queues'
        params = {
            'metatype': 'Queue',
            'state': 'active'
        }
        response = self.api.request('GET', url, headers=headers, params=params)
        return response.json()

    def read_queue(self, queue_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.task_engine_id}/queue/{queue_id}'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    def delete_queue(self, queue_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.task_engine_id}/queue/{queue_id}'
        response = self.api.request('DELETE', url, headers=headers)
        return response.json()

    def add_queue(self, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.task_engine_id}/queue'
        data = json.dumps(attributes)
        response = self.api.request('POST', url, headers=headers, data=data)
        return response.json()

    def update_queue(self, queue_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.task_engine_id}/queue/{queue_id}'
        data = json.dumps(attributes)
        response = self.api.request('POST', url, headers=headers, data=data)
        return response.json()

    def read_tasks(self, queue_id, metatype, state):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.task_engine_id}/queue/{queue_id}/tasks'
        params = {
            'metatype': metatype,
            'state': state
        }
        response = self.api.request('GET', url, headers=headers, params=params)
        return response.json()

    def read_task(self, task_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.task_engine_id}/task/{task_id}'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    def delete_task(self, task_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.task_engine_id}/task/{task_id}'
        response = self.api.request('DELETE', url, headers=headers)
        return response.json()

    def add_task(self, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.task_engine_id}/task'
        data = json.dumps(attributes)
        response = self.api.request('POST', url, headers=headers, data=data)
        return response.json()

    def update_task(self, task_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.task_engine_id}/task/{task_id}'
        data = json.dumps(attributes)
        response = self.api.request('POST', url, headers=headers, data=data)
        return response.json()

