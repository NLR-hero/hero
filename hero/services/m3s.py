import json
import os
from tqdm import tqdm
import requests

from ..url_map import URL_MAP
from ..lib import ServiceBase, get_conf_from_collection

class M3SService(ServiceBase):

    def __init__(self, clientInstance, m3s_name):
        if not m3s_name:
            raise ValueError('m3s_name must be provided')
        self.base_url = get_conf_from_collection(URL_MAP, 'HERO_M3S_TRACKER_URL')
        self.m3s_name = m3s_name
        super().__init__(clientInstance)

    def _configure(self):
        '''
        Sets the API and adds the user scope
        '''
        self.client.add_scope('m3s/user')

    def get_tracking_uri(self):
        '''
        Sets the MLFlow tracking token in the environment and returns the tracking URI
        '''
        os.environ['MLFLOW_TRACKING_TOKEN'] = self.client.get_token()
        return f'{self.base_url}/proxy/{self.m3s_name}'

    def read_experiment(self, experiment_id):
        '''
        Reads the experiment with the given ID
        '''
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/registry/{self.m3s_name}/experiment/{experiment_id}'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    def update_experiment(self, experiment_id, attributes):
        '''
        Updates the experiment with the given ID
        Note: Only `name` can be updated
        '''
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/registry/{self.m3s_name}/experiment/{experiment_id}'
        data = json.dumps(attributes)
        response = self.api.request('PUT', url, headers=headers, json=data)
        return response.json()

    def delete_experiment(self, experiment_id):
        '''
        Deletes the experiment with the given ID
        '''
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/registry/{self.m3s_name}/experiment/{experiment_id}'
        response = self.api.request('DELETE', url, headers=headers)
        return response.json()

    def read_run(self, run_id):
        '''
        Reads the run with the given ID
        '''
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/registry/{self.m3s_name}/run/{run_id}'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    def delete_run(self, run_id):
        '''
        Deletes the run with the given ID
        '''
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/registry/{self.m3s_name}/run/{run_id}'
        response = self.api.request('DELETE', url, headers=headers)
        return response.json()

    def list_artifacts(self, run_id):
        '''
        Lists the artifacts for a given run ID
        '''
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/registry/{self.m3s_name}/run/{run_id}/artifacts'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    def download_artifact(self, run_id, artifact_path, local_path):
        '''
        Downloads the artifact from the given run ID
        '''
        try:
            headers = self.get_headers(self.client.get_token())
            url = f'{self.base_url}/registry/{self.m3s_name}/run/{run_id}/artifacts/{artifact_path}'
            response = self.api.request('GET', url, headers=headers)

            # Get the total file size from the headers
            total_size = int(response.headers.get('content-length', 0))

            # Open the file in write-binary mode
            with open(local_path, 'wb') as file, tqdm(
                desc=local_path,
                total=total_size,
                unit='B',
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

    def download_artifacts(self, run_id, artifact_path, local_path):
        '''
        Downloads the artifacts from the given run ID
        '''
        artifacts = self.list_artifacts(self, run_id)
        for artifact in artifacts:
            artifact_path = artifact['path']
            save_path = os.path.join(local_path, artifact_path)
            self.download_artifact(run_id, artifact_path, save_path)

    def search_runs(self, experiment_ids, filter_string, run_view_type, max_results, order_by, page_token):
        '''
        Searches the runs with the given parameters
        '''
        # headers = self.get_headers(self.client.get_token())
        # url = f'{self.base_url}/registry/{self.m3s_name}/runs/search'
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



