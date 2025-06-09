import json
import os
import threading
import urllib.parse

from ..url_map import URL_MAP
from ..lib import ServiceBase, decorate_all, log_errors, get_conf_from_collection
from ..lib.errors import MissingRequiredAttribute


@decorate_all(log_errors)
class MLModelRegistry(ServiceBase):

    def __init__(self, client, application_id):
        """
        Initializes the MLModelRegistry class

        Parameters
        ----------
        client : object
            The client to use for authentication
        application_id : str
            The application ID for the ML Model Registry
        """
        super().__init__(client, application_id)
        self._creds_lock = threading.Lock()
        self.client_credentials = None

    def _configure(self):
        """
        Sets the API and adds the user scope
        """
        self.registry_name = self.application_id
        self.client.add_scope("ml-model-registry/user")
        self.base_url = get_conf_from_collection(URL_MAP, "HERO_ML_MODEL_REGISTRY_URL")
        self.client_credentials = None

    def get_tracking_uri(self):
        """
        Returns the MLflow tracking URI.
        """
        return self.base_url

    # hero-core MLModelRegistry
    def get_patched_mlflow(self):
        try:
            from hero_mlflow.mlflow_support import get_patched_mlflow
        except ImportError as e:
            raise RuntimeError(
                "hero-mlflow is not installed. To use MLflow support, install it via:\n"
                "pip install git+https://github.com/myorg/hero-mlflow.git"
            ) from e

        return get_patched_mlflow(self.client, self.application_id)

    def get_patched_mlflow_client(self):
        """
        Lazily loads and returns the patched MLflow client (tracking + preflight).
        """
        try:
            from hero_mlflow.mlflow_support import get_patched_mlflow_client
        except ImportError as e:
            raise RuntimeError(
                "hero-mlflow is not installed. To use MLflow support, install it via:\n"
                "pip install git+https://github.com/myorg/hero-mlflow.git"
            ) from e

        return get_patched_mlflow_client(self.client, self.application_id)

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
        filter=None,
        run_view_type=None,
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
        filter : str, optional
            The filter to apply to the runs, by default None
        run_view_type : str, optional
            The view type to apply to the runs, by default None (API default is 'ACTIVE_ONLY')

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
        if filter is not None:
            params["filter"] = urllib.parse.quote(filter, safe="")
        if run_view_type is not None:
            params["runViewType"] = run_view_type
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

    def update_run(self, run_id, attributes):
        """
        Updates a run in the model registry

        Parameters
        ----------
        run_id : str
            The ID of the run to update
        attributes : dict
            The attributes to update Note: Only `name` and `description` can be updated

        Returns
        -------
        run : dict
            The updated run

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if run_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "run_id"')
        if attributes is None:
            raise MissingRequiredAttribute('Missing required attribute: "attributes"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/run/{run_id}"
        data = json.dumps(attributes)
        response = self.api.request("PUT", url, headers=headers, json=data)
        return response.json()

    def read_metric_history(self, run_id, metric, count=None, next_token=None):
        """
        Reads the history of a metric for a given run ID in the model registry

        Parameters
        ----------
        run_id : str
            The ID of the run to read metric history for
        metric : str
            The name of the metric to read history for
        count : int, optional
            The number of metrics to return, by default None
        next_token : str, optional
            The token for the next page of metrics, by default None

        Returns
        -------
        metric_history : dict
            The history of the metric for the given run ID

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if run_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "run_id"')
        if metric is None:
            raise MissingRequiredAttribute('Missing required attribute: "metric"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/run/{run_id}/history"
        params = {"count": count, "nextToken": next_token, "metric": metric}
        response = self.api.request("GET", url, headers=headers, params=params)
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
