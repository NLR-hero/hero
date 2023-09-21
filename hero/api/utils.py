import time
import logging

log = logging.getLogger('hero:api:utils')

class RetryAttemptsExceeded(Exception):
    def __init__(self):
        super().__init__('Failed due to number of retry attempts.')

def retry(retry_function, project, queue_url, resource_name=None, attempts=1):
    retries = 0
    while retries < attempts:
        result = retry_function(project, queue_url, resource_name)
        # print('result', result)
        if result is None:
            retries += 1
            if retries >= attempts:
                raise RetryAttemptsExceeded()
            time.sleep(retries)
        else:
            return result
        
def retry_task(retry_function, project, queue_url, resource_name=None, worker_id=None, attempts=1, num_tasks=1):
    retries = 0
    while retries < attempts:
        result = retry_function(project, queue_url, resource_name, worker_id, num_tasks=num_tasks)
        # print('result', result)
        if result is None:
            retries += 1
            if retries >= attempts:
                raise RetryAttemptsExceeded()
            time.sleep(retries)
        else:
            return result