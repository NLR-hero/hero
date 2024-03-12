from functools import cache
from pathlib import Path

from .. import auth
from .. import config
from . import data_repo_api

from .errors import retry_method


class DataRepo:

    def __init__(self):
        self._login()

    def _login(self):
        """This method should not have a @retry_method decorator"""
        client_id, client_secret = config.get_client_credentials()
        self._client_id = client_id
        self._client_secret = client_secret
        self._scopes = config.get_data_repo_scopes()
        self._datarepo_id = config.get_data_repo_id()
        self._access_token = auth.cognito.get_token(
            client_id=self._client_id,
            client_secret=self._client_secret,
            scopes=self._scopes,
        )

    @retry_method
    def add_or_get_project(self, project_name):
        projects = data_repo_api.read_projects_by_datarepo(
            self._access_token, self._datarepo_id
        )
        for project in projects:
            if project["name"] == project_name:
                return project

        # else we need to add it
        data = {"name": project_name, "metadata": {}}
        project = data_repo_api.create_project(
            self._access_token, self._datarepo_id, data
        )
        if project is not None:
            return project

    @retry_method
    def add_or_get_dataset(self, project, dataset_name):
        """This will fail with a large number of datasets"""
        datasets = data_repo_api.read_datasets_by_project(
            self._access_token, self._datarepo_id, project.get("id")
        )
        for dataset in datasets:
            if dataset["name"] == dataset_name:
                return dataset

        data = {
            "name": dataset_name,
            "metadata": {},
            "projectId": project["id"],
        }
        dataset = data_repo_api.create_dataset(
            self._access_token, self._datarepo_id, data
        )
        return dataset

    @retry_method
    def add_or_get_file_object(self, dataset, file_name):
        """This will fail with a large number of files"""
        file_objects = data_repo_api.read_files_by_dataset(
            self._access_token, self._datarepo_id, dataset["id"]
        )
        for file_object in file_objects:
            if file_object["name"] == file_name:
                return file_object
        data = {
            "name": file_name,
            "metadata": {},
            "datasetId": dataset["id"],
        }
        file_obj = data_repo_api.create_file(
            self._access_token, self._datarepo_id, data
        )
        return file_obj

    @retry_method
    def upload_file(self, file_object, upload_path):
        data_repo_api.upload_file(
            self._access_token, self._datarepo_id, file_object, upload_path
        )

    @retry_method
    def download_file(self, file_object, download_path):
        data_repo_api.download_file(
            self._access_token, self._datarepo_id, file_object, download_path
        )
