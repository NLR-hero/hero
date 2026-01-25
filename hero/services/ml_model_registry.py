import json
import os
import threading
from urllib import response
import urllib.parse

from ..url_map import URL_MAP
from ..lib import (
    ServiceBase,
    decorate_all,
    log_errors,
    get_conf_from_collection,
    HeroObject,
)
from ..lib.errors import (
    MissingRequiredAttribute,
    HEROMLModelRegistryResourceAlreadyExists,
    HEROMLModelRegistryResourceNotFound,
    HEROMLModelRegistryForbiddenError,
)
from requests.exceptions import HTTPError


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
        self.base_url = get_conf_from_collection(
            URL_MAP, "HERO_ML_MODEL_REGISTRY_API_URL"
        )
        self.client_credentials = None

    def get_patched_mlflow(self):
        try:
            from hero_mlflow.mlflow_support import get_patched_mlflow
        except ImportError as e:
            raise RuntimeError(
                "hero-mlflow is not installed. To use MLflow support, install it via:\n"
                "pip install git+https://github.nrel.gov/Hero/hero-mlflow.git"
            ) from e

        return get_patched_mlflow(
            self.get_tracking_uri(),
            self.client,
            self.application_id,
            self.client.get_token,
        )

    def get_patched_mlflow_client(self):
        """
        Lazily loads and returns the patched MLflow client (tracking + preflight).
        """
        try:
            from hero_mlflow.mlflow_support import get_patched_mlflow_client
        except ImportError as e:
            raise RuntimeError(
                "hero-mlflow is not installed. To use MLflow support, install it via:\n"
                "pip install git+https://github.nrel.gov/Hero/hero-mlflow.git"
            ) from e

        return get_patched_mlflow_client(
            self.get_tracking_uri(),
            self.client,
            self.application_id,
            self.client.get_token,
        )

    def get_tracking_uri(self):
        """
        Sets the MLFlow tracking token in the environment and returns the tracking URI
        """
        os.environ["MLFLOW_TRACKING_TOKEN"] = self.client.get_token()
        return f"{self.base_url}/proxy/{self.registry_name}"

    def get_description_from_tags(self, tags):
        description = ""
        for tag in tags:
            if tag["key"] == "mlflow.note.content":
                description = tag["value"]
        return description

    def _extract_detail_from_response(self, response):
        if response is None:
            return None
        try:
            body = response.json()
            # Prefer common string fields, but handle nested structures safely.
            for key in ("message", "error", "detail"):
                if key in body:
                    val = body.get(key)
                    if isinstance(val, str):
                        return val
                    if isinstance(val, dict):
                        # Try nested message-like fields
                        for nk in ("message", "error", "detail"):
                            nv = val.get(nk)
                            if isinstance(nv, str):
                                return nv
                        # fall back to stringifying the nested dict
                        return str(val)
            return str(body)
        except Exception:
            return getattr(response, "text", None)

    def _raise_forbidden_from_http_error(self, http_error, operation):
        resp = getattr(http_error, "response", None)
        if resp is None:
            raise http_error
        status = resp.status_code
        detail = self._extract_detail_from_response(resp)
        detail_str = None
        if detail:
            detail_str = detail if isinstance(detail, str) else str(detail)
        # Fallback to raw response text if extractor didn't produce a string
        if not detail_str:
            raw_text = getattr(resp, "text", None)
            if raw_text:
                detail_str = raw_text

        # Handle 403 as forbidden/access denied
        if status == 403:
            msg = None
            if detail_str:
                msg = f"HERO ML Model Registry access denied for registry '{self.registry_name}' during '{operation}': {detail_str}"
            raise HEROMLModelRegistryForbiddenError(
                self.registry_name, operation, message=msg
            )

        # Handle 400 with "already exists" messages as resource conflict
        if status == 400 and detail_str:
            detail_lower = detail_str.lower()
            if "already exists" in detail_lower or "already exist" in detail_lower:
                raise HEROMLModelRegistryResourceAlreadyExists()

        raise http_error

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
        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "experiments" in data:
                return HeroObject(data).experiments
            return []
        return []

    def create_experiment(self, name):
        """
        Creates an experiment in the registry

        Parameters
        ----------
        name : str
            The name of the experiment to create

        Returns
        -------
        experiment : dict
            The created experiment

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if name is None:
            raise MissingRequiredAttribute('Missing required attribute: "name"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/experiment"
        attributes = {"name": name}
        try:
            response = self.api.request("POST", url, headers=headers, json=attributes)
            data = response.json()
            return HeroObject(data)
        except HTTPError as e:
            if (
                getattr(e, "response", None) is not None
                and e.response.status_code == 409
            ):
                raise HEROMLModelRegistryResourceAlreadyExists()
            if getattr(e, "response", None) is not None:
                self._raise_forbidden_from_http_error(e, "create_experiment")
            else:
                raise e

    def read_experiment(self, id):
        """
        Reads the experiment with the given ID

        Parameters
        ----------
        id : str
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
        if id is None:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/experiment/{id}"
        try:
            response = self.api.request("GET", url, headers=headers)
            data = response.json()
            return HeroObject(data).experiment
        except HTTPError as e:
            if e.response.status_code == 404:
                raise HEROMLModelRegistryResourceNotFound()
            if getattr(e, "response", None) is not None:
                self._raise_forbidden_from_http_error(e, "read_experiment")
            else:
                raise e

    def read_experiment_by_name(self, name):
        """
        Reads the experiment with the given name

        Parameters
        ----------
        name : str
            The name of the experiment to read

        Returns
        -------
        experiment : dict
            The experiment with the given name

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if name is None:
            raise MissingRequiredAttribute('Missing required attribute: "name"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/experiment/by-name/{urllib.parse.quote(name, safe='')}"
        try:
            response = self.api.request("GET", url, headers=headers)
            data = response.json()
            return HeroObject(data).experiment
        except HTTPError as e:
            if e.response.status_code == 404:
                raise HEROMLModelRegistryResourceNotFound()
            if getattr(e, "response", None) is not None:
                self._raise_forbidden_from_http_error(e, "read_experiment_by_name")
            else:
                raise e

    def read_or_create_experiment(self, name):
        """
        Reads the experiment with the given name, or creates it if it does not exist

        Parameters
        ----------
        name : str
            The name of the experiment to read or create

        Returns
        -------
        experiment : dict
            The experiment with the given name

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        HEROMLModelRegistryForbiddenError
            If access is denied (e.g., experiment belongs to another project)
        """
        try:
            return self.read_experiment_by_name(name)
        except HEROMLModelRegistryResourceNotFound:
            # Experiment doesn't exist, try to create it
            return self.create_experiment(name)
        except HEROMLModelRegistryForbiddenError:
            # Access denied (e.g., cross-project ownership) - don't try to create
            raise

    def update_experiment(self, id, name=None, description=None):
        """
        Updates the experiment with the given ID

        Parameters
        ----------
        id : str
            The ID of the experiment to update
        name : str, optional
            The new name for the experiment, by default None
        description : str, optional
            The new description for the experiment, by default None

        Returns
        -------
        experiment : dict
            The updated experiment

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if id is None:
            raise MissingRequiredAttribute('Missing required attribute: "id"')
        attributes = {}
        if name is not None:
            attributes["name"] = name
        if description is not None:
            attributes["description"] = description
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/experiment/{id}"
        response = self.api.request("PUT", url, headers=headers, json=attributes)
        data = response.json()
        if isinstance(data, dict) and "experiment" in data:
            return HeroObject(data).experiment
        return HeroObject(data)

    def delete_experiment(self, id):
        """
        Deletes the experiment with the given ID

        Parameters
        ----------
        id : str
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
        if id is None:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/experiment/{id}"
        response = self.api.request("DELETE", url, headers=headers)
        data = response.json()
        return HeroObject(data)

    def update_experiment_tag(self, experiment_id, key, value):
        """
        Updates a tag for the given experiment ID

        Parameters
        ----------
        experiment_id : str
            The ID of the experiment to update the tag for
        key : str
            The key of the tag to update
        value : str
            The new value for the tag

        Returns
        -------
        tag : dict
            The updated tag

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if experiment_id is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "experiment_id"'
            )
        if key is None:
            raise MissingRequiredAttribute('Missing required attribute: "key"')
        if value is None:
            raise MissingRequiredAttribute('Missing required attribute: "value"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/experiment/{experiment_id}/tag"
        attributes = {"key": key, "value": value}
        response = self.api.request("POST", url, headers=headers, json=attributes)
        data = response.json()
        return HeroObject(data)

    def delete_experiment_tag(self, experiment_id, key):
        """
        Deletes a tag for the given experiment ID

        Parameters
        ----------
        experiment_id : str
            The ID of the experiment to delete the tag for
        key : str
            The key of the tag to delete

        Returns
        -------
        tag : dict
            The deleted tag

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if experiment_id is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "experiment_id"'
            )
        if key is None:
            raise MissingRequiredAttribute('Missing required attribute: "key"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/experiment/{experiment_id}/tag"
        attributes = {"key": key}
        response = self.api.request("DELETE", url, headers=headers, json=attributes)
        data = response.json()
        return HeroObject(data)

    def list_logged_models(self, experiment_id):
        """
        Lists the logged models for a given experiment ID

        Parameters
        ----------
        experiment_id : str
            The ID of the experiment to list logged models for

        Returns
        -------
        logged_model_collection : dict
            The collection of logged models for the given experiment ID

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
        url = f"{self.base_url}/project/{self.registry_name}/experiment/{experiment_id}/logged-models"
        response = self.api.request("GET", url, headers=headers)
        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "logged_models" in data:
                return HeroObject(data).logged_models
            if "items" in data:
                return HeroObject(data).items
            # empty dict or unknown shape -> empty list
            return []
        # Fallback: unknown type -> empty list
        return []

    def read_logged_model(self, id):
        """
        Reads a logged model for a given logged model ID

        Parameters
        ----------
        id : str
            The ID of the logged model to read
        id : str
            The ID of the logged model to read

        Returns
        -------
        logged_model : dict
            The logged model with the given ID

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """

        if id is None:
            raise MissingRequiredAttribute('Missing required attribute: "id"')
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/logged-model/{id}"
        response = self.api.request("GET", url, headers=headers)
        data = response.json()
        if isinstance(data, dict) and "model" in data:
            return HeroObject(data).model
        return HeroObject(data)

    def read_bulk_metric_history(
        self, experiment_id, run_ids, metric, count=None, next_token=None
    ):
        """
        Reads the history of a metric for multiple run IDs in the model registry

        Parameters
        ----------
        experiment_id : str
            The ID of the experiment to which the runs belong
        run_ids : list
            The list of run IDs to read metric history for
        metric : str
            The name of the metric to read history for
        count : int, optional
            The number of metrics to return, by default None
        next_token : str, optional
            The token for the next page of metrics, by default None

        Returns
        -------
        metric_history : dict
            The history of the metric for the given run IDs

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if experiment_id is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "experiment_id"'
            )
        if not run_ids:
            raise MissingRequiredAttribute('Missing required attribute: "run_ids"')
        if metric is None:
            raise MissingRequiredAttribute('Missing required attribute: "metric"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/experiment/{experiment_id}/bulk-history"
        params = {
            "count": count,
            "nextToken": next_token,
            "metric": metric,
            "runIds": run_ids,
        }
        response = self.api.request("GET", url, headers=headers, params=params)
        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "metrics" in data:
                return HeroObject(data).metrics
            return []
        return []

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
        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "runs" in data:
                return HeroObject(data).runs
            return []
        return []

    def read_run(self, id):
        """
        Reads the run with the given ID

        Parameters
        ----------
        id : str
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
        if id is None:
            raise MissingRequiredAttribute('Missing required attribute: "id"')
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/run/{id}"
        response = self.api.request("GET", url, headers=headers)
        data = response.json()
        if isinstance(data, dict) and "run" in data:
            return HeroObject(data).run
        return HeroObject(data)

    def update_run(self, id, name=None, description=None):
        """
        Updates a run in the model registry

        Parameters
        ----------
        id : str
            The ID of the run to update
        name : str, optional
            The new name for the run, by default None
        description : str, optional
            The new description for the run, by default None

        Returns
        -------
        run : dict
            The updated run

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if id is None:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        attributes = {}
        if name is not None:
            attributes["name"] = name
        if description is not None:
            attributes["description"] = description

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/run/{id}"
        response = self.api.request("PUT", url, headers=headers, json=attributes)
        data = response.json()
        if isinstance(data, dict) and "run" in data:
            return HeroObject(data).run
        return HeroObject(data)

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
        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "metrics" in data:
                return HeroObject(data).metrics
            return []
        return []

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
        data = response.json()
        return HeroObject(data)

    def update_run_tag(self, run_id, key, value):
        """
        Updates a tag for a given run ID

        Parameters
        ----------
        run_id : str
            The ID of the run to update the tag for
        key : str
            The key of the tag to update
        value : str
            The new value for the tag

        Returns
        -------
        tag : dict
            The updated tag

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if run_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "run_id"')
        if key is None:
            raise MissingRequiredAttribute('Missing required attribute: "key"')
        if value is None:
            raise MissingRequiredAttribute('Missing required attribute: "value"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/run/{run_id}/tag"
        attributes = {"key": key, "value": value}
        response = self.api.request("POST", url, headers=headers, json=attributes)
        data = response.json()
        return HeroObject(data)

    def delete_run_tag(self, run_id, key):
        """
        Deletes a tag for a given run ID

        Parameters
        ----------
        run_id : str
            The ID of the run to delete the tag for
        key : str
            The key of the tag to delete

        Returns
        -------
        tag : dict
            The deleted tag

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if run_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "run_id"')
        if key is None:
            raise MissingRequiredAttribute('Missing required attribute: "key"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/run/{run_id}/tag"
        attributes = {"key": key}
        response = self.api.request("DELETE", url, headers=headers, json=attributes)
        data = response.json()
        return HeroObject(data)

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
        data = response.json()
        return data if isinstance(data, list) else HeroObject(data)

    def list_logged_model_artifacts(self, model_id):
        """
        Lists the artifacts for a given logged model ID

        Parameters
        ----------
        model_id : str
            The ID of the logged model to list artifacts for

        Returns
        -------
        artifact_collection : dict
            The collection of artifacts for the given logged model ID

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if model_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "model_id"')
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/logged-model/{model_id}/artifacts"
        response = self.api.request("GET", url, headers=headers)
        data = response.json()
        return data if isinstance(data, list) else HeroObject(data)

    def create_registered_model(self, id):
        """
        Creates a registered model in the model registry

        Parameters
        ----------
        id : str
            Name/ID of the model

        Returns
        -------
        dict
            The created registered model

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROMLModelRegistryResourceAlreadyExists
            If the model with the given ID already exists
        """
        if not id:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/model/{id}"
        try:
            response = self.api.request("POST", url, headers=headers)
            data = response.json()
            if isinstance(data, dict) and "registered_model" in data:
                return HeroObject(data).registered_model
            return HeroObject(data)
        except HTTPError as e:
            if (
                getattr(e, "response", None) is not None
                and e.response.status_code == 409
            ):
                raise HEROMLModelRegistryResourceAlreadyExists()
            if getattr(e, "response", None) is not None:
                self._raise_forbidden_from_http_error(e, "create_registered_model")
            else:
                raise e

    def list_registered_models(
        self, count=None, next_token=None, search_key=None, sort_order=None, filter=None
    ):
        """
        Lists the registered models in the model registry

        Parameters
        ----------
        count : int, optional
            Number of models to return, by default None
        next_token : str, optional
            Token for the next page of models, by default None
        search_key : str, optional
            Key to search for in the models (API defaults to 'name'), by default None
        sort_order : str, optional
            Order to sort the models by (API defaults to 'ASC'), by default None
        filter : str, optional
            Filter to apply to the models, by default None

        Returns
        -------
        dict
            The collection of models in the registry

        """

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/models"
        params = {
            "count": count,
            "nextToken": next_token,
            "searchKey": search_key,
            "sortOrder": sort_order,
            "filter": filter,
        }
        response = self.api.request("GET", url, headers=headers, params=params)
        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "registered_models" in data:
                return HeroObject(data).registered_models
            return []
        return []

    def read_registered_model(self, id):
        """
        Reads a registered model in the model registry

        Parameters
        ----------
        id : str
            The ID of the model to read

        Returns
        -------
        dict
            The model with the given ID

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROMLModelRegistryResourceNotFound
            If the model with the given ID is not found
        """
        if not id:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/model/{id}"
        try:
            response = self.api.request("GET", url, headers=headers)
            data = response.json()
            return HeroObject(data).registered_model
        except HTTPError as e:
            if e.response.status_code == 404:
                raise HEROMLModelRegistryResourceNotFound()
            if getattr(e, "response", None) is not None:
                self._raise_forbidden_from_http_error(e, "read_registered_model")
            else:
                raise e

    def read_or_create_registered_model(self, id):
        """
        Reads a registered model in the model registry, or creates it if it does not exist

        Parameters
        ----------
        id : str
            The ID of the model to read or create

        Returns
        -------
        dict
            The model with the given ID

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        HEROMLModelRegistryForbiddenError
            If access is denied (e.g., model belongs to another project)
        """
        try:
            return self.read_registered_model(id)
        except HEROMLModelRegistryResourceNotFound:
            # Model doesn't exist, try to create it
            return self.create_registered_model(id)
        except HEROMLModelRegistryForbiddenError:
            # Access denied (e.g., cross-project ownership) - don't try to create
            raise

    def rename_registered_model(self, id, new_name):
        """
        Renames a model in the model registry

        Parameters
        ----------
        id : str
            The ID of the model to rename
        new_name : str
            The new name for the model

        Returns
        -------
        dict
            The updated model

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if not id:
            raise MissingRequiredAttribute('Missing required attribute: "id"')
        if not new_name:
            raise MissingRequiredAttribute('Missing required attribute: "new_name"')
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/model/{id}"
        attributes = {"newName": new_name}
        response = self.api.request("PUT", url, headers=headers, json=attributes)
        data = response.json()
        if isinstance(data, dict) and "registered_model" in data:
            return HeroObject(data).registered_model
        return HeroObject(data)

    def update_registered_model(self, id, description=None, deployment_job_id=None):
        """
        Updates a registered model in the model registry

        Parameters
        ----------
        id : str
            The ID of the model to update
        description : str, optional
            The new description for the model, by default None
        deployment_job_id : str, optional
            The ID of the deployment job associated with the model, by default None

        Returns
        -------
        dict
            The updated model

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if not id:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/model/{id}"
        attributes = {}
        if description is not None:
            attributes["description"] = description
        if deployment_job_id is not None:
            attributes["deploymentJobId"] = deployment_job_id
        response = self.api.request("PUT", url, headers=headers, json=attributes)
        data = response.json()
        if isinstance(data, dict) and "registered_model" in data:
            return HeroObject(data).registered_model
        return HeroObject(data)

    def delete_registered_model(self, id):
        """
        Deletes a registered model in the model registry

        Parameters
        ----------
        id : str
            The ID of the model to delete

        Returns
        -------
        dict
            The deleted model

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if not id:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/model/{id}"
        response = self.api.request("DELETE", url, headers=headers)
        data = response.json()
        return HeroObject(data)

    def update_registered_model_tag(self, model_id, key, value):
        """
        Updates a tag for a registered model in the model registry

        Parameters
        ----------
        model_id : str
            The ID of the model to update the tag for
        key : str
            The key of the tag to update
        value : str
            The new value for the tag

        Returns
        -------
        dict
            The updated tag

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if not model_id:
            raise MissingRequiredAttribute('Missing required attribute: "model_id"')
        if not key:
            raise MissingRequiredAttribute('Missing required attribute: "key"')
        if not value:
            raise MissingRequiredAttribute('Missing required attribute: "value"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/model/{model_id}/tag"
        attributes = {"key": key, "value": value}
        response = self.api.request("POST", url, headers=headers, json=attributes)
        data = response.json()
        return HeroObject(data)

    def delete_registered_model_tag(self, model_id, key):
        """
        Deletes a tag for a registered model in the model registry

        Parameters
        ----------
        model_id : str
            The ID of the model to delete the tag for
        key : str
            The key of the tag to delete

        Returns
        -------
        dict
            The deleted tag

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if not model_id:
            raise MissingRequiredAttribute('Missing required attribute: "model_id"')
        if not key:
            raise MissingRequiredAttribute('Missing required attribute: "key"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/model/{model_id}/tag"
        attributes = {"key": key}
        response = self.api.request("DELETE", url, headers=headers, json=attributes)
        data = response.json()
        return HeroObject(data)

    def create_registered_model_version(self, model_id, run_id, source):
        """
        Creates a registered model version in the model registry

        Parameters
        ----------
        model_id : str
            The ID of the model to create the version for
        run_id : str
            The ID of the run associated with the model version
        source : str
            The source location of the model version

        Returns
        -------
        dict
            The created model version

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if not model_id:
            raise MissingRequiredAttribute('Missing required attribute: "model_id"')
        if not run_id:
            raise MissingRequiredAttribute('Missing required attribute: "run_id"')
        if not source:
            raise MissingRequiredAttribute('Missing required attribute: "source"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/model/{model_id}/version"
        attributes = {"runId": run_id, "source": source}
        response = self.api.request("POST", url, headers=headers, json=attributes)
        data = response.json()
        if isinstance(data, dict) and "model_version" in data:
            return HeroObject(data).model_version
        return HeroObject(data)

    def list_registered_model_versions(self, model_id):
        """
        Lists the versions of a registered model in the model registry

        Parameters
        ----------
        model_id : str
            The ID of the model to list versions for

        Returns
        -------
        dict
            The collection of model versions

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if not model_id:
            raise MissingRequiredAttribute('Missing required attribute: "model_id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/versions"
        response = self.api.request("GET", url, headers=headers)
        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "model_versions" in data:
                return HeroObject(data).model_versions
            return []
        return []

    def read_registered_model_version(self, model_id, id):
        """
        Reads a registered model version in the model registry

        Parameters
        ----------
        model_id : str
            The ID of the model to read the version for
        id : str
            The ID of the model version to read

        Returns
        -------
        dict
            The model version with the given ID

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if not model_id:
            raise MissingRequiredAttribute('Missing required attribute: "model_id"')
        if not id:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/model/{model_id}/version/{id}"
        response = self.api.request("GET", url, headers=headers)
        data = response.json()
        if isinstance(data, dict) and "model_version" in data:
            return HeroObject(data).model_version
        return HeroObject(data)

    def update_registered_model_version(self, model_id, id, description=None):
        """
        Updates a registered model version in the model registry

        Parameters
        ----------
        model_id : str
            The ID of the model to update the version for
        id : str
            The ID of the model version to update
        description : str, optional
            The new description for the model version, by default None

        Returns
        -------
        dict
            The updated model version

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if not model_id:
            raise MissingRequiredAttribute('Missing required attribute: "model_id"')
        if not id:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/model/{model_id}/version/{id}"
        attributes = {"description": description}
        response = self.api.request("PUT", url, headers=headers, json=attributes)
        data = response.json()
        if isinstance(data, dict) and "model_version" in data:
            return HeroObject(data).model_version
        return HeroObject(data)

    def delete_registered_model_version(self, model_id, id):
        """
        Deletes a registered model version in the model registry

        Parameters
        ----------
        model_id : str
            The ID of the model to delete the version for
        id : str
            The ID of the model version to delete

        Returns
        -------
        dict
            The deleted model version

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        if not model_id:
            raise MissingRequiredAttribute('Missing required attribute: "model_id"')
        if not id:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/model/{model_id}/version/{id}"
        response = self.api.request("DELETE", url, headers=headers)
        data = response.json()
        if isinstance(data, dict) and "model_version" in data:
            return HeroObject(data).model_version
        return HeroObject(data)

    def update_registered_model_version_tag(self, model_id, id, key, value):
        """
        Updates a tag for a registered model version in the model registry

        Parameters
        ----------
        model_id : str
            The ID of the model to update the version for
        id : str
            The ID of the model version to update the tag for
        key : str
            The key of the tag to update
        value : str
            The new value for the tag

        Returns
        -------
        dict
            The updated model version tag
        """
        if not model_id:
            raise MissingRequiredAttribute('Missing required attribute: "model_id"')
        if not id:
            raise MissingRequiredAttribute('Missing required attribute: "id"')
        if not key:
            raise MissingRequiredAttribute('Missing required attribute: "key"')
        if not value:
            raise MissingRequiredAttribute('Missing required attribute: "value"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/model/{model_id}/version/{id}/tag"
        response = self.api.request(
            "POST", url, headers=headers, json={"key": key, "value": value}
        )
        data = response.json()
        return HeroObject(data)

    def delete_registered_model_version_tag(self, model_id, id, key):
        """
        Deletes a tag for a registered model version in the model registry

        Parameters
        ----------
        model_id : str
            The ID of the model to delete the version tag for
        id : str
            The ID of the model version to delete the tag for
        key : str
            The key of the tag to delete

        Returns
        -------
        dict
            The deleted model version tag
        """
        if not model_id:
            raise MissingRequiredAttribute('Missing required attribute: "model_id"')
        if not id:
            raise MissingRequiredAttribute('Missing required attribute: "id"')
        if not key:
            raise MissingRequiredAttribute('Missing required attribute: "key"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/project/{self.registry_name}/model/{model_id}/version/{id}/tag"
        response = self.api.request("DELETE", url, headers=headers, json={"key": key})
        data = response.json()
        return HeroObject(data)

    # ============================================================================
    # Model State Management Methods
    # ============================================================================

    def set_model_state(
        self,
        model_id,
        version,
        state,
        metadata=None,
    ):
        """
        Sets the state of a model version with optional metadata.

        Parameters
        ----------
        model_id : str
            The ID of the registered model
        version : str
            The version number of the model
        state : str
            The state to set. Valid states: 'registered', 'packaging', 'packaged',
            'validating', 'deploying', 'deployed', 'deprecated', 'archived', 'error'
        metadata : dict, optional
            Additional metadata to store with the state, by default None

        Returns
        -------
        dict
            Result of the tag update operation

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        ValueError
            If an invalid state is provided
        """
        valid_states = [
            "registered",
            "packaging",
            "packaged",
            "validating",
            "deploying",
            "deployed",
            "deprecated",
            "archived",
            "error",
        ]

        if state not in valid_states:
            raise ValueError(
                f"Invalid state '{state}'. Must be one of: {', '.join(valid_states)}"
            )

        # Set the main state tag
        result = self.update_registered_model_version_tag(
            model_id, version, "mmr.state", state
        )

        # Set metadata if provided
        if metadata:
            for key, value in metadata.items():
                self.update_registered_model_version_tag(
                    model_id, version, f"mmr.state.{key}", str(value)
                )

        return result

    def get_model_state(self, model_id, version):
        """
        Gets the current state and metadata of a model version.

        Parameters
        ----------
        model_id : str
            The ID of the registered model
        version : str
            The version number of the model

        Returns
        -------
        dict
            Dictionary containing 'state' and 'metadata' keys with state information

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        """
        model_version = self.read_registered_model_version(model_id, version)

        state = None
        metadata = {}

        # Extract state and metadata from tags
        if hasattr(model_version, "tags") and model_version.tags:
            for tag in model_version.tags:
                if tag.get("key") == "mmr.state":
                    state = tag.get("value")
                elif tag.get("key", "").startswith("mmr.state."):
                    # Extract metadata key (remove 'mmr.state.' prefix)
                    meta_key = tag.get("key")[10:]  # len('mmr.state.') = 10
                    metadata[meta_key] = tag.get("value")

        return {"state": state, "metadata": metadata}

    def set_model_packaging(self, model_id, version):
        """
        Sets the model state to 'packaging'.

        Parameters
        ----------
        model_id : str
            The ID of the registered model
        version : str
            The version number of the model

        Returns
        -------
        dict
            Result of the state update operation
        """
        from datetime import datetime

        return self.set_model_state(
            model_id,
            version,
            "packaging",
            metadata={"timestamp": datetime.utcnow().isoformat()},
        )

    def set_model_packaged(
        self, model_id, version, container_uri, container_digest=None, registry=None
    ):
        """
        Sets the model state to 'packaged' with container information.

        Parameters
        ----------
        model_id : str
            The ID of the registered model
        version : str
            The version number of the model
        container_uri : str
            The full URI of the container image
        container_digest : str, optional
            The SHA256 digest of the container for immutability, by default None
        registry : str, optional
            The container registry name (e.g., 'ECR', 'GCR', 'ACR'), by default None

        Returns
        -------
        dict
            Result of the state update operation

        Raises
        ------
        MissingRequiredAttribute
            If container_uri is not provided
        """
        if not container_uri:
            raise MissingRequiredAttribute(
                'Missing required attribute: "container_uri"'
            )

        from datetime import datetime

        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Set container-specific tags separately for better organization
        self.update_registered_model_version_tag(
            model_id, version, "mmr.container.uri", container_uri
        )

        if container_digest:
            self.update_registered_model_version_tag(
                model_id, version, "mmr.container.digest", container_digest
            )

        if registry:
            self.update_registered_model_version_tag(
                model_id, version, "mmr.container.registry", registry
            )

        return self.set_model_state(model_id, version, "packaged", metadata=metadata)

    def set_model_validating(self, model_id, version):
        """
        Sets the model state to 'validating'.

        Parameters
        ----------
        model_id : str
            The ID of the registered model
        version : str
            The version number of the model

        Returns
        -------
        dict
            Result of the state update operation
        """
        from datetime import datetime

        return self.set_model_state(
            model_id,
            version,
            "validating",
            metadata={"timestamp": datetime.utcnow().isoformat()},
        )

    def set_model_deploying(self, model_id, version, environment=None):
        """
        Sets the model state to 'deploying'.

        Parameters
        ----------
        model_id : str
            The ID of the registered model
        version : str
            The version number of the model
        environment : str, optional
            The deployment environment (e.g., 'dev', 'staging', 'prod'), by default None

        Returns
        -------
        dict
            Result of the state update operation
        """
        from datetime import datetime

        metadata = {"timestamp": datetime.utcnow().isoformat()}

        if environment:
            self.update_registered_model_version_tag(
                model_id, version, "mmr.deployment.environment", environment
            )

        return self.set_model_state(model_id, version, "deploying", metadata=metadata)

    def set_model_deployed(
        self,
        model_id,
        version,
        deployment_type,
        endpoint=None,
        queue=None,
        environment=None,
    ):
        """
        Sets the model state to 'deployed' with deployment information.

        Parameters
        ----------
        model_id : str
            The ID of the registered model
        version : str
            The version number of the model
        deployment_type : str
            The type of deployment ('webservice', 'batch', 'streaming', 'edge')
        endpoint : str, optional
            The HTTP endpoint URL for webservice deployments, by default None
        queue : str, optional
            The queue name/ARN for event-driven deployments, by default None
        environment : str, optional
            The deployment environment (e.g., 'dev', 'staging', 'prod'), by default None

        Returns
        -------
        dict
            Result of the state update operation

        Raises
        ------
        MissingRequiredAttribute
            If deployment_type is not provided
        ValueError
            If an invalid deployment_type is provided
        """
        if not deployment_type:
            raise MissingRequiredAttribute(
                'Missing required attribute: "deployment_type"'
            )

        valid_deployment_types = ["webservice", "batch", "streaming", "edge"]
        if deployment_type not in valid_deployment_types:
            raise ValueError(
                f"Invalid deployment_type '{deployment_type}'. Must be one of: {', '.join(valid_deployment_types)}"
            )

        from datetime import datetime

        metadata = {"timestamp": datetime.utcnow().isoformat()}

        # Set deployment-specific tags
        self.update_registered_model_version_tag(
            model_id, version, "mmr.deployment.type", deployment_type
        )

        if endpoint:
            self.update_registered_model_version_tag(
                model_id, version, "mmr.deployment.endpoint", endpoint
            )

        if queue:
            self.update_registered_model_version_tag(
                model_id, version, "mmr.deployment.queue", queue
            )

        if environment:
            self.update_registered_model_version_tag(
                model_id, version, "mmr.deployment.environment", environment
            )

        return self.set_model_state(model_id, version, "deployed", metadata=metadata)

    def set_model_error(self, model_id, version, error_message, error_stage=None):
        """
        Sets the model state to 'error' with error information.

        Parameters
        ----------
        model_id : str
            The ID of the registered model
        version : str
            The version number of the model
        error_message : str
            The error message describing what went wrong
        error_stage : str, optional
            The stage where the error occurred, by default None

        Returns
        -------
        dict
            Result of the state update operation

        Raises
        ------
        MissingRequiredAttribute
            If error_message is not provided
        """
        if not error_message:
            raise MissingRequiredAttribute(
                'Missing required attribute: "error_message"'
            )

        from datetime import datetime

        metadata = {"timestamp": datetime.utcnow().isoformat()}

        # Set error-specific tags
        self.update_registered_model_version_tag(
            model_id, version, "mmr.error.message", error_message
        )

        if error_stage:
            self.update_registered_model_version_tag(
                model_id, version, "mmr.error.stage", error_stage
            )

        return self.set_model_state(model_id, version, "error", metadata=metadata)

    def clear_model_error(self, model_id, version):
        """
        Clears error state and metadata from a model version.

        Parameters
        ----------
        model_id : str
            The ID of the registered model
        version : str
            The version number of the model

        Returns
        -------
        dict
            Result of clearing error tags
        """
        # Delete error-related tags
        try:
            self.delete_registered_model_version_tag(
                model_id, version, "mmr.error.message"
            )
        except Exception:
            pass  # Tag may not exist

        try:
            self.delete_registered_model_version_tag(
                model_id, version, "mmr.error.stage"
            )
        except Exception:
            pass  # Tag may not exist

        try:
            self.delete_registered_model_version_tag(
                model_id, version, "mmr.error.timestamp"
            )
        except Exception:
            pass  # Tag may not exist

        # Return the current state
        return self.get_model_state(model_id, version)

    def set_model_deprecated(self, model_id, version, reason=None):
        """
        Sets the model state to 'deprecated'.

        Parameters
        ----------
        model_id : str
            The ID of the registered model
        version : str
            The version number of the model
        reason : str, optional
            The reason for deprecation, by default None

        Returns
        -------
        dict
            Result of the state update operation
        """
        from datetime import datetime

        metadata = {"timestamp": datetime.utcnow().isoformat()}

        if reason:
            metadata["reason"] = reason

        return self.set_model_state(model_id, version, "deprecated", metadata=metadata)

    def set_model_archived(self, model_id, version, reason=None):
        """
        Sets the model state to 'archived'.

        Parameters
        ----------
        model_id : str
            The ID of the registered model
        version : str
            The version number of the model
        reason : str, optional
            The reason for archiving, by default None

        Returns
        -------
        dict
            Result of the state update operation
        """
        from datetime import datetime

        metadata = {"timestamp": datetime.utcnow().isoformat()}

        if reason:
            metadata["reason"] = reason

        return self.set_model_state(model_id, version, "archived", metadata=metadata)

    def set_monitoring_config(
        self,
        model_id,
        version,
        enabled=True,
        drift_threshold=None,
        metrics=None,
    ):
        """
        Configures monitoring settings for a model version.

        Parameters
        ----------
        model_id : str
            The ID of the registered model
        version : str
            The version number of the model
        enabled : bool, optional
            Whether monitoring is enabled, by default True
        drift_threshold : float, optional
            The threshold for data drift detection, by default None
        metrics : dict, optional
            Latest evaluation metrics as a dictionary, by default None

        Returns
        -------
        dict
            Result of the monitoring configuration
        """
        self.update_registered_model_version_tag(
            model_id, version, "mmr.monitoring.enabled", str(enabled).lower()
        )

        if drift_threshold is not None:
            self.update_registered_model_version_tag(
                model_id,
                version,
                "mmr.monitoring.drift_threshold",
                str(drift_threshold),
            )

        if metrics:
            # Store metrics as JSON string
            self.update_registered_model_version_tag(
                model_id, version, "mmr.evaluation.metrics", json.dumps(metrics)
            )

        from datetime import datetime

        self.update_registered_model_version_tag(
            model_id,
            version,
            "mmr.evaluation.last_run",
            datetime.utcnow().isoformat(),
        )

        return {"monitoring_enabled": enabled}

    def get_monitoring_config(self, model_id, version):
        """
        Gets the monitoring configuration for a model version.

        Parameters
        ----------
        model_id : str
            The ID of the registered model
        version : str
            The version number of the model

        Returns
        -------
        dict
            Dictionary containing monitoring configuration
        """
        model_version = self.read_registered_model_version(model_id, version)

        config = {
            "enabled": False,
            "drift_threshold": None,
            "metrics": None,
            "last_evaluation": None,
        }

        # Extract monitoring config from tags
        if hasattr(model_version, "tags") and model_version.tags:
            for tag in model_version.tags:
                key = tag.get("key", "")
                value = tag.get("value")

                if key == "mmr.monitoring.enabled":
                    config["enabled"] = value.lower() == "true"
                elif key == "mmr.monitoring.drift_threshold":
                    config["drift_threshold"] = float(value)
                elif key == "mmr.evaluation.metrics":
                    try:
                        config["metrics"] = json.loads(value)
                    except json.JSONDecodeError:
                        config["metrics"] = value
                elif key == "mmr.evaluation.last_run":
                    config["last_evaluation"] = value

        return config

    def set_approval_status(
        self, model_id, version, status, required=False, approver=None
    ):
        """
        Sets the approval status for a model version.

        Parameters
        ----------
        model_id : str
            The ID of the registered model
        version : str
            The version number of the model
        status : str
            The approval status ('pending', 'approved', 'rejected')
        required : bool, optional
            Whether approval is required, by default False
        approver : str, optional
            The username/email of the approver, by default None

        Returns
        -------
        dict
            Result of the approval status update

        Raises
        ------
        ValueError
            If an invalid approval status is provided
        """
        valid_statuses = ["pending", "approved", "rejected"]
        if status not in valid_statuses:
            raise ValueError(
                f"Invalid approval status '{status}'. Must be one of: {', '.join(valid_statuses)}"
            )

        self.update_registered_model_version_tag(
            model_id, version, "mmr.approval.status", status
        )

        self.update_registered_model_version_tag(
            model_id, version, "mmr.approval.required", str(required).lower()
        )

        if approver:
            self.update_registered_model_version_tag(
                model_id, version, "mmr.approval.approver", approver
            )

        from datetime import datetime

        self.update_registered_model_version_tag(
            model_id, version, "mmr.approval.timestamp", datetime.utcnow().isoformat()
        )

        return {"approval_status": status, "required": required}

    def set_rollback_info(self, model_id, version, previous_version):
        """
        Sets rollback information for a model version.

        Parameters
        ----------
        model_id : str
            The ID of the registered model
        version : str
            The version number of the model
        previous_version : str
            The previous version number to rollback to

        Returns
        -------
        dict
            Result of setting rollback information

        Raises
        ------
        MissingRequiredAttribute
            If previous_version is not provided
        """
        if not previous_version:
            raise MissingRequiredAttribute(
                'Missing required attribute: "previous_version"'
            )

        self.update_registered_model_version_tag(
            model_id, version, "mmr.rollback.previous_version", previous_version
        )

        return {"rollback_target": previous_version}

    def set_canary_deployment(self, model_id, version, percentage):
        """
        Sets canary deployment configuration for a model version.

        Parameters
        ----------
        model_id : str
            The ID of the registered model
        version : str
            The version number of the model
        percentage : int or float
            The percentage of traffic to route to this version (0-100)

        Returns
        -------
        dict
            Result of setting canary deployment

        Raises
        ------
        ValueError
            If percentage is not between 0 and 100
        """
        if not 0 <= percentage <= 100:
            raise ValueError("Percentage must be between 0 and 100")

        self.update_registered_model_version_tag(
            model_id, version, "mmr.canary.percentage", str(percentage)
        )

        from datetime import datetime

        self.update_registered_model_version_tag(
            model_id, version, "mmr.canary.timestamp", datetime.utcnow().isoformat()
        )

        return {"canary_percentage": percentage}
