from . import task_engine_queue_api as queue_api
from . import task_engine_task_api as task_api
from ..config import get_client_credentials, get_task_engine_id, get_task_engine_scopes
from ..auth.cognito import get_token
import time
import requests

# from ..errors import UnauthorizedException, NoActiveException

from .. import errors


def required(func):
    def wrapper(self, *args, **kwargs):
        try:
            if self._queue_id is None:
                self.get_active_queue()
            return func(self, *args, **kwargs)
        except errors.UnauthorizedException as e:
            self.login()
            return func(self, *args, **kwargs)

    return wrapper


class TaskEngine:

    def __init__(self, queue_name: str):
        self._queue_name = queue_name
        self.login()
        self._queue_id = None

    def login(self):
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

    @required
    def clear_queue(self):
        queue = queue_api.add_or_get_queue(
            self._token, self._task_engine_id, self._queue_name
        )
        queue_api.delete_queue(self._token, self._task_engine_id, queue["id"])
        self._queue = queue_api.add_or_get_queue(
            self._token, self._task_engine_id, self._queue_name
        )
        self._queue_id = self._queue["id"]

    def get_active_queue(self, retry=3):
        for i in range(retry):
            self._queue = queue_api.get_active_queue(
                self._token, self._task_engine_id, self._queue_name
            )
            if self._queue is not None:
                self._queue_id = self._queue["id"]
                return self._queue
            time.sleep(1)
        raise errors.NoActiveException(f"Used {retry} reties")

    @required
    def put_tasks(self, tasks: list):
        for task in tasks:
            task_api.add_task(
                self._token,
                self._task_engine_id,
                self._queue_id,
                {
                    "name": f"test-task-{task['id']}",
                    "metadata": {},
                    "inputs": task,
                },
            )

    @required
    def pull_tasks(self, messages=1, attempts=10):

        # Try attempts time
        attempt = 0
        while attempt < attempts:
            tasks = task_api.pull_tasks(
                self._token, self._task_engine_id, self._queue_id, messages=messages
            )
            if len(tasks) > 0:
                return tasks
            attempt += 1
            time.sleep(1)

        #

    @required
    def update_task(self, task, results={}):
        task = task_api.update_task(
            self._token,
            self._task_engine_id,
            task["id"],
            {
                "state": task_api.DONE,
                "outputs": results,
            },
        )
        return task

    @required
    def estimate_ready_tasks(self):
        tasks = task_api.get_ready_tasks(
            self._token, self._task_engine_id, self._queue_id
        )
        return len(tasks)
