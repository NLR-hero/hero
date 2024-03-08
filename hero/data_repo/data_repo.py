from functools import cache
from pathlib import Path

from .. import auth
from .. import config
from . import data_repo_api


class DataRepo:

    def __init__(self):
        client_id, client_secret = config.get_client_credentials()
        self._client_id = client_id
        self._client_secret = client_secret
        self._scopes = config.get_data_repo_scopes()
        self._access_token = auth.cognito.get_token(
            client_id=self._client_id, client_secret=self._client_secret, scopes=self._scopes
        )
        self._datarepo_id = config.get_data_repo_id()

    @cache
    def get_project(self, project_name):
        """ This will fail with a large number of projects"""
        projects = data_repo_api.read_projects_by_datarepo(self._access_token, self._datarepo_id)
        for project in projects:
            if project['name'] == project_name:
                return project

    @cache
    def get_dataset(self, project_name, dataset_name):
        """ This will fail with a large number of datasets"""
        project = self.get_project(project_name)
        datasets = data_repo_api.read_datasets_by_project(self._access_token, self._datarepo_id, project['id'])
        for dataset in datasets:
            if dataset['name'] == dataset_name:
                return dataset

        data = {
            "name": dataset_name,
            "metadata": {},
            "projectId": project['id'],
        }
        dataset = data_repo_api.create_dataset(self._access_token, self._datarepo_id, data)
        return dataset

    @cache
    def get_file_object(self, project_name, dataset_name, file_name):
        """ This will fail with a large number of files"""
        dataset = self.get_dataset(project_name, dataset_name)
        file_objects = data_repo_api.read_files_by_dataset(self._access_token, self._datarepo_id, dataset['id'])
        for file_object in file_objects:
            if file_object['name'] == file_name:
                return file_object
        data = {
            "name": file_name,
            "metadata": {},
            "datasetId": dataset['id'],
        }
        file_obj = data_repo_api.create_file(self._access_token, self._datarepo_id, data)
        return file_obj
        

    def download_file(self, project_name, dataset_name, file_name, download_path):
        file_object = self.get_file_object(project_name, dataset_name, file_name)
        data_repo_api.download_file(self._access_token, self._datarepo_id, file_object, download_path)

    def upload_file(self, project_name, dataset_name, file_name, upload_path):
        file_object = self.get_file_object(project_name, dataset_name, file_name)
        data_repo_api.upload_file(self._access_token, self._datarepo_id, file_object, upload_path)
