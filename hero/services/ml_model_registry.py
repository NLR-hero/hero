import json
import os
from tqdm import tqdm
import requests

from ..url_map import URL_MAP
from ..lib import ServiceBase, decorate_all, log_errors, get_conf_from_collection
from ..lib.errors import MissingRequiredAttribute


@decorate_all(log_errors)
class MLModelRegistry(ServiceBase):

    def __init__(self, clientInstance, registry_name):
        if not registry_name:
            raise ValueError("registry_name must be provided")
        self.base_url = get_conf_from_collection(URL_MAP, "HERO_ML_MODEL_REGISTRY_URL")
        self.registry_name = registry_name
        super().__init__(clientInstance)

    def _configure(self):
        """
        Sets the API and adds the user scope
        """
        self.client.add_scope("m3s/user")

    def get_tracking_uri(self):
        """
        Sets the MLFlow tracking token in the environment and returns the tracking URI
        """
        os.environ["MLFLOW_TRACKING_TOKEN"] = self.client.get_token()
        return f"{self.base_url}/proxy/{self.registry_name}"

    def list_experiments(self, count=None, next_token=None):
        """
        Lists the experiments in the registry

        Parameters
        ----------
        count : int, optional
            The number of experiments to list, by default None
        next_token : str, optional
            The token to get the next set of experiments, by default None

        Returns
        -------
        experiment_collection: dict
            The collection of experiments
        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/experiments"
        params = {"count": count, "nextToken": next_token}
        response = self.api.request("GET", url, headers=headers, params=params)
        return response.json()

    def read_experiment(self, experiment_id):
        """
        Reads the experiment with the given ID

        Parameters
        ----------
        experiment_id : str
            The ID of the experiment to read

        Returns
        -------
        experiment : dict
            The experiment with the given ID

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if experiment_id is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "experiment_id"'
            )

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/experiment/{experiment_id}"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def update_experiment(self, experiment_id, attributes):
        """
        Updates the experiment with the given ID

        Parameters
        ----------
        experiment_id : str
            The ID of the experiment to update
        attributes : dict
            The attributes to update Note: Only `name` can be updated

        Returns
        -------
        experiment : dict
            The updated experiment

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if experiment_id is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "experiment_id"'
            )
        if attributes is None:
            raise MissingRequiredAttribute('Missing required attribute: "attributes"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/experiment/{experiment_id}"
        data = json.dumps(attributes)
        response = self.api.request("PUT", url, headers=headers, json=data)
        return response.json()

    def delete_experiment(self, experiment_id):
        """
        Deletes the experiment with the given ID

        Parameters
        ----------
        experiment_id : str
            The ID of the experiment to delete

        Returns
        -------
        experiment : dict
            The deleted experiment

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if experiment_id is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "experiment_id"'
            )

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/experiment/{experiment_id}"
        response = self.api.request("DELETE", url, headers=headers)
        return response.json()

    def list_runs(
        self,
        experiment_id,
        count=None,
        next_token=None,
        search_key=None,
        sort_order=None,
    ):
        """
        Lists the runs for the given experiment ID

        Parameters
        ----------
        experiment_id : str
            The ID of the experiment to list runs for
        count : int, optional
            The number of runs to list, by default None
        next_token : str, optional
            The token to get the next set of runs, by default None
        search_key : str, optional
            The key to search for, by default None (API default is 'attributes.start_time')
        sort_order : str, optional
            The order to sort the runs, by default None (API default is 'DESC')

        Returns
        -------
        run_collection : dict
            The collection of runs for the given experiment ID

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if experiment_id is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "experiment_id"'
            )

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/experiment/{experiment_id}/runs"
        params = {
            "count": count,
            "nextToken": next_token,
            "searchKey": search_key,
            "sortOrder": sort_order,
        }
        response = self.api.request("GET", url, headers=headers, params=params)
        return response.json()

    def read_run(self, run_id):
        """
        Reads the run with the given ID

        Parameters
        ----------
        run_id : str
            The ID of the run to read

        Returns
        -------
        run : dict
            The run with the given ID

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if run_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "run_id"')
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/run/{run_id}"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def delete_run(self, run_id):
        """
        Deletes the run with the given ID

        Parameters
        ----------
        run_id : str
            The ID of the run to delete

        Returns
        -------
        run : dict
            The deleted run

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if run_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "run_id"')
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/run/{run_id}"
        response = self.api.request("DELETE", url, headers=headers)
        return response.json()

    def list_artifacts(self, run_id):
        """
        Lists the artifacts for a given run ID

        Parameters
        ----------
        run_id : str
            The ID of the run to list artifacts for

        Returns
        -------
        artifact_collection : dict
            The collection of artifacts for the given run ID

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if run_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "run_id"')
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/run/{run_id}/artifacts"
        response = self.api.request("GET", url, headers=headers)
        return response.json()
