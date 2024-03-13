from functools import cache
from pathlib import Path

from .. import auth
from .. import config
from . import data_repo_api

from .. import errors
from .errors import retry_method


def track_calls(func):
    def wrapper(self, *args, **kwargs):
        self._calls += 1
        return func(self, *args, **kwargs)

    return wrapper


class DataRepo:

    def __init__(self):
        self._calls = 0
        self._login()

    @track_calls
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

    @track_calls
    @retry_method
    def list_projects(self):
        projects = data_repo_api.read_projects_by_datarepo(
            self._access_token, self._datarepo_id
        )
        return projects

    @track_calls
    @retry_method
    def list_datasets(self, project):
        datasets = data_repo_api.read_datasets_by_project(
            self._access_token, self._datarepo_id, project.get("id")
        )
        return datasets

    @track_calls
    @retry_method
    def list_file_objects(self, dataset):
        files = data_repo_api.read_files_by_dataset(
            self._access_token, self._datarepo_id, dataset.get("id")
        )
        return files

    @track_calls
    @retry_method
    def add_or_get_project(self, project_name):
        projects = data_repo_api.read_projects_by_datarepo(
            self._access_token, self._datarepo_id
        )
        for project in projects:
            if project["name"] == project_name:
                return project

        return self.create_project(project_name)
    
    @track_calls
    @retry_method
    def get_project(self, project_id):
        projects = data_repo_api.read_projects_by_id(
            self._access_token, self._datarepo_id, project_id
        )
        
        return projects

    @track_calls
    @retry_method
    def create_project(self, project_name, metatype='Project', metadata={}):
        data = {
            "name": project_name, 
            "metatype": metatype,
            "metadata": metadata
        }
        project = data_repo_api.create_project(
            self._access_token, self._datarepo_id, data
        )
        if project is not None:
            return project
        raise errors.ClientCreateProject

    @track_calls
    @retry_method
    def add_or_get_dataset(self, project, dataset_name):
        """This will fail with a large number of datasets"""
        datasets = data_repo_api.read_datasets_by_project(
            self._access_token, self._datarepo_id, project.get("id")
        )
        for dataset in datasets:
            if dataset["name"] == dataset_name:
                return dataset

        return self.create_dataset(project, dataset_name)
    
    @track_calls
    @retry_method
    def get_dataset(self, dataset_id):
        """This will fail with a large number of datasets"""
        datasets = data_repo_api.read_datasets_by_id(
            self._access_token, self._datarepo_id, dataset_id
        )

        return datasets

    @track_calls
    @retry_method
    def create_dataset(self, project, dataset_name, metatype='Dataset', metadata={}):
        data = {
            "name": dataset_name,
            "metatype": metatype,
            "metadata": metadata,
            "projectId": project["id"],
        }
        dataset = data_repo_api.create_dataset(
            self._access_token, self._datarepo_id, data
        )
        if dataset is not None:
            return dataset
        raise errors.ClientCreateDataset

    @track_calls
    @retry_method
    def add_or_get_file_object(self, dataset, file_name):
        """This will fail with a large number of files"""
        file_objects = data_repo_api.read_files_by_dataset(
            self._access_token, self._datarepo_id, dataset["id"]
        )
        for file_object in file_objects:
            if file_object["name"] == file_name:
                return file_object

        return self.create_file_object(dataset, file_name)
    
    @track_calls
    @retry_method
    def get_file_object(self, file_id):
        file_object = data_repo_api.read_file_by_id(
            self._access_token, self._datarepo_id, file_id
        )
        
        return file_object

    @track_calls
    @retry_method
    def create_file_object(self, dataset, file_name, metatype='File', metadata={}):
        data = {
            "name": file_name,
            "metatype": metatype,
            "metadata": metadata,
            "datasetId": dataset["id"],
        }
        file_obj = data_repo_api.create_file(
            self._access_token, self._datarepo_id, data
        )
        if file_obj is not None:
            return file_obj
        raise errors.ClientCreateFileObject

    @track_calls
    @retry_method
    def upload_file(self, file_object, upload_path):
        data_repo_api.upload_file(
            self._access_token, self._datarepo_id, file_object, upload_path
        )

    @track_calls
    @retry_method
    def download_file(self, file_object, download_path):
        data_repo_api.download_file(
            self._access_token, self._datarepo_id, file_object, download_path
        )
