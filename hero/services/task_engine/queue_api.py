from ...config import get_task_engine_api
from ...api import ApiBase



class QueueApi(ApiBase):

    ACTIVE = "active"
    DELETED = "deleted"

    def __init__(self, resilient_session=False):
        super().__init__(resilient_session)
        self.base_url = get_task_engine_api()

    def add_or_get_queue(self, token, task_engine_id, data):
        """
        Returns the active queue associated with a queue_name if it exists. If it doesn't
        exist, it creates a new queue and returns
        """
        url = f"{self.base_url}/{task_engine_id}/queue"
        response = self.session.request("POST", url, headers=self.get_headers(token), data=data)
        response.raise_for_status()
        return response.json()


    def delete_queue(self, token, task_engine_id, queue_id):
        """
        Marks the queue as deleted
        """
        url = f"{self.base_url}/{task_engine_id}/queue/{queue_id}"
        response = self.session.request("DELETE", url, headers=self.get_headers(token))
        response.raise_for_status()
        return response.json()


    def get_queues(self, token, task_engine_id, queue_name, state):
        """
        Returns a random set of `limit` queues of a given `state`
        """
        state = state or QueueApi.ACTIVE
        assert state in [QueueApi.ACTIVE, QueueApi.DELETED]
        url = f"{self.base_url}/{task_engine_id}/queues/metatype/Queue"
        query_params = f"?name={queue_name}|{state}"
        url = url + query_params
        response = self.session.request("GET", url, headers=self.get_headers(token))
        response.raise_for_status()
        return response.json()


    def get_active_queue(self, access_token, task_engine_id, queue_name):
        """
        There can only be one active queue for a given queue_name.  This returns
        that queue or None if an active queue doesn't exist.
        """
        queues = self.get_queues(access_token, task_engine_id, queue_name, state=QueueApi.ACTIVE)
        for queue in queues:
            if queue["name"] == queue_name:
                tmp = {
                    "id": queue["id"],
                    "name": queue["name"],
                    "queueUrl": queue["queueUrl"],
                }
                return tmp
