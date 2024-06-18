from . import queue_api as queue_api
from . import task_api as task_api
from ..config import get_client_credentials, get_task_engine_id, get_task_engine_scopes
from ..auth.cognito import get_token
import time
import requests

from .errors import retry_method, DEFAULT_ATTEMPTS, DEFAULT_WAIT
from .. import errors


class Queue:

    def __init__(self, queue):
        self._id = queue["id"]
        self._queue = queue

    @property
    def queue_id(self):
        return self._id


class TaskEngine:

    def __init__(self, queue_name: str):
        self._queue_name = queue_name
        self._login()
        self._queue = None

    def _login(self):
        """This method should not have a @robust decorator"""
        self._task_engine_id = get_task_engine_id()
        self._scopes = get_task_engine_scopes()
        client_id, client_secret = get_client_credentials()
        self._client_id = client_id
        self._client_secret = client_secret
        self._token = get_token(
            client_id=self._client_id,
            client_secret=self._client_secret,
            scopes=self._scopes,
        )

    def _get_active_queue(self):
        """Private method should not have a @robust decorator"""
        queue = queue_api.get_active_queue(
            self._token, self._task_engine_id, self._queue_name
        )
        if queue is not None:
            self._queue = Queue(queue)
            return self._queue

        raise errors.ClientQueueNotActive(
            f"{self._queue_name} queue not active in DynamoDB"
        )

    """ Public method """

    @property
    @retry_method
    def queue_id(self):
        if self._queue is None or not isinstance(self._queue, Queue):
            self._get_active_queue()
        return self._queue.queue_id

    @retry_method
    def clear_queue(self):
        self._queue = self.add_or_get_queue()
        self.delete_queue()
        self._queue = self.add_or_get_queue()

    @retry_method
    def add_or_get_queue(self):
        queue = queue_api.add_or_get_queue(
            self._token, self._task_engine_id, self._queue_name
        )
        if queue is not None:
            self._queue = Queue(queue)
            return self._queue
        raise errors.ClientRetry(
            f"add_or_get_queue returned none for {self._queue_name}"
        )

    @retry_method
    def delete_queue(self):
        response = queue_api.delete_queue(
            self._token, self._task_engine_id, self.queue_id
        )
        self._queue = None

    # ==========================================================================
    #       Work on active queues only
    # ==========================================================================

    def raise_error_if_queue_is_not_active(self):
        tmp = queue_api.get_active_queue(
            self._token, self._task_engine_id, self._queue_name
        )
        if tmp is None or tmp.get("id") != self.queue_id:
            raise errors.ClientQueueNotActive(f"{self._queue_name} queue is not active")

    @retry_method
    def estimate_ready_tasks(self):
        # TODO raise error on the API if self._queue isn't active
        self.raise_error_if_queue_is_not_active()

        tasks = task_api.get_ready_tasks(
            self._token, self._task_engine_id, self.queue_id
        )
        if tasks is not None:
            return len(tasks)

        raise errors.ClientReadyTaskEstimate(
            f"No ready tasks results for {self._queue_name}"
        )

    @retry_method
    def pull_tasks(self, messages=1, metatype='Task', attempts=DEFAULT_ATTEMPTS, wait=DEFAULT_WAIT):
        self.raise_error_if_queue_is_not_active()

        tasks = task_api.pull_tasks(
            self._token, self._task_engine_id, self.queue_id, messages=messages, metatype=metatype
        )
        if len(tasks) > 0:
            return tasks
        raise errors.ClientPullTasksEmpty(f"Pull task failed for {self._queue_name}")

    @retry_method
    def put_tasks(self, tasks: list, attempts=DEFAULT_ATTEMPTS, wait=DEFAULT_WAIT):
        self.raise_error_if_queue_is_not_active()
        for task in tasks:
            task_api.add_task(
                self._token,
                self._task_engine_id,
                self.queue_id,
                {
                    "name": task.get("name", "No name specified"),
                    "metadata": task.get("metadata", {}),
                    "inputs": task.get("inputs", task),
                },
            )

    # ==========================================================================
    #       Maybe work on active or deleted?
    # ==========================================================================

    # @retry_method
    def update_task(
        self, task, results={}, attempts=DEFAULT_ATTEMPTS, wait=DEFAULT_WAIT
    ):
        res = task_api.update_task(
            self._token,
            self._task_engine_id,
            task["id"],
            {
                "state": task_api.DONE,
                "outputs": results,
            },
        )
        return res

    @retry_method
    def completed_tasks(self, attempts=DEFAULT_ATTEMPTS, wait=DEFAULT_WAIT):
        tasks = task_api.get_completed_tasks(
            self._token, self._task_engine_id, self.queue_id
        )
        return tasks
