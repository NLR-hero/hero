"""
"""

import time
import socket
import logging
import datetime
from botocore.exceptions import ClientError

from .api.task import Task, COMPLETE, CLAIMED, READY
from .auth import cognito
from .api import role, queue, task, QueueDoesNotExits
from .api import queue as sqsqueue
from .api.utils import RetryAttemptsExceeded
from .config import config
from .aws import dynamodb, rds
from .aws.utils import get_session
import uuid 

from . import aws
from . import api

from . import __version__ 

log = logging.getLogger("hero:hero")

def integrity_check(func):
    def wrapper(self, *args, **kwargs):
        try:
            self.login()
            return func(self, *args, **kwargs)
        except ClientError as e:
            print("ClientError", e.response["Error"]["Code"])
            if e.response["Error"]["Code"] == "ExpiredTokenException":
                print("token expired, getting new token")
                self.aws_credentials = None
                self.login()
                return func(self, *args, **kwargs)
            if e.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
                time.sleep(1)
                try:
                    self._queue_url = api.queue.get_queue_url(self._session, self._project, self._queue_name)
                    self._queue_count = 0
                    print("new queue url", self._queue_url)
                    return func(self, *args, **kwargs)
                except QueueDoesNotExits as e:
                    print("QueueDoesNotExits")
                    return None 
        except RetryAttemptsExceeded as e:
            try:
                self._queue_url = api.queue.get_queue_url(self._session, self._project, self._queue_name)
                self._queue_count = 0
                print(f"RetryAttemptsExceeded: using queue ending in {self._queue_url[-10:]}")
                return None
            except QueueDoesNotExits as e:
                    print("QueueDoesNotExits")
                    return None 
        except QueueDoesNotExits as e:
            print("QueueDoesNotExits")
            return None
    return wrapper



class Hero:
    def __init__(self, queue=None, resource_name=None):
        
        self._version = __version__
        self.aws_credentials = None
        self._project = config.get_project()
        self._queue_name = config.get_queue(queue)
        self._resource_name = config.get_resource_name(resource_name)
        self._worker_id = f"hero-{str(uuid.uuid4())}"
        self._queue_url = None
        self._queue_count = 0
        log.info(f'Initializing HERO {self._version}: {self._resource_name} {self._queue_name} {self._project}')
    
    @property
    def logged_in(self):
        if self.aws_credentials is not None:
            return True
        return False

    @property
    def queue_url(self):
        return self._queue_url

    def login(self):
        
        if not self.logged_in:
          
            client_id, client_secret = config.get_client_credentials()
            scopes = ['hero-api/user', f'project/{self._project}']
            self.access_token = cognito.get_token(client_id=client_id, client_secret=client_secret, scopes=scopes)
            self.aws_credentials = role.assume_role(self.access_token)
            # config.export_session_to_env(self.aws_credentials)
            self._session = aws.utils.get_session(self.aws_credentials)
            self._aws_expiration = datetime.datetime.fromisoformat(self.aws_credentials['Expiration'][:-1]).astimezone(datetime.timezone.utc)
            
            try:
                self._queue_url = api.queue.get_queue_url(self._session, self._project, self._queue_name)
                self._queue_count = 0
            except QueueDoesNotExits as e:
                self._queue_url = None
                print('Queue not found, you need to create the queue first.')

        print("expiration = ", (self._aws_expiration - datetime.datetime.now(datetime.timezone.utc)).total_seconds()) 


    @integrity_check
    def clear_tasks(self):
        """
        Clears the queue of all messages by deleting queue
        """
        log.debug('clear_tasks')
        self._queue_url = api.queue.create_queue(self._session, self._project, self._queue_name)
        self._queue_count = 0
        
        api.queue.delete_other_queues(self._session, self._queue_url, self._project, self._queue_name)
        api.queue.update_queue_url(self._session, self._queue_url, self._project, self._queue_name)
        self._queue_url = api.queue.get_queue_url(self._session, self._project, self._queue_name)
        print(f"Queue {self._queue_name} cleared.  New queue url {self._queue_url} is ready")

    
    @property
    def resource_name(self):
        return self._resource_name

    @property
    def count(self):
        return self._queue_count

    @property
    @integrity_check
    def queue_url(self):
        if self._queue_url is None:
            self._queue_url = api.queue.get_queue_url(self._session, self._project, self._queue_name)
            self._queue_count = 0
        return self._queue_url


    @integrity_check
    def put_task(self, item):
        task = Task(
            project=self._project,
            queue_name=self._queue_name,
            queue_url=self.queue_url,
            inputs=item,
            status=READY,
            insert_resource_name=self._resource_name,
            insert_worker_id=self._worker_id,
        )
        task_id = aws.dynamodb.put_item(self._session, self._project, task)
        return task_id

    @integrity_check
    def put_tasks(self, items):
        tasks = [
            Task(
                project=self._project,
                queue_name=self._queue_name,
                queue_url=self.queue_url,
                inputs=i,
                status=READY,
                insert_resource_name=self._resource_name,
                insert_worker_id=self._worker_id,
            )
            for i in items
        ]
        task_ids = aws.dynamodb.put_items(self._session, self._project, tasks)
        return task_ids

    @integrity_check
    def pull_task(self, attempts=10):
        """
        Pulls a task from the queue. Returns None otherwise.
        """   
        raw_task = api.utils.Retry(attempts=attempts).retry(
            task.pull_task_sqs_dynamo,
            self._session, 
            self._project,
            self.queue_url, 
            self._resource_name, 
            self._worker_id, 
            num_tasks=1
        )

        # raw_task = self.poll(attempts, num_tasks=1)
        if raw_task is None:
            return None
        self._queue_count += 1
        return self.create_task(raw_task[0])
       

    @integrity_check
    def pull_tasks(self, attempts=10, num_tasks=1):
        """
        Pulls tasks from the queue. Returns None otherwise.
        """
        # for AWS SQS, max num_tasks is 10
        num_tasks = min(10, num_tasks)
        raw_tasks = api.utils.Retry(attempts=attempts).retry(
            task.pull_task_sqs_dynamo,
            self._session, 
            self._project,
            self.queue_url, 
            self._resource_name, 
            self._worker_id, 
            num_tasks=num_tasks
        )
        results = [ self.create_task(raw_task) for raw_task in raw_tasks if raw_task is not None ]
        self._queue_count += len(results)
        return results
    
    def create_task(self, raw_task):
        if raw_task is None:
            return None
        # Do we need this?
        # raw_task['task_id'] = raw_task['id']
        # raw_task['queue_name'] = raw_task['queue']
        del raw_task['id']
        del raw_task['queue']
        return Task(**raw_task)
        
    @integrity_check
    def update_task(self, task, results):
        """Updates a task in the queue"""
        # task.completed_resource_name = self._resource_name
        task.results = results
        task.status = COMPLETE
        dynamodb.update_item_results(
            self._session, self._project, task.task_id, task.queue_name, results=task.results
        )
        return task

    def wait(self, seconds):
        """A simple wrapper for time.sleep"""
        time.sleep(seconds)

    @integrity_check
    def get_task_status_count(self, status):
        return rds.get_jobs_status_count_by_queue_url(self._project, self._queue, status)

    @integrity_check 
    def map(self, items, sleep=5):
        task_ids = self.put_tasks(items)
        # wait for tasks to be available
        while True:
            results = rds.get_items_detail(task_ids)
            if len(results) == len(task_ids) and all([r["status"] == COMPLETE for r in results]):
                return results
            time.sleep(sleep)

    @integrity_check 
    def wait_for_tasks(self, task_ids):
        while True:
            results = rds.get_items_detail(task_ids)
            print(len(results))
            print([r["status"] for r in results if r["status"] != COMPLETE ])
            print([ r['job_description']['name'] for r in results if r["status"] != COMPLETE ])
            if len(results) == len(task_ids) and all([r["status"] == COMPLETE for r in results]):
                return results
            time.sleep(5)

