import json
import os

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
        return f'{self.base_url}/{self.m3s_name}'

    def read_experiment(self, experiment_id):
        '''
        Reads the experiment with the given ID
        '''
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.m3s_name}/experiment/{experiment_id}'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    def update_experiment(self, experiment_id, attributes):
        '''
        Updates the experiment with the given ID
        Note: Only `name` can be updated
        '''
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.m3s_name}/experiment/{experiment_id}'
        data = json.dumps(attributes)
        response = self.api.request('PUT', url, headers=headers, json=data)
        return response.json()

    def delete_experiment(self, experiment_id):
        '''
        Deletes the experiment with the given ID
        '''
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.m3s_name}/experiment/{experiment_id}'
        response = self.api.request('DELETE', url, headers=headers)
        return response.json()

    def read_run(self, run_id):
        '''
        Reads the run with the given ID
        '''
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.m3s_name}/run/{run_id}'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    def delete_run(self, run_id):
        '''
        Deletes the run with the given ID
        '''
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.m3s_name}/run/{run_id}'
        response = self.api.request('DELETE', url, headers=headers)
        return response.json()

    def list_artifacts(self, run_id):
        '''
        Lists the artifacts for a given run ID
        '''
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.m3s_name}/run/{run_id}/artifacts'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    def download_artifact(self, run_id, artifact_path, local_path):
        '''
        Downloads the artifact from the given run ID
        '''
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.m3s_name}/run/{run_id}/artifacts/{artifact_path}'
        response = self.api.request('GET', url, headers=headers)
        # TODO: Save the file to the local path
        return response.content

    def download_artifacts(self, run_id, artifact_path, local_path):
        '''
        Downloads the artifacts from the given run ID
        '''
        pass

    def search_runs(self, experiment_ids, filter_string, run_view_type, max_results, order_by, page_token):
        '''
        Searches the runs with the given parameters
        '''
        # headers = self.get_headers(self.client.get_token())
        # url = f'{self.base_url}/{self.m3s_name}/runs/search'
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



