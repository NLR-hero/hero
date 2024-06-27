import json

from ..lib import ServiceBase, decorate_all, log_errors
from ..config import get_data_repo_id

@decorate_all(log_errors)
class DataRepoService(ServiceBase):
    def _configure(self):
        '''
        Sets the API, adds data_repo id and required scope
        '''
        self._datarepo_id = get_data_repo_id()
        self.client.add_scope('data-repo/user')

    # export async function getProjects(setData, user, dataRepoId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${dataRepoId}/projects`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    def get_projects(self, datarepo_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{self.datarepo_id}/projects'
        response = self.api.request('GET', url, headers=headers)
        return response.json()


    # export async function getProjectDatasets(setData, user, dataRepoId, projectId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${dataRepoId}/project/${projectId}/datasets`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    #
    def get_project_datasets(self, datarepo_id, project_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/project/{project_id}/datasets'
        response = self.api.request('GET', url, headers=headers)
        return response.json()


    # export async function getProject(setData, user, dataRepoId, projectId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${dataRepoId}/project/${projectId}`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    def get_project(self, datarepo_id, project_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/project/{project_id}'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    # export async function deleteProject(user, dataRepoId, projectId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.delete(`${dataRepoId}/project/${projectId}`, {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def delete_project(self, datarepo_id, project_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/project/{project_id}'
        response = self.api.request('DELETE', url, headers=headers)
        return response.json()

    # export async function addProject(user, dataRepoId, attributes) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.post(`${dataRepoId}/project`,
    #     attributes,
    #     {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def add_project(self, datarepo_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/project'
        data = json.dumps(attributes)
        response = self.api.request('POST', url, headers=headers, data=data)
        return response.json()

    # export async function updateProject(user, dataRepoId, projectId, attributes) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.put(`${dataRepoId}/project/${projectId}`,
    #     attributes,
    #     {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def update_project(self, datarepo_id, project_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/project/{project_id}'
        data = json.dumps(attributes)
        response = self.api.request('PUT', url, headers=headers, data=data)
        return response.json()

    # export async function getDatasets(setData, user, dataRepoId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${dataRepoId}/datasets`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    def get_datasets(self, datarepo_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/datasets'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    # export async function getDataset(setData, user, dataRepoId, datasetId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${dataRepoId}/dataset/${datasetId}`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    def get_dataset(self, datarepo_id, dataset_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/dataset/{dataset_id}'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    # export async function getDatasetFiles(setData, user, dataRepoId, datasetId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${dataRepoId}/dataset/${datasetId}/files`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    def get_dataset_files(self, datarepo_id, dataset_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/dataset/{dataset_id}/files'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    # export async function deleteDataset(user, dataRepoId, datasetId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.delete(`${dataRepoId}/dataset/${datasetId}`, {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def delete_dataset(self, datarepo_id, dataset_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/dataset/{dataset_id}'
        response = self.api.request('DELETE', url, headers=headers)
        return response.json()

    # export async function addDataset(user, dataRepoId, attributes) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.post(`${dataRepoId}/dataset`,
    #     attributes,
    #     {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def add_dataset(self, datarepo_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/dataset'
        data = json.dumps(attributes)
        response = self.api.request('POST', url, headers=headers, data=data)
        return response.json()

    # export async function updateDataset(user, dataRepoId, datasetId, attributes) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.put(`${dataRepoId}/dataset/${datasetId}`,
    #     attributes,
    #     {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def update_dataset(self, datarepo_id, dataset_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/dataset/{dataset_id}'
        data = json.dumps(attributes)
        response = self.api.request('PUT', url, headers=headers, data=data)
        return response.json()

    # export async function getFiles(setData, user, dataRepoId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${dataRepoId}/files`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    def get_files(self, datarepo_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/files'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    # export async function getFile(setData, user, dataRepoId, fileId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${dataRepoId}/file/${fileId}`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    def get_file(self, datarepo_id, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/file/{file_id}'
        response = self.api.request('GET', url, headers=headers)
        return response.json()


    # /**
    # * Get file download url
    # */
    # export async function getFileDownloadUrl(setData, user, dataRepoId, file) {
    #     const requestHeaders = createRequestHeaders(user);
    #         const response = await api.get(`${dataRepoId}/files/download/${file.id}`, {
    #             headers: requestHeaders
    #         });
    #         console.log(response);
    #         setData(response.data.url);
    # }
    def get_file_download_url(self, datarepo_id, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/files/download/{file_id}'
        response = self.api.request('GET', url, headers=headers)
        return response.json()

    # /**
    # * Download file
    # */
    # export async function downloadFile(setData, url) {
    #     const response = await api.get(url);
    #     setData(response.data);
    # }
    def download_file(self, url):
        response = self.api.request('GET', url)
        return response.json()

    # export async function deleteFile(user, dataRepoId, fileId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.delete(`${dataRepoId}/file/${fileId}`, {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def delete_file(self, datarepo_id, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/file/{file_id}'
        response = self.api.request('DELETE', url, headers=headers)
        return response.json()

    # export async function addFile(user, dataRepoId, attributes) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.post(`${dataRepoId}/file`,
    #         attributes,
    #         {
    #             headers: requestHeaders
    #         });
    #     return response.data;
    # }
    def add_file(self, datarepo_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/file'
        data = json.dumps(attributes)
        response = self.api.request('POST', url, headers=headers, data=data)
        return response.json()

    # export async function updateFile(user, dataRepoId, fileId, attributes) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.put(`${dataRepoId}/file/${fileId}`,
    #     attributes,
    #     {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def update_file(self, datarepo_id, file_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/file/{file_id}'
        data = json.dumps(attributes)
        response = self.api.request('PUT', url, headers=headers, data=data)
        return response.json()

    # /**
    # * Get file upload url
    # */
    # export async function getFileUploadUrl(user, dataRepoId, file) {
    #     const requestHeaders = createRequestHeaders(user);
    #     console.log(`${dataRepoId}/files/upload/${file.id}`);
    #     const response = await api.get(`${dataRepoId}/files/upload/${file.id}`,
    #         {
    #             headers: requestHeaders
    #         });
    #     console.log(response);
    #     return response.data.url;
    # }
    def get_file_upload_url(self, datarepo_id, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f'{self.base_url}/{datarepo_id}/files/upload/{file_id}'
        response = self.api.request('GET', url, headers=headers)
        return response.json()


