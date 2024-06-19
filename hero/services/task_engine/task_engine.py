import json

from ...service import ServiceBase
from ... import errors

from .queue import Queue
from .task_engine_api import TaskEngineApi
from .queue_api import QueueApi
from .task_api import TaskApi

from ...config import get_task_engine_id, get_task_engine_scopes

class TaskEngine(ServiceBase):

    def __init__(self, queue_name):
        self._queue_name = queue_name
        self._queue = None
        super().__init__()

    def _configure(self):
        self.api = TaskEngineApi()
        self.queue_api = QueueApi()
        self.task_api = TaskApi()
        self._task_engine_id = get_task_engine_id()
        self._scopes = get_task_engine_scopes()

    def _get_active_queue(self):
        """Private method should not have a @robust decorator"""
        queue = self.queue_api.get_active_queue(
            self._access_token,
            self._task_engine_id,
            self._queue_name
        )
        if queue is not None:
            self._queue = Queue(queue)
            return self._queue

        raise errors.ClientQueueNotActive(
            f"{self._queue_name} queue not active in DynamoDB"
        )

    """ Public method """

    @property
    def queue_id(self):
        if self._queue is None or not isinstance(self._queue, Queue):
            self._get_active_queue()
        return self._queue.queue_id

    def clear_queue(self):
        self._queue = self.add_or_get_queue()
        self.delete_queue()
        self._queue = self.add_or_get_queue()

    def add_or_get_queue(self):
        attributes = {"name": self._queue_name}
        queue = self.queue_api.add_or_get_queue(
            self._access_token,
            self._task_engine_id,
            json.dumps(attributes)
        )
        if queue is not None:
            self._queue = Queue(queue)
            return self._queue
        raise errors.ClientRetry(
            f"add_or_get_queue returned none for {self._queue_name}"
        )

    def delete_queue(self):
        response = self.queue_api.delete_queue(
            self._access_token,
            self._task_engine_id,
            self.queue_id
        )
        self._queue = None

    # ==========================================================================
    #       Work on active queues only
    # ==========================================================================

    def _raise_error_if_queue_is_not_active(self):
        tmp = self.queue_api.get_active_queue(
            self._access_token,
            self._task_engine_id,
            self._queue_name
        )
        if tmp is None or tmp.get("id") != self.queue_id:
            raise errors.ClientQueueNotActive(f"{self._queue_name} queue is not active")

    def estimate_ready_tasks(self):
        # TODO raise error on the API if self._queue isn't active
        self._raise_error_if_queue_is_not_active()

        tasks = self.task_api.get_ready_tasks(
            self._access_token, self._task_engine_id, self.queue_id
        )
        if tasks is not None:
            return len(tasks)

        raise errors.ClientReadyTaskEstimate(
            f"No ready tasks results for {self._queue_name}"
        )

    def pull_tasks(self, messages=1, metatype='Task'):
        self._raise_error_if_queue_is_not_active()

        tasks = self.task_api.pull_tasks(
            self._access_token, self._task_engine_id, self.queue_id, messages=messages, metatype=metatype
        )
        if len(tasks) > 0:
            return tasks
        raise errors.ClientPullTasksEmpty(f"Pull task failed for {self._queue_name}")

    def put_tasks(self, tasks: list):
        self._raise_error_if_queue_is_not_active()
        for task in tasks:
            self.task_api.add_task(
                self._access_token,
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

    def update_task( self, task, results={}):
        res = self.task_api.update_task(
            self._access_token,
            self._task_engine_id,
            task["id"],
            {
                "state": self.task_api.DONE,
                "outputs": results,
            },
        )
        return res

    def completed_tasks(self):
        tasks = self.task_api.get_completed_tasks(
            self._access_token, self._task_engine_id, self.queue_id
        )
        return tasks
