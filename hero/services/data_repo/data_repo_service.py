import json

from ...service import ServiceBase, decorate_all, log_errors
from ...errors import ClientCreateProject, ClientCreateDataset, ClientCreateFileObject
from ...config import get_data_repo_id

from .data_repo_api import DataRepoApi

@decorate_all(log_errors)
class DataRepoService(ServiceBase):
    def _configure(self):
        self.api = DataRepoApi()
        self._datarepo_id = get_data_repo_id()
        self.client.add_scope('data-repo/user')

    def list_projects(self):
        projects = self.api.read_projects_by_datarepo(
            self.client.get_token(),
            self._datarepo_id
        )
        return projects

    def list_datasets(self, project):
        datasets = self.api.read_datasets_by_project(
            self.client.get_token(),
            self._datarepo_id,
            project.get("id")
        )
        return datasets

    def list_file_objects(self, dataset):
        files = self.api.read_files_by_dataset(
            self.client.get_token(),
            self._datarepo_id,
            dataset.get("id")
        )
        return files

    def add_or_get_project(self, project_name):
        projects = self.api.read_projects_by_datarepo(
            self.client.get_token(),
            self._datarepo_id
        )
        for project in projects:
            if project["name"] == project_name:
                return project

        return self.create_project(project_name)

    def get_project(self, project_id):
        projects = self.api.read_project_by_id(
            self.client.get_token(),
            self._datarepo_id,
            project_id
        )

        return projects

    def create_project(self, project_name, metatype="Project", metadata={}):
        data = {"name": project_name, "metatype": metatype, "metadata": metadata}
        project = self.api.create_project(
            self.client.get_token(),
            self._datarepo_id,
            json.dumps(data)
        )
        if project is not None:
            return project
        raise ClientCreateProject

    def add_or_get_dataset(self, project, dataset_name):
        """This will fail with a large number of datasets"""
        datasets = self.api.read_datasets_by_project(
            self.client.get_token(),
            self._datarepo_id,
            project.get("id")
        )
        for dataset in datasets:
            if dataset["name"] == dataset_name:
                return dataset

        return self.create_dataset(project, dataset_name)

    def get_dataset(self, dataset_id):
        """This will fail with a large number of datasets"""
        datasets = self.api.read_dataset_by_id(
            self.client.get_token(),
            self._datarepo_id,
            dataset_id
        )

        return datasets

    def create_dataset(self, project, dataset_name, metatype="Dataset", metadata={}):
        data = {
            "name": dataset_name,
            "metatype": metatype,
            "metadata": metadata,
            "projectId": project["id"],
        }
        dataset = self.api.create_dataset(
            self.client.get_token(),
            self._datarepo_id,
            json.dumps(data)
        )
        if dataset is not None:
            return dataset
        raise ClientCreateProject

    def add_or_get_file_object(self, dataset, file_name, metatype="File", metadata={}):
        """This will fail with a large number of files"""
        file_objects = self.api.read_files_by_dataset(
            self.client.get_token(),
            self._datarepo_id,
            dataset["id"]
        )
        for file_object in file_objects:
            if file_object["name"] == file_name:
                return file_object

        return self.create_file_object(
            dataset,
            file_name,
            metatype=metatype,
            metadata=metadata
        )

    def get_file_object(self, file_id):
        file_object = self.api.read_file_by_id(
            self.client.get_token(),
            self._datarepo_id,
            file_id
        )

        return file_object

    def create_file_object(self, dataset, file_name, metatype="File", metadata={}):
        data = {
            "name": file_name,
            "metatype": metatype,
            "metadata": metadata,
            "datasetId": dataset["id"],
        }
        file_obj = self.api.create_file(
            self.client.get_token(),
            self._datarepo_id,
            json.dumps(data)
        )
        if file_obj is not None:
            return file_obj
        raise ClientCreateFileObject

    def upload_file(self, file_object, upload_path):
        self.api.upload_file(
            self.client.get_token(),
            self._datarepo_id,
            file_object,
            upload_path
        )

    def download_file(self, file_object, download_path):
        self.api.download_file(
            self.client.get_token(),
            self._datarepo_id,
            file_object,
            download_path
        )

    def update_file_object(self, file_object):
        file_object = self.api.update_file_object(
            self.client.get_token(),
            self._datarepo_id,
            file_object["id"],
            json.dumps(file_object)
        )

        return file_object
