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

    def read_project_by_name(self, name, metatype="Project"):
        """This returns a single project even if there are many with the same name
        and returns an 404 error if there are no projects, nice!
        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project/metatype/{metatype}"
        params = f"name={name}"
        response = self.api.request("GET", url, headers=headers, params=params)
        return response.json()

    def delete_project(self, project_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project/{project_id}"
        response = self.api.request("DELETE", url, headers=headers)
        return response
        # return response.json()

    def read_projects(self):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/projects"
        response = self.api.request("GET", url, headers=headers)
        return response.json()
    
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

    def read_project_datasets(self, project_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project/{project_id}/datasets"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def read_project(self, project_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project/{project_id}"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def read_project_by_name(self, name, metatype='Project'):
        """This returns a single project even if there are many with the same name
        and returns an 404 error if there are no projects, nice!
        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project/metatype/{metatype}"
        params = f"name={name}"
        response = self.api.request("GET", url, headers=headers, params=params)
        return response.json()

    def delete_project(self, project_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project/{project_id}"
        response = self.api.request("DELETE", url, headers=headers)
        return response
        # return response.json()

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

    def update_project(self, project_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project/{project_id}"
        data = json.dumps(attributes)
        response = self.api.request("PUT", url, headers=headers, data=data)
        return response.json()

    def get_datasets(self):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/datasets"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

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

    def get_dataset_files(self, dataset_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/dataset/{dataset_id}/files"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def delete_dataset(self, dataset_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/dataset/{dataset_id}"
        response = self.api.request("DELETE", url, headers=headers)
        return response

    def add_dataset(self, project_id, dataset_name, metatype="Dataset", metadata={}, private=True):
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

    def update_dataset(self, dataset_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/dataset/{dataset_id}"
        data = json.dumps(attributes)
        response = self.api.request("PUT", url, headers=headers, data=data)
        # does not return json.
        return response

    def read_files(self):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/files"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def read_file(self, file_id):
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

    def read_file_download_url(self, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/files/download/{file_id}"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def download_file(self, url):
        response = self.api.request("GET", url)
        return response.json()

    def delete_file(self, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/file/{file_id}"
        response = self.api.request("DELETE", url, headers=headers)
        return response

    def add_file(self, dataset_id, filename, metatype="File", metadata={}, private=True):
        attributes = {
            "name": filename,
            "datasetId": dataset_id,
            "metatype": metatype,
            "metadata": metadata,
            "private": private,
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

    def update_file(self, file_id, attributes):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/file/{file_id}"
        data = json.dumps(attributes)
        response = self.api.request("PUT", url, headers=headers, data=data)
        # does not return json()
        return response

    def read_file_upload_url(self, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/files/upload/{file_id}"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def get_or_create_project(self, project_name, metatype="Project", private=False, metadata={}):
        try:
            project = self.read_project_by_name(project_name, metatype=metatype)
            return project
        except HTTPError as err:
            project = self.add_project(project_name, metatype=metatype, private=private)
            return project

    def get_or_create_dataset(self, project_id, dataset_name, metatype="Dataset", private=True, metadata={}):
        try:
            dataset = self.read_dataset_by_name(dataset_name)
            return dataset
        except HTTPError as err:
            print(f"creating dataset with {private}")
            dataset = self.add_dataset(
                project_id,
                dataset_name,
                private=private,
                metadata=metadata,
                metatype=metatype,
            )
            return dataset

    def get_file_upload_url(self, file_id):
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/files/upload/{file_id}"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def add_file_if_not_exists(
        self, dataset_id, local_filepath, filename=None, private=True
    ):
        assert os.path.exists(local_filepath)
        if filename is None:
            filename = os.path.basename(local_filepath).replace("&", "and")
        try:
            fileobj = self.read_file_by_name(filename)
            return fileobj
        except HTTPError as err:
            fileobj = self.add_file(dataset_id, filename, private=private)
            url = self.get_file_upload_url(fileobj["id"])
            self.upload_file(url["url"], local_filepath)
            # not necessary... but a check.
            fileobj = self.read_file_by_name(filename)
            return fileobj

    def add_or_replace_file(
        self, dataset_id, local_filepath, filename=None, private=True
    ):
        assert os.path.exists(local_filepath)
        if filename is None:
            filename = os.path.basename(local_filepath).replace("&", "and")
        try:
            fileobj = self.read_file_by_name(filename)
        except HTTPError as err:
            fileobj = self.add_file(dataset_id, filename, private=private)
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