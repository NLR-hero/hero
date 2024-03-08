import os
import json
import time
from ..resilent_session import ResilientSession

HERO_TASK_ENGINE_API_URL = os.environ.get(
    "HERO_TASK_ENGINE_API_URL",
    "https://db1kvdyyqlha5.cloudfront.net/task-engine/api/v1",
)

READY = "ready"
CLAIMED = "claimed"
DONE = "done"
FAILED = "failed"


def add_task(token, task_engine_id, queue_id, task):
    """
    Adds a task to the queue with queue_id
    """
    url = f"{HERO_TASK_ENGINE_API_URL}/{task_engine_id}/task"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    # ensure the task has the following minimum fields
    task["queueId"] = queue_id
    task["metadata"] = task.get("metadata", {})
    task["inputs"] = task.get("inputs", {})
    assert "name" in task

    payload = json.dumps(task)
    s = ResilientSession()
    response = s.request("POST", url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()


def pull_tasks(token, task_engine_id, queue_id, messages=1, visibility_timeout=60):
    """
    The API pulls a task from SQS, checks to ensure it has not been claimed,
    and returns the task.
    """
    url = f"{HERO_TASK_ENGINE_API_URL}/{task_engine_id}/tasks"
    query_params = f"?receive={messages}"
    query_params += f"&visibilityTimeout={visibility_timeout}"
    query_params += f"&queueId={queue_id}"
    url = url + query_params
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    s = ResilientSession()
    response = s.request("GET", url, headers=headers)
    response.raise_for_status()
    return response.json()


def update_task(token, task_engine_id, task_id, task):
    """
    Updates the task status and results in dynamodb and steams to open search.
    """
    url = f"{HERO_TASK_ENGINE_API_URL}/{task_engine_id}/task/{task_id}"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    # ensure it has the following fields
    task["state"] = task.get("state", DONE)
    assert task["state"] in [DONE, READY, CLAIMED, FAILED]
    task["outputs"] = task.get("outputs", {})

    payload = json.dumps(task)
    s = ResilientSession()
    response = s.request("POST", url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()


def get_tasks(token, task_engine_id, queue_id, state=READY):
    """ """
    url = f"{HERO_TASK_ENGINE_API_URL}/{task_engine_id}/queue/{queue_id}/tasks"
    query_params = f"?metatype=Task&state={READY}"
    url = url + query_params
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    s = ResilientSession()
    response = s.request("GET", url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_ready_tasks(token, task_engine_id, queue_id):
    return get_tasks(token, task_engine_id, queue_id, state=READY)


def get_completed_tasks(token, task_engine_id, queue_id):
    return get_tasks(token, task_engine_id, queue_id, state=DONE)
