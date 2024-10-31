import json
from requests.exceptions import HTTPError, JSONDecodeError

from ..url_map import URL_MAP
from ..lib import (
    ServiceBase,
    decorate_all,
    log_errors,
    get_conf_from_collection,
    HeroRetryError,
)
from ..lib.errors import (
    MissingRequiredAttribute,
    HEROTaskEngineQueueNotFound,
    HEROTaskEngineTaskNotFound,
)
from ..lib.helpers import kwargs_to_json_for_request

@decorate_all(log_errors)
class TaskEngineService(ServiceBase):

    def _configure(self):
        """
        Sets the API, adds task engine id and required scope
        """
        self.task_engine_id = self.application_id
        self.client.add_scope("task-engine/user")
        self.base_url = get_conf_from_collection(URL_MAP, "HERO_TASK_ENGINE_API_URL")
        self.task_engine_url = f"{self.base_url}/{self.task_engine_id}"

    def read_queues(self, metatype: str = "Queue", state: str = "active") -> list[dict]:
        """
        List queues.

        Parameters
        ----------
        metatype : str, optional
            The metatype of the queue. Defaults to "Queue".

        state : str, optional
            The state of queues to list. Defaults to "active".

        Returns
        -------
        queues : list[dict]
            A list of queues where each dict is queue attributes.

        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.task_engine_url}/queues"
        params = {"metatype": metatype, "state": state}
        response = self.api.request("GET", url, headers=headers, params=params)
        return response.json()

    def read_queue(self, queue_id: str) -> dict:
        """
        Get a queue resource by id.

        Parameters
        ----------
        queue_id : str, required
            The queue UUID

        Returns
        -------
        queue : dict
            The queue attributes.

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROTaskEngineQueueNotFound
            If the queue does not exists

        """

        if queue_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "queue_id"')

        headers = self.get_headers(self.client.get_token())
        url = f'{self.task_engine_url}/queue/{queue_id}'
        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 404:
                raise HEROTaskEngineQueueNotFound()
            raise e

    def read_queue_by_name(self, task_engine_id : str=None, name : str=None, metatype : str="Queue", state : str=None) -> dict:
        """
        Read a queue by name.

        Parameters
        -----------
        task_engine_id : str, optional
            The parent task engine name. Note: in the future this will likely be a UUID.

        name : str, required
            The queue name.

        metatype : str, required
            Queue metatype. Defaults to "Queue".

        state : str, optional
            The state of the queue. Could be one of {"active", "deleted"}

        Returns
        --------
        queue : dict
            The queue attributes.

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROTaskEngineQueueNotFound
            If the queue does not exist

        Notes
        -----
        Added in version 0.3.0.
        """
        if name is None:
            raise MissingRequiredAttribute('Missing required attribute: "name"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.task_engine_url}/queue/metatype/{metatype}"

        params = kwargs_to_json_for_request(
            name=name, taskEngineId=task_engine_id, state=state
        )

        try:
            response = self.api.request("GET", url, headers=headers, params=params)
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 404:
                raise HEROTaskEngineQueueNotFound()
            raise e

    def delete_queue(self, queue_id: str) -> None:
        """
        Delete a queue.

        Parameters
        -----------
        queue_id : str, required
            The queue UUID to delete.

        Returns
        --------
        None

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        """

        if queue_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "queue_id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.task_engine_url}/queue/{queue_id}"
        response = self.api.request("DELETE", url, headers=headers)
        return None

    def add_queue(self, name, metatype="Queue", metadata={}):
        """
        Create a new queue.

        Parameters
        -----------
        name : str, required
            The name of the queue.

        metatype : str, optional
            The queue metatype. Defaults to "Queue".

        metadata : dict, optional
            The queue metadata. Defaults to an empty dictionary.

        Returns
        --------
        queue : dict
            The queue attributes

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        """

        attributes = {"name": name, "metatype": metatype, "metadata": metadata}

        # drop attributes that are None
        attributes = {k: v for k, v in attributes.items() if v is not None}

        if "name" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "name"')
        if "metadata" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "metadata"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.task_engine_url}/queue"
        data = json.dumps(attributes)
        response = self.api.request("POST", url, headers=headers, data=data)
        return response.json()

    def update_queue(self, queue_id, name, metadata={}):
        """
        Update the attributes of a queue resource.

        Parameters
        -----------
        name : str, required
            The name of the queue.

        metatype : str, optional
            The queue metatype. Defaults to "Queue".

        metadata : dict, optional
            The queue metadata. Defaults to an empty dictionary.

        Returns
        --------
        queue : dict
            The queue attributes

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        """

        if "queue_id" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "queue_id"')

        attributes = {"name": name, "metadata": metadata}

        if "name" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "name"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.task_engine_url}/queue/{queue_id}"
        data = json.dumps(attributes)
        response = self.api.request("POST", url, headers=headers, data=data)
        return response.json()

    def read_tasks(self, queue_id, metatype="Task", state="ready"):
        """
        List tasks.

        Parameters
        ----------
        queue_id : str, required
            A queue UUID.

        metatype : str, optional
            The metatype of the task. Defaults to "Task".

        state : str, optional
            The state of tasks to list. Defaults to "ready".

        Returns
        -------
        tasks : list[dict]
            A list of tasks where each dict is task attributes.

        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.task_engine_url}/queue/{queue_id}/tasks"
        params = {"metatype": metatype, "state": state}
        response = self.api.request("GET", url, headers=headers, params=params)
        return response.json()

    def read_task(self, task_id):
        """
        Get a task resource by id.

        Parameters
        ----------
        task_id : str, required
            The task UUID

        Returns
        -------
        task : dict
            The task attributes.

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROTaskEngineTaskNotFound
            If the task does not exists

        """

        if task_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "task_id"')

        headers = self.get_headers(self.client.get_token())
        url = f'{self.task_engine_url}/task/{task_id}'
        response = self.api.request('GET', url, headers=headers)
        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 404:
                raise HEROTaskEngineTaskNotFound()
            raise e

    def read_task_by_name(self, queue_id=None, name=None, metatype="Task"):
        """
        Read a task by name.

        Parameters
        -----------
        queue_id : str, optional
            The parent task engine UUID.

        name : str, required
            The task name.

        metatype : str, required
            Task metatype. Defaults to "Task".

        Returns
        --------
        task : dict
            The task attributes.

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROTaskEngineTaskNotFound
            If the task does not exist

        Notes
        -----
        Added in version 0.3.0.
        """
        if name is None:
            raise MissingRequiredAttribute('Missing required attribute: "name"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.task_engine_url}/task/metatype/{metatype}"

        params = kwargs_to_json_for_request(name=name, queueId=queue_id)

        try:
            response = self.api.request("GET", url, headers=headers, params=params)
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 404:
                raise HEROTaskEngineTaskNotFound()
            raise e

    def delete_task(self, task_id):
        """
        Delete a task.

        Parameters
        -----------
        task_id : str, required
            The task UUID to delete.

        Returns
        --------
        None

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        """

        if task_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "task_id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.task_engine_url}/task/{task_id}"
        response = self.api.request("DELETE", url, headers=headers)
        return response.json()

    def add_task(self, queue_id, name, metatype="Task", metadata={}):
        """
        Create a new task.

        Parameters
        ----------
        queue_id : str, required
            A queue UUID.

        name : str, required
            The name of the task.

        metatype : str, optional
            The task metatype. Defaults to "Task".

        metadata : dict, optional
            The task metadata. Defaults to an empty dictionary.

        Returns
        --------
        task : dict
            The task attributes

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        """

        attributes = {
            "queueId": queue_id,
            "name": name,
            "metatype": metatype,
            "metadata": metadata,
        }

        # drop attributes that are None
        attributes = {k: v for k, v in attributes.items() if v is not None}

        if "queueId" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "queue_id"')
        if "name" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "name"')
        if "metadata" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "metadata"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.task_engine_url}/task"
        data = json.dumps(attributes)
        response = self.api.request("POST", url, headers=headers, data=data)
        return response.json()

    def update_task(self, task_id, name, state, metadata={}):
        """
        Update an existing task.

        Parameters
        ----------
        queue_id : str, required
            A queue UUID.

        name : str, required
            The name of the task.

        metatype : str, optional
            The task metatype. Defaults to "Task".

        metadata : dict, optional
            The task metadata. Defaults to an empty dictionary.

        Returns
        --------
        task : dict
            The task attributes
        
        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        """

        attributes = {
            "name": name,
            "metadata": metadata,
            "state": state,
            # "inputs": inputs,
            # "outputs": outputs
        }

        if "name" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "name"')
        
        # if "task_id" not in attributes.keys():
        #     raise MissingRequiredAttribute('Missing required attribute: "task_id"')

        headers = self.get_headers(self.client.get_token())
        url = f'{self.task_engine_url}/task/{task_id}'
        data = json.dumps(attributes)
        response = self.api.request('POST', url, headers=headers, data=data)
        return response.json()
