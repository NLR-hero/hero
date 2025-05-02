import json
import os
import threading
import time
from datetime import datetime, timezone

from ..url_map import URL_MAP
from ..lib import ServiceBase, decorate_all, log_errors, get_conf_from_collection
from ..lib.errors import MissingRequiredAttribute

from ..lib.patched_mlflow import enable_preflight_patching, get_patched_mlflow


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
        # guard for serializing refresh
        self._creds_lock = threading.Lock()
        self.client_credentials = None

    def _configure(self):
        """
        Sets the API and adds the user scope
        """
        self.registry_name = self.application_id
        self.client.add_scope("ml-model-registry/user")
        self.base_url = get_conf_from_collection(URL_MAP, "HERO_ML_MODEL_REGISTRY_URL")
        self.mlflow_client = enable_preflight_patching(
            preflight_hook=self.mlflow_preflight
        )
        self.mlflow = get_patched_mlflow()
        self.client_credentials = None

    def mlflow_preflight(self, method_name, *args, **kwargs):
        """
        Preflight hook for MLflow that only refreshes credentials
        when (a) they've never been fetched, or (b) they're about to expire.
        Concurrent callers will block on the same lock instead of stomping on
        each other.
        """
        token = self.client.get_token()
        if token is None:
            self.client.authenticate()

        # Check once without locking (fast path)
        if not self._needs_refresh():
            return

        # Only one thread at a time enters this block
        with self._creds_lock:
            # Check again inside the lock (double-check)
            if not self._needs_refresh():
                return
            # refresh if needed
            self.get_client_credentials()

    def _needs_refresh(self):
        """Return True if we've never fetched creds or they're expiring soon."""
        if self.client_credentials is None:
            return True
        exp_str = self.client_credentials["Expiration"]

        # Parse the ISO string into a datetime object
        dt = datetime.strptime(exp_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        # Set it as UTC (Z = Zulu = UTC)
        dt = dt.replace(tzinfo=timezone.utc)
        # Convert to UNIX timestamp
        exp_ts = dt.timestamp()

        # if within 5 minutes of expiry, refresh
        return (exp_ts - 300) < time.time()

    def get_client_credentials(self):
        """
        Atomically fetch & set client_credentials and export them into env vars.
        """
        creds = self.client.authInstance.get_client_credentials(
            self.registry_name, f"hero-service-role-ops-{self.registry_name}"
        )
        # only once everything is successful do we overwrite the shared state
        self.client_credentials = creds
        os.environ["AWS_ACCESS_KEY_ID"] = creds["AccessKeyId"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = creds["SecretAccessKey"]
        os.environ["AWS_SESSION_TOKEN"] = creds["SessionToken"]

    def get_patched_mlflow(self):
        return self.mlflow

    def get_patched_mlflow_client(self):
        return self.mlflow_client

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
