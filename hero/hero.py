import json
import time
import requests
from botocore.exceptions import ClientError

from .task import Task, COMPLETE, CLAIMED, READY
from .dynamo import (
    get_queue_url,
    get_project_table,
    put_item,
    put_items,
    update_queue_url,
    update_item_results,
)
from .queue import create_queue, receive_messages
from .session import get_project, get_queue, get_session, get_client_credentials
from .pull import retry, pull_task_sqs_dynamo
from .auth import get_token_from_cognito, assume_role

import socket

get_session()

# class SuperHero:
# - clear_tasks
# - create_tables, dynamo_streams, lambda_functions with tagging


class Hero:
    def __init__(self, project=None, queue=None):
        client_id, client_secret = get_client_credentials()
        scopes = ['hero-api/user']
        self.access_token = get_token_from_cognito(client_id=client_id, client_secret=client_secret, scopes=scopes)
        self.aws_credentials = assume_role(self.access_token)

        self._session = get_session(self.aws_credentials)
        self._project = get_project(project)
        self._queue = get_queue(queue)

        #TODO: This fails if the queue doesn't exist.
        try:
            self._queue_url = get_queue_url(self._session, self._project, self._queue)
        except KeyError as e:
            print('Queue not found, you need to create the queue first.')
            # self._queue_url = create_queue(self._session, self._project, self._queue)
        self._table = get_project_table(self._session, self._project)
        self._resource_name = socket.gethostname()

        

    # def get_queue_url(self):
    #     endpoint = f'{API_URL}/hero/api/v2/project/{self.project}/queue/{self.queue}'
    #     response = requests.get(endpoint,
    #         headers={
    #             'Authorization': f'Bearer {self.access_token}'
    #         },
    #         verify=False)
    #     return response.json()['QueueUrl']

    def put_task(self, item):
        task = Task(
            project=self._project,
            queue_name=self._queue,
            queue_url=self._queue_url,
            inputs=item,
            status=READY,
            insert_resource_name=self._resource_name,
        )
        task_id = put_item(self._table, task)
        return task_id

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
        task_ids = put_items(self._table, tasks)
        return task_ids

    def clear_tasks(self):
        """Clears the queue of all messages by deleting queue"""
        self._queue_url = create_queue(self._session, self._project, self._queue)
        update_queue_url(self._session, self._project, self._queue, self._queue_url)

    def pull_task(self, attempts=3):
        """Pulls a task from the queue. If the queue is empty, it will return None."""
        try:
            raw_task = retry(
                pull_task_sqs_dynamo,
                self._session,
                self._project,
                self._queue,
                self._queue_url,
                attempts=attempts,
            )
            ## TODO: clean up dynamo description
            if raw_task is None:
                # queue may not exist..
                print("REDO this functionality...")
                self._queue_url = get_queue_url(self._session, self._project, self._queue)
                return None
            del raw_task["id"]
            del raw_task["queue"]
            raw_task["claimed_resource_name"] = self._resource_name
            raw_task["status"] = CLAIMED
            task = Task(**raw_task)
            return task
        except ClientError as e:
            if e.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
                print("queue does not exist, getting new queue")
                time.sleep(1)
                self._queue_url = get_queue_url(self._session, self._project, self._queue)
                raw_task = retry(
                    pull_task_sqs_dynamo,
                    self._session,
                    self._project,
                    self._queue,
                    self._queue_url,
                    attempts=attempts,
                )
                if raw_task is None:
                    return None
                del raw_task["id"]
                del raw_task["queue"]
                raw_task["claimed_resource_name"] = self._resource_name
                raw_task["status"] = CLAIMED
                task = Task(**raw_task)
                return task

        

    def update_task(self, task, results):
        """Updates a task in the queue"""
        # task.completed_resource_name = self._resource_name
        task.results = results
        task.status = COMPLETE
        update_item_results(
            self._table, task.task_id, task.queue_name, results=task.results
        )
        return task

    def get_task(self, task_id):
        """Gets a task from the queue"""
        response = self._table.get_item(Key={"id": task_id, "queue": self._queue})
        return response["Item"]
