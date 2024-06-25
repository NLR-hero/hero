import json

from ...config import get_task_engine_api
from ...api import ApiBase

class TaskEngineApi(ApiBase):

    ACTIVE = "active"
    DELETED = "deleted"
    READY = "ready"
    CLAIMED = "claimed"
    DONE = "done"
    FAILED = "failed"

    def __init__(self, resilient_session=False):
        super().__init__(resilient_session)
        self.base_url = get_task_engine_api()

    def add_or_get_queue(self, token, task_engine_id, data):
        """
        Returns the active queue associated with a queue_name if it exists. If it doesn't
        exist, it creates a new queue and returns
        """
        url = f"{self.base_url}/{task_engine_id}/queue"
        response = self.session.request("POST", url, headers=self.get_headers(token), data=data)
        return response.json()


    def delete_queue(self, token, task_engine_id, queue_id):
        """
        Marks the queue as deleted
        """
        url = f"{self.base_url}/{task_engine_id}/queue/{queue_id}"
        response = self.session.request("DELETE", url, headers=self.get_headers(token))
        return response.json()


    def get_queues(self, token, task_engine_id, queue_name, state):
        """
        Returns a random set of `limit` queues of a given `state`
        """
        state = state or TaskEngineApi.ACTIVE
        assert state in [TaskEngineApi.ACTIVE, TaskEngineApi.DELETED]
        url = f"{self.base_url}/{task_engine_id}/queues/metatype/Queue"
        query_params = f"?name={queue_name}|{state}"
        url = url + query_params
        response = self.session.request("GET", url, headers=self.get_headers(token))
        return response.json()


    def get_active_queue(self, access_token, task_engine_id, queue_name):
        """
        There can only be one active queue for a given queue_name.  This returns
        that queue or None if an active queue doesn't exist.
        """
        queues = self.get_queues(access_token, task_engine_id, queue_name, state=TaskEngineApi.ACTIVE)
        for queue in queues:
            if queue["name"] == queue_name:
                tmp = {
                    "id": queue["id"],
                    "name": queue["name"],
                    "queueUrl": queue["queueUrl"],
                }
                return tmp

    def add_task(self, token, task_engine_id, queue_id, task):
        """
        Adds a task to the queue with queue_id
        """
        url = f"{self.base_url}/{task_engine_id}/task"

        # ensure the task has the following minimum fields
        task["queueId"] = queue_id
        task["metadata"] = task.get("metadata", {})
        task["inputs"] = task.get("inputs", {})
        assert "name" in task

        payload = json.dumps(task)
        response = self.session.request("POST", url, headers=self.get_headers(token), data=payload)
        return response.json()


    def pull_tasks(self,
        token, task_engine_id, queue_id, metatype="Task", messages=1, visibility_timeout=60
    ):
        """
        The API pulls a task from SQS, checks to ensure it has not been claimed,
        and returns the task.
        """
        url = f"{self.base_url}/{task_engine_id}/tasks"
        query_params = f"?receive={messages}"
        query_params += f"&visibilityTimeout={visibility_timeout}"
        query_params += f"&queueId={queue_id}"
        query_params += f"&metatype={metatype}"
        url = url + query_params
        response = self.session.request("GET", url, headers=self.get_headers(token))
        return response.json()


    def update_task(self, token, task_engine_id, task_id, task):
        """
        Updates the task status and results in dynamodb and steams to open search.
        """
        url = f"{self.base_url}/{task_engine_id}/task/{task_id}"

        # ensure it has the following fields
        task["state"] = task.get("state", TaskEngineApi.DONE)
        assert task["state"] in [TaskEngineApi.DONE, TaskEngineApi.READY, TaskEngineApi.CLAIMED, TaskEngineApi.FAILED]
        task["outputs"] = task.get("outputs", {})

        payload = json.dumps(task)
        response = self.session.request("POST", url, headers=self.get_headers(token), data=payload)
        return response.json()


    def get_tasks(self, token, task_engine_id, queue_id, state=READY):
        """ """
        url = f"{self.base_url}/{task_engine_id}/queue/{queue_id}/tasks"
        query_params = f"?metatype=Task&state={state}"
        url = url + query_params
        response = self.session.request("GET", url, headers=self.get_headers(token))
        return response.json()


    def get_ready_tasks(self, token, task_engine_id, queue_id):
        return self.get_tasks(token, task_engine_id, queue_id, state=TaskEngineApi.READY)


    def get_completed_tasks(self, token, task_engine_id, queue_id):
        return self.get_tasks(token, task_engine_id, queue_id, state=TaskEngineApi.DONE)