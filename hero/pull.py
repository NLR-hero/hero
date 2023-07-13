import json
import time

from .task import Task
from .queue import receive_messages, delete_message
from .dynamo import update_item_claimed, get_project_table
from .rds import get_next_available_job


def retry(pull_function, project, queue, queue_url, attempts=3):
    retries = 0
    while retries < attempts:
        task = pull_function(project, queue, queue_url)
        if task is None:
            retries += 1
            time.sleep(retries)
        else:
            return task


def pull_task_sqs_dynamo(project, queue, queue_url):
    table = get_project_table(project)
    message_packet = receive_messages(queue_url)

    if "Messages" in message_packet.keys():
        for m in message_packet["Messages"]:
            task = json.loads(m["Body"])
            # either way we need to delete the message from the queue
            delete_message(queue_url, m)
            if update_item_claimed(table, task["id"], task["queue"]) == True:
                return task
            else:
                print(f"task {task['id']} already claimed")


def pull_task_rds(project, queue, queue_url):
    task = get_next_available_job(queue_url)
    return task
