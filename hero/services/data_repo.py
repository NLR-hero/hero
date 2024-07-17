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
        self.client.add_scope("data-repo/user")
        self.base_url = get_conf_from_collection(URL_MAP, "HERO_DATA_REPO_API_URL")

    def read_projects(self, datarepo_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/projects"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def read_project_datasets(self, datarepo_id, project_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/project/{project_id}/datasets"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def read_project(self, datarepo_id, project_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/project/{project_id}"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def read_project_by_name(self, datarepo_id, name, metatype='Project'):
        """This returns a single project even if there are many with the same name
        and returns an 404 error if there are no projects, nice!
        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/project/metatype/{metatype}"
        params = f"name={name}"
        response = self.api.request("GET", url, headers=headers, params=params)
        return response.json()

    def delete_project(self, datarepo_id, project_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/project/{project_id}"
        response = self.api.request("DELETE", url, headers=headers)
        return response
        # return response.json()

    def add_project(self, datarepo_id, project_name, metadata={}, metatype="Project"):
        attributes = {
            "datarepoId": datarepo_id,
            "name": project_name,
            "metatype": metatype,
            "metadata": metadata,
        }
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/project"
        data = json.dumps(attributes)
        response = self.api.request("POST", url, headers=headers, data=data)
        return response.json()

    def update_project(self, datarepo_id, project_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/project/{project_id}"
        data = json.dumps(attributes)
        response = self.api.request("PUT", url, headers=headers, data=data)
        return response.json()

    def read_datasets(self, datarepo_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/datasets"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def read_dataset(self, datarepo_id, dataset_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/dataset/{dataset_id}"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def read_dataset_by_name(self, datarepo_id, name, metatype="Dataset"):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/dataset/metatype/{metatype}"
        params = f"name={name}"
        response = self.api.request("GET", url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def read_dataset_files(self, datarepo_id, dataset_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/dataset/{dataset_id}/files"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def delete_dataset(self, datarepo_id, dataset_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/dataset/{dataset_id}"
        response = self.api.request("DELETE", url, headers=headers)
        return response

    def add_dataset(self, datarepo_id, project_id, dataset_name, metatype="Dataset", metadata={}):
        attributes = {
            "projectId": project_id,
            "name": dataset_name,
            "metatype": metatype,
            "metadata": metadata,
        }
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/dataset"
        data = json.dumps(attributes)
        response = self.api.request("POST", url, headers=headers, data=data)
        return response.json()

    def update_dataset(self, datarepo_id, dataset_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/dataset/{dataset_id}"
        data = json.dumps(attributes)
        response = self.api.request("PUT", url, headers=headers, data=data)
        return response.json()

    def read_files(self, datarepo_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/files"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def read_file(self, datarepo_id, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/file/{file_id}"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def read_file_by_name(self, datarepo_id, name, metatype="File"):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/file/metatype/{metatype}"
        params = f"name={name}"
        response = self.api.request("GET", url, headers=headers, params=params)
        return response.json()
    def read_file_download_url(self, datarepo_id, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/files/download/{file_id}"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def download_file(self, url):
        response = self.api.request("GET", url)
        return response.json()

    def delete_file(self, datarepo_id, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/file/{file_id}"
        response = self.api.request("DELETE", url, headers=headers)
        return response

    def add_file(self, datarepo_id, dataset_id, filename, metatype="File", metadata={}):
        attributes = {
            "name": filename,
            "datasetId": dataset_id,
            "metatype": metatype,
            "metadata": metadata,
        }
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/file"
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

    def update_file(self, datarepo_id, file_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/file/{file_id}"
        data = json.dumps(attributes)
        response = self.api.request("PUT", url, headers=headers, data=data)
        return response.json()

    def read_file_upload_url(self, datarepo_id, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{datarepo_id}/files/upload/{file_id}"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def get_or_create_project(self, DATA_REPO_ID, project_name):
        try:
            project = self.read_project_by_name(DATA_REPO_ID, project_name)
            return project
        except HTTPError as err:
            project = self.add_project(DATA_REPO_ID, project_name)
            return project

    def get_or_create_dataset(self, DATA_REPO_ID, project_id, dataset_name):
        try:
            dataset = self.read_dataset_by_name(DATA_REPO_ID, dataset_name)
            return dataset
        except HTTPError as err:
            dataset = self.add_dataset(DATA_REPO_ID, project_id, dataset_name)
            return dataset

    def add_file_if_not_exists(
        self, DATA_REPO_ID, dataset_id, local_filepath, filename=None
    ):
        assert os.path.exists(local_filepath)
        if filename is None:
            filename = os.path.basename(local_filepath).replace("&", "and")
        try:
            fileobj = self.read_file_by_name(DATA_REPO_ID, filename)
            return fileobj
        except HTTPError as err:
            fileobj = self.add_file(DATA_REPO_ID, dataset_id, filename)
            url = self.get_file_upload_url(DATA_REPO_ID, fileobj["id"])
            self.upload_file(url["url"], local_filepath)
            # not necessary... but a check.
            fileobj = self.read_file_by_name(DATA_REPO_ID, filename)
            return fileobj

    def add_or_replace_file(
        self, DATA_REPO_ID, dataset_id, local_filepath, filename=None
    ):
        assert os.path.exists(local_filepath)
        if filename is None:
            filename = os.path.basename(local_filepath).replace("&", "and")
        try:
            fileobj = self.read_file_by_name(DATA_REPO_ID, filename)
        except HTTPError as err:
            fileobj = self.add_file(DATA_REPO_ID, dataset_id, filename)
        finally:
            url = self.get_file_upload_url(DATA_REPO_ID, fileobj["id"])
            self.upload_file(url["url"], local_filepath)
            fileobj = self.read_file_by_name(DATA_REPO_ID, filename)
            return fileobj

    def download_file_by_filename(self, DATA_REPO_ID, filename, local_filepath):
        fileobj = self.read_file_by_name(DATA_REPO_ID, filename)
        self.download_file_by_file_id(DATA_REPO_ID, fileobj["id"], local_filepath)

    def download_file_by_file_id(self, DATA_REPO_ID, file_id, local_filepath):
        url = self.get_file_download_url(DATA_REPO_ID, file_id)

        with self.api.get(url["url"], stream=True) as r:
            r.raise_for_status()
            try:
                with open(local_filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            except Exception as e:
                print(f"File write to disk failed with error: {str(e)}")
