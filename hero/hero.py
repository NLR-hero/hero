"""
Welcome to Hero.


"""
import time
import socket
import logging
from botocore.exceptions import ClientError

from .api.task import Task, COMPLETE, CLAIMED, READY
from .auth import cognito
from .api import role, queue, task
from .api.utils import RetryAttemptsExceeded, retry
from .config import config
from .aws import dynamodb
from .aws.utils import get_session

log = logging.getLogger("hero:hero")

def required_login(func):
    def wrapper(self, *args, **kwargs):
        self.login()
        return func(self, *args, **kwargs)
    return wrapper

class Hero:
    def __init__(self, project=None, queue=None):
        log.info('Initializing HERO')
        self.aws_credentials = None
        self._project = config.get_project(project)
        self._queue = config.get_queue(queue)
        self._resource_name = socket.gethostname()


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

    @property
    def project_table(self):
        return dynamodb.get_project_table(self._session, self._project)

    def claim_task(self, task):
        task.claimed_resource_name = self._resource_name
        task.status = CLAIMED
    
    def poll(self, attempts):
        return retry(
            task.pull_task_sqs_dynamo,
            self.project_table,
            self._queue_url,
            attempts=attempts
        )

    @required_login
    def pull_task(self, attempts=3):
        """
        Pulls a task from the queue. Returns None otherwise.
        """
        try:
            print('queue_url', self._queue_url)
            raw_task = self.poll(attempts)
            return self.create_task(raw_task)
        except ClientError as e:
            if e.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
                print("queue does not exist, getting new queue")
                time.sleep(1)
                self._queue_url = queue.get_queue_url(self._project, self._queue)
                return None
        except RetryAttemptsExceeded as e:
            ## TODO: clean up dynamo description
            # queue may not exist..
            print(e)
            self._queue_url = queue.get_queue_url(self._project, self._queue)
            return None


    def create_task(self, raw_task):
        if raw_task is None:
            return None
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
