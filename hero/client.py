"""
"""

import time
import socket
import logging
from botocore.exceptions import ClientError

from .api.task import Task, COMPLETE, CLAIMED, READY
from .auth import cognito
from .api import role, queue, task
from .api.utils import RetryAttemptsExceeded, retry, retry_task
from .config import config
from .aws import dynamodb, rds
from .aws.utils import get_session

log = logging.getLogger("hero:hero")

def required_login(func):
    def wrapper(self, *args, **kwargs):
        self.login()
        return func(self, *args, **kwargs)
    return wrapper

def pull_execptions(func):
    def wrapper(self, *args, **kwargs):
        try:
            self.login()
            return func(self, *args, **kwargs)
        except ClientError as e:
            if e.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
                print("queue does not exist, getting new queue")
                time.sleep(1)
                self._queue_url = queue.get_queue_url(self._project, self._queue)
                return None
        except RetryAttemptsExceeded as e:
            ## TODO: clean up dynamo description
            # queue may not exist..
            #print(e)
            self._queue_url = queue.get_queue_url(self._project, self._queue)
            return None
    return wrapper

class Hero:
    def __init__(self, project=None, queue=None, resource_name=None):
        
        self.aws_credentials = None
        self._project = config.get_project(project)
        self._queue = config.get_queue(queue)
        self._resource_name = config.get_resource_name(resource_name)
        log.info(f'Initializing HERO {self._resource_name}')

    @property
    def resource_name(self):
        return self._resource_name

    @property
    def logged_in(self):
        if self.aws_credentials is not None:
            return True
        return False
        
    def login(self):
        if not self.logged_in:
            client_id, client_secret = config.get_client_credentials()
            scopes = ['hero-api/user', f'project/{self._project}']
            self.access_token = cognito.get_token(client_id=client_id, client_secret=client_secret, scopes=scopes)
            self.aws_credentials = role.assume_role(self.access_token)
            config.export_session_to_env(self.aws_credentials)
            self._session = get_session(self.aws_credentials)

            #TODO: This fails if the queue doesn't exist.
            try:
                self._queue_url = queue.get_queue_url(self._project, self._queue)
            except KeyError as e:
                print('Queue not found, you need to create the queue first.')
                # self._queue_url = create_queue(self._session, self._project, self._queue)
            self._table = dynamodb.get_project_table(self._session, self._project)

    @required_login
    def put_task(self, item):
        task = Task(
            project=self._project,
            queue_name=self._queue,
            queue_url=self._queue_url,
            inputs=item,
            status=READY,
            insert_resource_name=self._resource_name,
        )
        task_id = dynamodb.put_item(self._table, task)
        return task_id

    @required_login
    def put_tasks(self, items):
        tasks = [
            Task(
                project=self._project,
                queue_name=self._queue,
                queue_url=self._queue_url,
                inputs=i,
                status=READY,
                insert_resource_name=self._resource_name,
            )
            for i in items
        ]
        task_ids = dynamodb.put_items(self._table, tasks)
        return task_ids

    @required_login
    def clear_tasks(self):
        """
        Clears the queue of all messages by deleting queue
        """
        log.debug('clear_tasks')
        self._queue_url = queue.create_queue(self._project, self._queue)
        queue.delete_other_queues(self._queue_url, self._project, self._queue)
        queue.update_queue_url(self._project, self._queue, self._queue_url)
        #TODO: can you remind me...oh this is deleting tasks from Postgres. maybe rename this function
        rds.delete_queue(self._project, self._queue)

    @property
    def project_table(self):
        return dynamodb.get_project_table(self._session, self._project)

    def claim_task(self, task):
        task.claimed_resource_name = self._resource_name
        task.status = CLAIMED
    
    def poll(self, attempts, num_tasks=1):
        return retry_task(
            task.pull_task_sqs_dynamo,
            self.project_table,
            self._queue_url,
            self._resource_name,
            attempts=attempts,
            num_tasks=num_tasks
        )


    @pull_execptions
    def pull_task(self, attempts=3):
        """
        Pulls a task from the queue. Returns None otherwise.
        """   
        raw_task = self.poll(attempts, num_tasks=1)
        return self.create_task(raw_task[0])
       

    @pull_execptions
    def pull_tasks(self, attempts=3, num_tasks=1):
        """
        Pulls tasks from the queue. Returns None otherwise.
        """
        # for AWS SQS, max num_tasks is 10
        num_tasks = min(10, num_tasks)
        raw_tasks = self.poll(attempts, num_tasks=num_tasks)
        return [ self.create_task(raw_task) for raw_task in raw_tasks ]
    
    def create_task(self, raw_task):
        if raw_task is None:
            return None
        # Do we need this?
        # raw_task['task_id'] = raw_task['id']
        # raw_task['queue_name'] = raw_task['queue']
        del raw_task['id']
        del raw_task['queue']
        return Task(**raw_task)
        
    @required_login
    def update_task(self, task, results):
        """Updates a task in the queue"""
        # task.completed_resource_name = self._resource_name
        task.results = results
        task.status = COMPLETE
        dynamodb.update_item_results(
            self._table, task.task_id, task.queue_name, results=task.results
        )
        return task

    @required_login
    def get_task(self, task_id):
        """Gets a task from the queue"""
        response = self._table.get_item(Key={"id": task_id, "queue": self._queue})
        return response["Item"]
    
    def wait(self, seconds):
        """A simple wrapper for time.sleep"""
        time.sleep(seconds)

    def get_task_status_count(self, status):
        return rds.get_jobs_status_count_by_queue_url(self._project, self._queue, status)

    def send_exit_key_value(self, key, value, num_tasks=100):

        def create_task(index):
            return {
                "name": f"test_{index:02d}",
                "stream_db": False,
                key: value
            }
        
        items = [ create_task(i) for i in range(int(num_tasks)) ]
        self.put_tasks(items)
        
    def map(self, items, sleep=5):
        task_ids = self.put_tasks(items)
        # wait for tasks to be available
        while True:
            results = rds.get_items_detail(task_ids)
            if len(results) == len(task_ids) and all([r["status"] == COMPLETE for r in results]):
                return results
            time.sleep(sleep)