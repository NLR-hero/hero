import json

from ..url_map import URL_MAP
from ..lib import ServiceBase, decorate_all, log_errors, get_conf_from_collection

@decorate_all(log_errors)
class TaskEngineService(ServiceBase):

    def _configure(self):
        '''
        Sets the API, adds task engine id and required scope
        '''
        self.client.add_scope('task-engine/user')
        self.base_url = get_conf_from_collection(URL_MAP, 'HERO_TASK_ENGINE_API_URL')


    # export async function getQueues(setData, user, taskEngineId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${taskEngineId}/queues`, {
    #         headers: requestHeaders,
    #         params: {
    #             metatype: 'Queue',
    #             state: 'active'
    #         }
    #     });
    #     setData(response.data);
    # }
    def get_queues(self, task_engine_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{task_engine_id}/queues'
        params = json.dumps({
            'metatype': 'Queue',
            'state': 'active'
        })
        response = self.api.request('GET', url, headers, params=params)
        return response.json()

    # export async function getQueue(setData, user, taskEngineId, queueId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${taskEngineId}/queue/${queueId}`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    def get_queue(self, task_engine_id, queue_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{task_engine_id}/queue/{queue_id}'
        response = self.api.request('GET', url, headers)
        return response.json()

    # export async function deleteQueue(user, taskEngineId, queueId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.delete(`${taskEngineId}/queue/${queueId}`, {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def delete_queue(self, task_engine_id, queue_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{task_engine_id}/queue/{queue_id}'
        response = self.api.request('DELETE', url, headers)
        return response.json()

    # export async function addQueue(user, taskEngineId, attributes) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.post(`${taskEngineId}/queue`,
    #     attributes,
    #     {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def add_queue(self, task_engine_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{task_engine_id}/queue'
        data = json.dumps(attributes)
        response = self.api.request('POST', url, headers=headers, data=data)
        return response.json()

    # export async function updateQueue(user, taskEngineId, queueId, attributes) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.post(`${taskEngineId}/queue/${queueId}`,
    #     attributes,
    #     {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def update_queue(self, task_engine_id, queue_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{task_engine_id}/queue/{queue_id}'
        data = json.dumps(attributes)
        response = self.api.request('POST', url, headers=headers, data=data)
        return response.json()


    # export async function getTasks(setData, user, taskEngineId, queueId, metatype, state) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${taskEngineId}/queue/${queueId}/tasks`, {
    #         headers: requestHeaders,
    #         params: {
    #             metatype,
    #             state
    #         }
    #     });
    #     setData(response.data);
    # }
    def get_tasks(self, task_engine_id, queue_id, metatype, state):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{task_engine_id}/queue/{queue_id}/tasks'
        params = json.dumps({
            'metatype': metatype,
            'state': state
        })
        response = self.api.request('GET', url, headers=headers, params=params)
        return response.json()

    # export async function getTask(setData, user, taskEngineId, taskId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${taskEngineId}/task/${taskId}`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    def get_task(self, task_engine_id, task_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{task_engine_id}/task/{task_id}'
        response = self.api.request('GET', url, headers)
        return response.json()

    # export async function deleteTask(user, taskEngineId, taskId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.delete(`${taskEngineId}/task/${taskId}`, {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def delete_task(self, task_engine_id, task_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{task_engine_id}/task/{task_id}'
        response = self.api.request('DELETE', url, headers)
        return response.json()

    # export async function addTask(user, taskEngineId, attributes) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.post(`${taskEngineId}/task`,
    #     attributes,
    #     {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def add_task(self, task_engine_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{task_engine_id}/task'
        data = json.dumps(attributes)
        response = self.api.request('POST', url, headers=headers, data=data)
        return response.json()

    # export async function updateTask(user, taskEngineId, taskId, attributes) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.post(`${taskEngineId}/task/${taskId}`,
    #     attributes,
    #     {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def update_task(self, task_engine_id, task_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{task_engine_id}/task/{task_id}'
        data = json.dumps(attributes)
        response = self.api.request('POST', url, headers=headers, data=data)
        return response.json()

