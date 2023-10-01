import time
import logging

log = logging.getLogger('hero:api:utils')
from ..integrity import RetryAttemptsExceeded

# class RetryAttemptsExceeded(Exception):
#     def __init__(self):
#         super().__init__('Failed due to number of retry attempts.')

class Retry:

    def __init__(self, attempts=10, sleep="linear"):
        self._attempts = attempts
        self._sleep = sleep

    def retry(self, retry_function, *args, **kwargs):
        retries = 0
        while retries < self._attempts:
            result = retry_function(*args, **kwargs)
            if result is None:
                retries += 1
                queue_url = kwargs.get("queue_url", "xxxxxx")
                if queue_url is None:
                    queue_url = "NoneNone"
                print(f"retries => {retries}    {queue_url[-6:]}")
                if retries >= self._attempts:
                    raise RetryAttemptsExceeded()
                if self._sleep == "linear":
                    time.sleep(retries)
                elif self._sleep == "exponential":
                    time.sleep(2**retries)
                elif self._sleep == "constant":
                    time.sleep(1)
            else:
                return result
        

# def retry_task(retry_function, project, queue_url, resource_name=None, worker_id=None, attempts=1, num_tasks=1):
#     retries = 0
#     while retries < attempts:
#         result = retry_function(project, queue_url, resource_name, worker_id, num_tasks=num_tasks)
#         # print('result', result)
#         if result is None:
#             retries += 1
#             if retries >= attempts:
#                 raise RetryAttemptsExceeded()
#             time.sleep(retries)
#         else:
#             return result