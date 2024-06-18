import json

from ...config import get_task_engine_api
from ...api import ApiBase

ACTIVE = "active"
DELETED = "deleted"


class QueueApi(ApiBase):
    def __init__(self, resilient_session=False):
        super().__init__(resilient_session)
        self.base_url = get_task_engine_api()

    def add_or_get_queue(self, token, task_engine_id, queue_name):
        """
        Returns the active queue associated with a queue_name if it exists. If it doesn't
        exist, it creates a new queue and returns
        """
        url = f"{self.base_url}/{task_engine_id}/queue"
        attributes = {"name": queue_name}
        payload = json.dumps(attributes)
        response = self.session.request("POST", url, headers=self.getHeaders(token), data=payload)
        response.raise_for_status()
        return response.json()


    def delete_queue(self, token, task_engine_id, queue_id):
        """
        Marks the queue as deleted
        """
        url = f"{self.base_url}/{task_engine_id}/queue/{queue_id}"
        response = self.session.request("DELETE", url, headers=self.getHeaders(token))
        response.raise_for_status()
        return response.json()


    def get_queues(self, token, task_engine_id, queue_name, state=ACTIVE):
        """
        Returns a random set of `limit` queues of a given `state`
        """
        assert state in [ACTIVE, DELETED]
        url = f"{self.base_url}/{task_engine_id}/queues/metatype/Queue"
        query_params = f"?name={queue_name}|{state}"
        url = url + query_params
        response = self.session.request("GET", url, headers=self.getHeaders(token))
        response.raise_for_status()
        return response.json()


    def get_active_queue(self, access_token, task_engine_id, queue_name):
        """
        There can only be one active queue for a given queue_name.  This returns
        that queue or None if an active queue doesn't exist.
        """
        queues = self.get_queues(access_token, task_engine_id, queue_name, state=ACTIVE)
        for queue in queues:
            if queue["name"] == queue_name:
                tmp = {
                    "id": queue["id"],
                    "name": queue["name"],
                    "queueUrl": queue["queueUrl"],
                }
                return tmp
