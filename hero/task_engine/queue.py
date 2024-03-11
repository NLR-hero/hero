import os
import json
import time
from ..resilient_session import ResilientSession


HERO_TASK_ENGINE_API_URL = os.environ.get(
    "HERO_TASK_ENGINE_API_URL",
    "https://db1kvdyyqlha5.cloudfront.net/task-engine/api/v1",
)

ACTIVE = "active"
DELETED = "deleted"


def add_or_get_queue(token, task_engine_id, queue_name):
    """
    Returns the active queue associated with a queue_name if it exists. If it doesn't
    exist, it creates a new queue and returns
    """
    url = f"{HERO_TASK_ENGINE_API_URL}/{task_engine_id}/queue"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    attributes = {"name": queue_name}
    payload = json.dumps(attributes)
    s = ResilientSession()
    response = s.request("POST", url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()


def delete_queue(token, task_engine_id, queue_id):
    """
    Marks the queue as deleted
    """
    url = f"{HERO_TASK_ENGINE_API_URL}/{task_engine_id}/queue/{queue_id}"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    s = ResilientSession()
    response = s.request("DELETE", url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_queues(token, task_engine_id, queue_name, state=ACTIVE):
    """
    Returns a random set of `limit` queues of a given `state`
    """
    assert state in [ACTIVE, DELETED]
    url = f"{HERO_TASK_ENGINE_API_URL}/{task_engine_id}/queues/metatype/Queue"
    query_params = f"?name={queue_name}|{state}"
    url = url + query_params
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    s = ResilientSession()
    response = s.request("GET", url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_active_queue(access_token, task_engine_id, queue_name):
    """
    There can only be one active queue for a given queue_name.  This returns
    that queue or None if an active queue doesn't exist.
    """
    queues = get_queues(access_token, task_engine_id, queue_name, state=ACTIVE)
    for queue in queues:
        if queue["name"] == queue_name:
            tmp = {
                "id": queue["id"],
                "name": queue["name"],
                "queueUrl": queue["queueUrl"],
            }
            return tmp
