import json
import logging

from ...config import get_data_repo_api
from ...api import ApiBase
log = logging.getLogger("hero:auth:cognito")


class DataRepoApi(ApiBase):
    def __init__(self, resilient_session=False):
        super().__init__(resilient_session)
        self.base_url = get_data_repo_api()

    def create_project(self, token, datahubId, project):
        url = f"{self.base_url}/{datahubId}/project"
        payload = json.dumps(project)
        response = self.session.request("POST", url, headers=self.getHeaders(token), data=payload)
        response.raise_for_status()
        return response.json()


    def create_dataset(self, token, datahubId, data):
        url = f"{self.base_url}/{datahubId}/dataset"
        payload = json.dumps(data)
        response = self.session.request("POST", url, headers=self.getHeaders(token), data=payload)
        response.raise_for_status()
        return response.json()


    def create_file(self, token, datahubId, fileData):
        url = f"{self.base_url}/{datahubId}/file"
        payload = json.dumps(fileData)
        response = self.session.request("POST", url, headers=self.getHeaders(token), data=payload)
        response.raise_for_status()
        return response.json()


    def get_or_create_file(self, token, datahubId, fileData):
        # if filename exists, return it
        try:
            filename = self.read_file_by_name(token, datahubId, "File", fileData["name"])
            return filename

        except Exception as e:
            # create file
            filename = self.create_file(token, datahubId, fileData)
            return filename


    def upload_file(self, token, datahubId, fileItem, file_path):
        url = f'{self.base_url}/{datahubId}/files/upload/{fileItem["id"]}'
        response = self.session.request("GET", url, headers=self.getHeaders(token))
        signed_url = response.json()["url"]

        # file_path = f'./tmp/{fileItem["name"]}'  # The local file you want to upload

        # Read the file data
        with open(file_path, "rb") as file:
            file_data = file.read()

        # Make a PUT request to the signed URL
        response = self.session.put(signed_url, data=file_data)

        # Check if the upload was successful (HTTP status code 200)
        if response.status_code == 200:
            print("File upload successful!")
        else:
            print(
                f"File upload failed with status code {response.status_code}: {response.text}"
            )


    def download_file(self, token, datahubId, fileItem, file_path):
        url = f'{self.base_url}/{datahubId}/files/download/{fileItem["id"]}'
        response = self.session.request("GET", url, headers=self.getHeaders(token))
        signed_url = response.json()["url"]

        with self.session.get(signed_url, stream=True) as r:
            r.raise_for_status()
            try:
                with open(f"{file_path}", "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            except Exception as e:
                print(f"File write to disk failed with error: {str(e)}")

        if response.status_code == 200:
            print("File download successful!")
        else:
            print(
                f"File download failed with status code {response.status_code}: {response.text}"
            )


    def read_project_by_name(self, token, datahubId, metatype, name):
        url = (
            f"{self.base_url}/{datahubId}/project/metatype/{metatype}?name={name}"
        )
        print(url)
        response = self.session.request("GET", url, headers=self.getHeaders(token))

        response.raise_for_status()
        return response.json()


    def read_dataset_by_name(self, token, datahubId, metatype, name):
        url = (
            f"{self.base_url}/{datahubId}/dataset/metatype/{metatype}?name={name}"
        )
        response = self.session.request("GET", url, headers=self.getHeaders(token))

        response.raise_for_status()
        return response.json()


    def read_file_by_name(self, token, datahubId, metatype, name):
        url = f"{self.base_url}/{datahubId}/file/metatype/{metatype}?name={name}"
        response = self.session.request("GET", url, headers=self.getHeaders(token))
        response.raise_for_status()
        return response.json()


    def read_projects_by_datarepo(self, token, datahubId):
        print("calling...")
        url = f"{self.base_url}/{datahubId}/projects"
        response = self.session.request("GET", url, headers=self.getHeaders(token))
        response.raise_for_status()
        return response.json()


    def read_datasets_by_project(self, token, datahubId, project_id):
        url = f"{self.base_url}/{datahubId}/project/{project_id}/datasets"
        response = self.session.request("GET", url, headers=self.getHeaders(token))
        response.raise_for_status()
        return response.json()


    def read_files_by_dataset(self, token, datahubId, dataset_id):
        url = f"{self.base_url}/{datahubId}/dataset/{dataset_id}/files"
        response = self.session.request("GET", url, headers=self.getHeaders(token))
        response.raise_for_status()
        return response.json()


    def read_project_by_id(self, token, datahubId, project_id):
        url = f"{self.base_url}/{datahubId}/project/{project_id}"
        response = self.session.request("GET", url, headers=self.getHeaders(token))
        response.raise_for_status()
        return response.json()


    def read_dataset_by_id(self, token, datahubId, dataset_id):
        url = f"{self.base_url}/{datahubId}/dataset/{dataset_id}"
        response = self.session.request("GET", url, headers=self.getHeaders(token))
        response.raise_for_status()
        return response.json()


    def read_file_by_id(self, token, datahubId, file_id):
        url = f"{self.base_url}/{datahubId}/file/{file_id}"
        response = self.session.request("GET", url, headers=self.getHeaders(token))
        response.raise_for_status()
        return response.json()


    def update_file_object(self, token, datahubId, file_id, data):
        url = f"{self.base_url}/{datahubId}/file/{file_id}"
        payload = json.dumps(data)
        response = self.session.request("PUT", url, headers=self.getHeaders(token), data=payload)
        response.raise_for_status()
        return response.json()
