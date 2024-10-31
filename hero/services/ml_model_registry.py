import json
import os
from tqdm import tqdm
import requests

from ..url_map import URL_MAP
from ..lib import ServiceBase, decorate_all, log_errors, get_conf_from_collection


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

    def read_experiment(self, experiment_id):
        """
        Reads the experiment with the given ID
        """
        headers = self.get_headers(self.client.get_token())
        url = (
            f"{self.base_url}/registry/{self.registry_name}/experiment/{experiment_id}"
        )
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def update_experiment(self, experiment_id, attributes):
        """
        Updates the experiment with the given ID
        Note: Only `name` can be updated
        """
        headers = self.get_headers(self.client.get_token())
        url = (
            f"{self.base_url}/registry/{self.registry_name}/experiment/{experiment_id}"
        )
        data = json.dumps(attributes)
        response = self.api.request("PUT", url, headers=headers, json=data)
        return response.json()

    def delete_experiment(self, experiment_id):
        """
        Deletes the experiment with the given ID
        """
        headers = self.get_headers(self.client.get_token())
        url = (
            f"{self.base_url}/registry/{self.registry_name}/experiment/{experiment_id}"
        )
        response = self.api.request("DELETE", url, headers=headers)
        return response.json()

    def read_run(self, run_id):
        """
        Reads the run with the given ID
        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/registry/{self.registry_name}/run/{run_id}"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def delete_run(self, run_id):
        """
        Deletes the run with the given ID
        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/registry/{self.registry_name}/run/{run_id}"
        response = self.api.request("DELETE", url, headers=headers)
        return response.json()

    def list_artifacts(self, run_id):
        """
        Lists the artifacts for a given run ID
        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/registry/{self.registry_name}/run/{run_id}/artifacts"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def download_artifact(self, run_id, local_path, artifact_path):
        """
        Downloads the artifact from the given run ID
        """
        try:
            print(f'Downloading artifact "{artifact_path}"...')
            headers = self.get_headers(self.client.get_token())
            url = (
                f"{self.base_url}/registry/{self.registry_name}/run/{run_id}/artifact/"
            )
            params = {"artifactPath": artifact_path}
            response = self.api.request("GET", url, headers=headers, params=params)

            local_path = os.path.join(local_path, artifact_path)

            # Create the directories if they do not exist
            directory = os.path.dirname(local_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Get the total file size from the headers
            total_size = int(response.headers.get("content-length", 0))

            # Open the file in write-binary mode
            with open(local_path, "wb") as file, tqdm(
                desc=local_path,
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(chunk_size=10000):
                    if chunk:
                        file.write(chunk)
                        bar.update(len(chunk))
            print(f"File downloaded successfully and saved to {local_path}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading file: {e}")

    def download_artifacts(self, run_id, local_path):
        """
        Downloads the artifacts from the given run ID
        """
        artifacts = self.list_artifacts(run_id)
        for artifact in artifacts:
            artifact_path = artifact["path"]
            self.download_artifact(run_id, local_path, artifact_path)

    def search_runs(
        self,
        experiment_ids,
        filter_string,
        run_view_type,
        max_results,
        order_by,
        page_token,
    ):
        """
        Searches the runs with the given parameters
        """
        # headers = self.get_headers(self.client.get_token())
        # url = f'{self.base_url}/registry/{self.registry_name}/runs/search'
        # data = {
        #     'experiment_ids': experiment_ids,
        #     'filter': filter_string,
        #     'run_view_type': run_view_type,
        #     'max_results': max_results,
        #     'order_by': order_by,
        #     'page_token': page_token
        # }
        # response = self.api.request('POST', url, headers=headers, json=data)
        # return response.json()
        pass
