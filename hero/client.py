"""
"""

import time
import socket
import logging
import datetime
from botocore.exceptions import ClientError


from .api.task import Task, COMPLETE, CLAIMED, READY
from .auth import cognito
from .api import role, queue, task

from .config import config
from .aws import dynamodb
import uuid 

from multiprocessing import Process

from . import aws
from . import api

from . import __version__ 

log = logging.getLogger(__name__)

from .api.integrity import QueueDoesNotExits, QueueNotInDynamo, RetryAttemptsExceeded
from .api.integrity_check import integrity_check


class Hero:
    def __init__(self, queue=None, resource_name=None, worker_id=None, enable_task_engine=True):
        
        self._version = __version__
        self.aws_credentials = None
        self._project = config.get_project()
        self.enable_task_engine = enable_task_engine
        if enable_task_engine:
            self._queue_name = config.get_queue(queue)
            self._resource_name = config.get_resource_name(resource_name)
            self._worker_id = f"hero-{str(uuid.uuid4())}" if worker_id is None else worker_id
            self._queue_url = None
            self._queue_count = 0
            log.debug(f'Initializing HERO: {self._worker_id} {self._resource_name} {self._queue_name} {self._project}')
    
    @property
    def logged_in(self):
        if self.aws_credentials is not None:
            return True
        return False

    @property
    def queue_url(self):
        return self._queue_url
    
    def data_repo(self):
        return api.data_repo

    def login(self):
        
        if not self.logged_in:
          
            client_id, client_secret = config.get_client_credentials()
            scopes = ['hero-api/user', f'project/{self._project}']
            self.access_token = cognito.get_token(client_id=client_id, client_secret=client_secret, scopes=scopes)
            if self.enable_task_engine:
                self.aws_credentials = role.assume_role(self.access_token)
                # config.export_session_to_env(self.aws_credentials)
                self._session = aws.utils.get_session(self.aws_credentials)
                self._aws_expiration = datetime.datetime.fromisoformat(self.aws_credentials['Expiration'][:-1]).astimezone(datetime.timezone.utc)
            
                try:
                    self._queue_url = api.queue.get_queue_url(self._session, self._project, self._queue_name)
                    self._queue_count = 0
                except QueueDoesNotExits as e:
                    self._queue_url = None
                    log.debug(f'Queue {self._queue_name} not found, you need to create the queue first.')
                except QueueNotInDynamo as e:
                    self._queue_url = None
                    log.debug(f'Queue {self._queue_name} not found in Dynamo.  You need to create the queue first.')
                
        total_seconds = round((self._aws_expiration - datetime.datetime.now(datetime.timezone.utc)).total_seconds())
        if total_seconds % 60 == 0:
            log.debug(f"AWS session {self._worker_id} will expire in {str(datetime.timedelta(seconds=total_seconds))}")

    @integrity_check
    def clear_tasks(self):
        """
        Clears the queue of all messages by deleting queue
        """
        log.debug('clear_tasks')
        self._queue_url = api.queue.create_queue(self._session, self._project, self._queue_name)
        self._queue_count = 0
        
        api.queue.delete_other_queues(self._session, self._queue_url, self._project, self._queue_name, self._worker_id)
        api.queue.update_queue_url(self._session, self._queue_url, self._project, self._queue_name)
        self._queue_url = api.queue.get_queue_url(self._session, self._project, self._queue_name)
        log.debug(f"Queue {self._queue_name} cleared.  New queue url {self._queue_url} is ready")
    

    
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
        task_id = api.retry.Retry(attempts=10, sleep=1).retry(
            aws.dynamodb.put_item,
            self._session, 
            self._project, 
            task)
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
        task_ids = api.retry.Retry(attempts=10, sleep=1).retry(
            aws.dynamodb.put_items,
            self._session, 
            self._project, 
            tasks)
        return task_ids

    @integrity_check
    def pull_task(self, attempts=10, sleep="constant"):
        """
        Pulls a task from the queue. Returns None otherwise.  Run this as a process.
        """  
        # def retry(): 
        #     retries = 0
        #     while retries < attempts:
        #         try:
        #             result = task.pull_task_sqs_dynamo(self._session,
        #                                         self._project,
        #                                         self._resource_name, 
        #                                         self._worker_id, 
        #                                         num_tasks=1,
        #                                         queue_url=self.queue_url, 
        #                                         )
        #         except Exception as e:
        #             print("Exception -->", str(e))

        #         if result is None:
        #             retries += 1
                    
        #             if retries >= attempts:
        #                 raise RetryAttemptsExceeded()
                    
        #             if sleep == "linear":
        #                 time.sleep(retries)
        #             elif sleep == "exponential":
        #                 time.sleep(2**retries)
        #             elif sleep == "constant":
        #                 time.sleep(1)
        #         else:
        #             return result
        # raw_task = retry()

        raw_task = api.retry.Retry(attempts=attempts, sleep=sleep).retry(
            task.pull_task_sqs_dynamo,
            self._session, 
            self._project,
            self._resource_name, 
            self._worker_id, 
            num_tasks=1,
            queue_url=self.queue_url, 
        )
        
        if raw_task is None:
            return None
        self._queue_count += 1
        return self.create_task(raw_task[0])
       

    @integrity_check
    def pull_tasks(self, attempts=10, num_tasks=1, sleep="constant"):
        """
        Pulls tasks from the queue. Returns None otherwise.
        """
        # for AWS SQS, max num_tasks is 10
        num_tasks = min(10, num_tasks)
        raw_tasks = api.retry.Retry(attempts=attempts, sleep=sleep).retry(
            task.pull_task_sqs_dynamo,
            self._session, 
            self._project,
            self._resource_name, 
            self._worker_id, 
            num_tasks=num_tasks,
            queue_url=self.queue_url, 
        )
        results = [ self.create_task(raw_task) for raw_task in raw_tasks if raw_task is not None ]
        self._queue_count += len(results)
        return results
    
    def create_task(self, raw_task):
        if raw_task is None:
            return None
        del raw_task['id']
        del raw_task['queue']
        return Task(**raw_task)
        
    @integrity_check
    def update_task(self, task, results):
        """Updates a task in the queue"""
        # task.completed_resource_name = self._resource_name
        task.results = results
        task.status = COMPLETE
        log.debug(f"update_task: {task.task_id} {task.queue_name} {task.status}")
        api.retry.Retry(attempts=10, sleep=5).retry(
            dynamodb.update_item_results,
            self._session,
            self._project,
            task.task_id,
            task.queue_name,
            results=task.results,
        )
        # dynamodb.update_item_results(
        #     self._session, self._project, task.task_id, task.queue_name, results=task.results
        # )
        return task

    def wait(self, seconds):
        """A simple wrapper for time.sleep"""
        time.sleep(seconds)

    @integrity_check
    def get_task_status_count(self, status):
        return
        # return rds.get_jobs_status_count_by_queue_url(self._project, self._queue, status)

    @integrity_check 
    def map(self, items, sleep=5):
        return
        # task_ids = self.put_tasks(items)
        # # wait for tasks to be available
        # while True:
        #     results = rds.get_items_detail(task_ids)
        #     if len(results) == len(task_ids) and all([r["status"] == COMPLETE for r in results]):
        #         return results
        #     log.debug(f"map: {len(results)} {len(task_ids)}")
        #     time.sleep(sleep)

    @integrity_check 
    def wait_for_tasks(self, task_ids):
        return
        # while True:
        #     results = rds.get_items_detail(task_ids)
        #     log.debug(f"wait_for_tasks: {len(results)} {len(task_ids)}")
        #     # print(len(results))
        #     # print([r["status"] for r in results if r["status"] != COMPLETE ])
        #     # print([ r['job_description']['name'] for r in results if r["status"] != COMPLETE ])
        #     if len(results) == len(task_ids) and all([r["status"] == COMPLETE for r in results]):
        #         return results
        #     time.sleep(5)

