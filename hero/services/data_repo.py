import json
import os
from ..url_map import URL_MAP
from ..lib import ServiceBase, decorate_all, log_errors, get_conf_from_collection
from requests.exceptions import HTTPError


# @decorate_all(log_errors)
class DataRepoService(ServiceBase):
    def _configure(self):
        """
        Sets the API, adds data_repo id and required scope
        """
        self.data_repo_id = (
            f"{os.environ.get('HERO_ENV')}-{os.environ.get('HERO_PROJECT')}"
        )
        self.client.add_scope("data-repo/user")
        self.base_url = get_conf_from_collection(URL_MAP, "HERO_DATA_REPO_API_URL")

    def remove_dataset_by_name(self, dataset_name):
        """This method will remove all objects in the dataset from the bottom up
        using the delete methods.
        """
        try:
            dataset = self.read_dataset_by_name(dataset_name)
            files = self.get_dataset_files(dataset["id"])
            for fileobj in files:
                self.delete_file(fileobj["id"])
            self.delete_dataset(dataset["id"])

        except HTTPError as e:
            # if the project doesn't exists return else raise
            if e.response.status_code == 404:
                return []
            raise e

    def remove_project_by_name(self, project_name):
        """This method will remove all objects in the project from the bottom up
        using the delete methods.
        """
        try:
            project = self.read_project_by_name(project_name)
            datasets = self.get_project_datasets(project_id=project["id"])
            for dataset in datasets:
                self.remove_dataset_by_name(dataset["name"])
            self.delete_project(project["id"])

        except HTTPError as e:
            # if the project doesn't exists return else raise
            if e.response.status_code == 404:
                return None
            raise e

        # datasets = data_repo.get_project_datasets(DATA_REPO_ID, project["id"])
        # for dataset in datasets:
        #     files = data_repo.get_dataset_files(DATA_REPO_ID, dataset["id"])
        #     for file in files:
        #         print("deleting file", file["name"])
        #         data_repo.delete_file(DATA_REPO_ID, file["id"])
        #     data_repo.delete_dataset(DATA_REPO_ID, dataset["id"])
        #     print("deleting dataset", dataset["name"])
        # data_repo.delete_project(DATA_REPO_ID, project["id"])
        # print("deleting project", project["name"])

    # export async function getProjects(setData, user, dataRepoId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${dataRepoId}/projects`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    def get_projects(self):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/projects"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    # export async function getProjectDatasets(setData, user, dataRepoId, projectId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${dataRepoId}/project/${projectId}/datasets`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    #
    def get_project_datasets(self, project_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project/{project_id}/datasets"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    # export async function getProject(setData, user, dataRepoId, projectId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${dataRepoId}/project/${projectId}`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    def get_project(self, project_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project/{project_id}"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def read_project_by_name(self, name, metatype="Project"):
        """This returns a single project even if there are many with the same name
        and returns an 404 error if there are no projects, nice!
        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project/metatype/{metatype}"
        params = f"name={name}"
        response = self.api.request("GET", url, headers=headers, params=params)
        return response.json()

    # export async function deleteProject(user, dataRepoId, projectId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.delete(`${dataRepoId}/project/${projectId}`, {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def delete_project(self, project_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project/{project_id}"
        response = self.api.request("DELETE", url, headers=headers)
        return response
        # return response.json()

    # export async function addProject(user, dataRepoId, attributes) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.post(`${dataRepoId}/project`,
    #     attributes,
    #     {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def add_project(self, project_name, metatype="Project", private=False, metadata={}):
        attributes = {
            "name": project_name,
            "metatype": metatype,
            "private": private,
            "metadata": {},
        }

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project"
        data = json.dumps(attributes)
        response = self.api.request("POST", url, headers=headers, data=data)
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
    def update_project(self, project_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project/{project_id}"
        data = json.dumps(attributes)
        response = self.api.request("PUT", url, headers=headers, data=data)
        return response.json()

    # export async function getDatasets(setData, user, dataRepoId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${dataRepoId}/datasets`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    def get_datasets(self):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/datasets"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    # export async function getDataset(setData, user, dataRepoId, datasetId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${dataRepoId}/dataset/${datasetId}`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    def get_dataset(self, dataset_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/dataset/{dataset_id}"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def read_dataset_by_name(self, name, metatype="Dataset"):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/dataset/metatype/{metatype}"
        params = f"name={name}"
        response = self.api.request("GET", url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    # export async function getDatasetFiles(setData, user, dataRepoId, datasetId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${dataRepoId}/dataset/${datasetId}/files`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    def get_dataset_files(self, dataset_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/dataset/{dataset_id}/files"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    # export async function deleteDataset(user, dataRepoId, datasetId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.delete(`${dataRepoId}/dataset/${datasetId}`, {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def delete_dataset(self, dataset_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/dataset/{dataset_id}"
        response = self.api.request("DELETE", url, headers=headers)
        return response

    # export async function addDataset(user, dataRepoId, attributes) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.post(`${dataRepoId}/dataset`,
    #     attributes,
    #     {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def add_dataset(
        self, project_id, dataset_name, metatype="Dataset", metadata={}, private=False
    ):
        attributes = {
            "projectId": project_id,
            "name": dataset_name,
            "metatype": metatype,
            "metadata": metadata,
            "private": private,
        }
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/dataset"
        data = json.dumps(attributes)
        print("add_dataset", attributes)
        response = self.api.request("POST", url, headers=headers, data=data)
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
    def update_dataset(self, dataset_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/dataset/{dataset_id}"
        data = json.dumps(attributes)
        response = self.api.request("PUT", url, headers=headers, data=data)
        # does not return json.
        return response

    # export async function getFiles(setData, user, dataRepoId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${dataRepoId}/files`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    def get_files(self):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/files"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    # export async function getFile(setData, user, dataRepoId, fileId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.get(`${dataRepoId}/file/${fileId}`, {
    #         headers: requestHeaders
    #     });
    #     setData(response.data);
    # }
    def get_file(self, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/file/{file_id}"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def read_file_by_name(self, name, metatype="File"):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/file/metatype/{metatype}"
        params = f"name={name}"
        response = self.api.request("GET", url, headers=headers, params=params)
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
    def get_file_download_url(self, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/files/download/{file_id}"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    # /**
    # * Download file
    # */
    # export async function downloadFile(setData, url) {
    #     const response = await api.get(url);
    #     setData(response.data);
    # }
    def download_file(self, url):
        response = self.api.request("GET", url)
        return response.json()

    # export async function deleteFile(user, dataRepoId, fileId) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.delete(`${dataRepoId}/file/${fileId}`, {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def delete_file(self, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/file/{file_id}"
        response = self.api.request("DELETE", url, headers=headers)
        return response

    # export async function addFile(user, dataRepoId, attributes) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.post(`${dataRepoId}/file`,
    #         attributes,
    #         {
    #             headers: requestHeaders
    #         });
    #     return response.data;
    # }
    def add_file(self, dataset_id, filename, metatype="File", metadata={}):
        attributes = {
            "name": filename,
            "datasetId": dataset_id,
            "metatype": metatype,
            "metadata": metadata,
        }
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/file"
        data = json.dumps(attributes)
        response = self.api.request("POST", url, headers=headers, data=data)
        return response.json()

    def upload_file(self, signed_url, file_path):

        # Read the file data
        with open(file_path, "rb") as file:
            file_data = file.read()

        # Make a PUT request to the signed URL
        response = self.api.put(signed_url, data=file_data)
        return response

    # export async function updateFile(user, dataRepoId, fileId, attributes) {
    #     const requestHeaders = createRequestHeaders(user);
    #     const response = await api.put(`${dataRepoId}/file/${fileId}`,
    #     attributes,
    #     {
    #         headers: requestHeaders
    #     });
    #     return response.data;
    # }
    def update_file(self, file_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/file/{file_id}"
        data = json.dumps(attributes)
        response = self.api.request("PUT", url, headers=headers, data=data)
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
    def get_file_upload_url(self, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/files/upload/{file_id}"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    # what do you think about these files?
    # ====================================
    def get_or_create_project(
        self, project_name, metatype="Project", private=False, metadata={}
    ):
        try:
            project = self.read_project_by_name(project_name, metatype=metatype)
            return project
        except HTTPError as err:
            project = self.add_project(project_name, metatype=metatype, private=False)
            return project

    # dataset_name, metatype="Dataset", metadata={}, private=False
    def get_or_create_dataset(
        self, project_id, dataset_name, metatype="Dataset", private=False, metadata={}
    ):
        try:
            dataset = self.read_dataset_by_name(dataset_name)
            return dataset
        except HTTPError as err:
            dataset = self.add_dataset(
                project_id,
                dataset_name,
                private=private,
                metadata=metadata,
                metatype=metatype,
            )
            return dataset

    def add_file_if_not_exists(self, dataset_id, local_filepath, filename=None):
        assert os.path.exists(local_filepath)
        if filename is None:
            filename = os.path.basename(local_filepath).replace("&", "and")
        try:
            fileobj = self.read_file_by_name(filename)
            return fileobj
        except HTTPError as err:
            fileobj = self.add_file(dataset_id, filename)
            url = self.get_file_upload_url(fileobj["id"])
            self.upload_file(url["url"], local_filepath)
            # not necessary... but a check.
            fileobj = self.read_file_by_name(filename)
            return fileobj

    def add_or_replace_file(self, dataset_id, local_filepath, filename=None):
        assert os.path.exists(local_filepath)
        if filename is None:
            filename = os.path.basename(local_filepath).replace("&", "and")
        try:
            fileobj = self.read_file_by_name(filename)
        except HTTPError as err:
            fileobj = self.add_file(dataset_id, filename)
        finally:
            url = self.get_file_upload_url(fileobj["id"])
            self.upload_file(url["url"], local_filepath)
            fileobj = self.read_file_by_name(filename)
            return fileobj

    def download_file_by_filename(self, filename, local_filepath):
        fileobj = self.read_file_by_name(filename)
        self.download_file_by_file_id(fileobj["id"], local_filepath)

    def download_file_by_file_id(self, file_id, local_filepath):
        url = self.get_file_download_url(file_id)

        with self.api.get(url["url"], stream=True) as r:
            r.raise_for_status()
            try:
                with open(local_filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            except Exception as e:
                print(f"File write to disk failed with error: {str(e)}")
