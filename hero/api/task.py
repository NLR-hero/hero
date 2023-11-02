import json
import time
import uuid

from typing import Optional
from dataclasses import dataclass, field
from decimal import Decimal
import logging

log = logging.getLogger(__name__)

READY = "ready"
CLAIMED = "claimed"
COMPLETE = "complete"
FAILED = "failed"


from .. import aws
from .. import config
#TODO: replace these with calls into the aws module...
# from .queue import receive_messages, delete_message
# from .dynamo import update_item_claimed, get_project_table
# from .rds import get_next_available_job




def pull_task_sqs_dynamo(session, project, resource_name, worker_id, num_tasks=1, queue_url=None):
    """
    Returns a task froma queue if availabe and it is not already claimed, otherwise returns None.
    """
    if queue_url is None:
        return None
    
    project_table = aws.dynamodb.get_project_table(session, project)
    messages = aws.sqs.receive_messages(session, queue_url, max_number_of_messages=num_tasks)

    tasks = []
    for message in messages:
        task = json.loads(message["Body"])
        task['claimed_resource_name'] = resource_name
        task['claimed_worker_id'] = worker_id
        # either way we need to delete the message from the queue
        aws.sqs.delete_message(session, queue_url, message)
        if aws.dynamodb.update_item_claimed(project_table, 
                                            task["id"], 
                                            task["queue"], 
                                            task['claimed_resource_name'], 
                                            task['claimed_worker_id']) == True:
            if num_tasks == 1:
                return [task]
            tasks.append(task)
        else:
            print(f"task {task['id']} already claimed")
            
    if len(tasks) > 0:
        return tasks

    return None

def _convert_to_decimal_json(data):
    return json.loads(json.dumps(data), parse_float=Decimal)


def get_new_uuid() -> str:
    return str(uuid.uuid4())


@dataclass
class Task:
    project: str
    queue_name: str
    queue_url: str
    inputs: dict
    # defaults
    task_id: Optional[str] = field(default_factory=get_new_uuid)
    status: str = READY
    created_by: str = None

    insert_time: str = None
    claimed_time: str = None
    complete_time: str = None

    insert_resource_name: str = None
    claimed_resource_name: str = None
    complete_resource_name: str = None
    
    insert_worker_id: str = None
    claimed_worker_id: str = None
    complete_worker_id: str = None

    attempts: int = 0
    inputs_s3: str = None
    results: dict = field(default_factory=dict)
    results_s3: str = None

    @property
    def data(self):
        tmp = self.__dict__
        # need these to match dynamo table
        tmp["id"] = self.task_id
        tmp["queue"] = self.queue_name
        return tmp


def create_task(task):
    aws.dynamodb.put_item(item.data)


# def put_item(item, project=None):
#     """
#     Puts an item into the table.
#     """
#     table_name = 'hero-dynamodb-project-queue-names'
#     table = aws.dynamodb.get_table(session, table_name)
#     project = config.get_project(project)
#     response = table.put_item(Item=item.data)
#     assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
#     return item.task_id