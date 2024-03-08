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
            # if self._queue_id is None:
            #     self.get_active_queue()
            return func(self, *args, **kwargs)

        # We can only catch and handel errors thrown by resilient_session

        # Unauthorized: login and try again
        except errors.UnauthorizedException as e:
            self.login()
            return func(self, *args, **kwargs)

        # we have the wrong queue_id
        except errors.ItemNotFoundException as e:
            self.get_active_queue()
            return func(self, *args, **kwargs)

        # Queue does not exists.  Sleep and try again.
        except errors.QueueDoesNotExistException as e:
            self.get_active_queue()
            return func(self, *args, **kwargs)

        # Explicitly pass these to the client
        # Queue is not active.
        except errors.QueueNotActiveException as e:
            raise

        # pass this to the client
        except errors.QueueEmptyException as e:
            raise

        except Exception as e:
            print("Need to handel this exception", str(e))

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

    @property
    @required
    def queue_id(self):
        if self._queue_id is None:
            self.get_active_queue()
        return self._queue_id

    @required
    def delete_queue(self):
        queue_api.delete_queue(self._token, self._task_engine_id, self.queue_id)

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

    @required
    def get_active_queue(self, attempts=3):
        tic = time.time()
        for i in range(attempts):
            self._queue = queue_api.get_active_queue(
                self._token, self._task_engine_id, self._queue_name
            )
            if self._queue is not None:
                self._queue_id = self._queue["id"]
                return self._queue
            time.sleep(i + 1)
        toc = time.time()
        raise errors.QueueNotActiveException(
            f"QueueNotActiveException: No active queue found after {attempts} attempts"
            + f" and {round(toc-tic, 2)} seconds.  Consider raising the number of attempts."
        )

    @required
    def put_tasks(self, tasks: list):
        for task in tasks:
            task_api.add_task(
                self._token,
                self._task_engine_id,
                self.queue_id,
                {
                    "name": f"test-task-{task['id']}",
                    "metadata": {},
                    "inputs": task,
                },
            )

    @required
    def pull_tasks(self, messages=1, attempts=10):

        attempt = 0
        tic = time.time()
        while attempt < attempts:

            try:
                tasks = task_api.pull_tasks(
                    self._token, self._task_engine_id, self.queue_id, messages=messages
                )
                if len(tasks) > 0:
                    return tasks
                attempt += 1
                time.sleep(1)

            except errors.QueueNotActiveException as e:
                attempt += 1
                print("errors.QueueNotActiveException")
                time.sleep(1)

        toc = time.time()
        print(
            f"Worker: no messages after {attempt} attempts and {round(toc-tic, 2)} seconds."
        )

        # If we still failed, check to see if the queue is empty
        if self.estimate_ready_tasks() == 0:
            raise errors.QueueEmptyException(
                f"QueueEmptyException: The queue you are using is empty"
            )

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
        if tasks is None:
            return 0
        return len(tasks)

    @required
    def completed_tasks(self):
        tasks = task_api.get_completed_tasks(
            self._token, self._task_engine_id, self._queue_id
        )
        return tasks
