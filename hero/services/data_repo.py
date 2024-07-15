import json

from ..url_map import URL_MAP
from ..lib import ServiceBase, decorate_all, log_errors, get_conf_from_collection

@decorate_all(log_errors)
class DataRepoService(ServiceBase):
    def _configure(self):
        '''
        Sets the API, adds data_repo id and required scope
        '''
        self.client.add_scope('data-repo/user')
        self.base_url = get_conf_from_collection(URL_MAP, 'HERO_DATA_REPO_API_URL')

    def read_projects(self, datarepo_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/projects'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    def read_project_datasets(self, datarepo_id, project_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/project/{project_id}/datasets'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    def read_project(self, datarepo_id, project_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/project/{project_id}'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    def delete_project(self, datarepo_id, project_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/project/{project_id}'
        response = self.api.request('DELETE', url, headers=headers)
        return response.json()

    def add_project(self, datarepo_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/project'
        data = json.dumps(attributes)
        response = self.api.request('POST', url, headers=headers, data=data)
        return response.json()

    def update_project(self, datarepo_id, project_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/project/{project_id}'
        data = json.dumps(attributes)
        response = self.api.request('PUT', url, headers=headers, data=data)
        return response.json()

    def read_datasets(self, datarepo_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/datasets'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    def read_dataset(self, datarepo_id, dataset_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/dataset/{dataset_id}'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    def read_dataset_files(self, datarepo_id, dataset_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/dataset/{dataset_id}/files'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    def delete_dataset(self, datarepo_id, dataset_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/dataset/{dataset_id}'
        response = self.api.request('DELETE', url, headers=headers)
        return response.json()

    def add_dataset(self, datarepo_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/dataset'
        data = json.dumps(attributes)
        response = self.api.request('POST', url, headers=headers, data=data)
        return response.json()

    def update_dataset(self, datarepo_id, dataset_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/dataset/{dataset_id}'
        data = json.dumps(attributes)
        response = self.api.request('PUT', url, headers=headers, data=data)
        return response.json()

    def read_files(self, datarepo_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/files'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    def read_file(self, datarepo_id, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/file/{file_id}'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    def read_file_download_url(self, datarepo_id, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/files/download/{file_id}'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    def download_file(self, url):
        response = self.api.request('GET', url)
        return response.json()

    def delete_file(self, datarepo_id, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/file/{file_id}'
        response = self.api.request('DELETE', url, headers=headers)
        return response.json()

    def add_file(self, datarepo_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/file'
        data = json.dumps(attributes)
        response = self.api.request('POST', url, headers=headers, data=data)
        return response.json()

    def update_file(self, datarepo_id, file_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/file/{file_id}'
        data = json.dumps(attributes)
        response = self.api.request('PUT', url, headers=headers, data=data)
        return response.json()

    def read_file_upload_url(self, datarepo_id, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/files/upload/{file_id}'
        response = self.api.request('GET', url, headers=headers)
        return response.json()


