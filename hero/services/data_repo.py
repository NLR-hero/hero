import json
import os
from ..url_map import URL_MAP
from ..lib import ServiceBase, decorate_all, log_errors, get_conf_from_collection
from requests.exceptions import HTTPError, JSONDecodeError
from ..lib.errors import (
    MissingRequiredAttribute,
    HEROAPIResponseException,
    HERODataRepoProjectNotFound,
    HERODataRepoDatasetNotFound,
    HERODataRepoFileNotFound,
    HERODataRepoFileAlreadyExists,
    HERODataRepoDatasetAlreadyExists,
    HERODataRepoProjectAlreadyExists,
)
from ..lib.helpers import kwargs_to_json_for_request


@decorate_all(log_errors)
class DataRepoService(ServiceBase):
    def _configure(self):
        """
        Sets the API, adds data_repo id and required scope
        """
        self.data_repo_id = self.application_id
        self.client.add_scope("data-repo/user")
        self.base_url = get_conf_from_collection(URL_MAP, "HERO_DATA_REPO_API_URL")
        self.data_repo_url = f"{self.base_url}/{self.application_id}"

    def read_projects(self):
        """
        List projects.

        Returns
        -------
        projects : list of dict
            A list of projects where each dict is project attributes.

        Notes
        -----
        New in version 0.2.0.
        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/projects"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def read_project(self, id: str) -> dict:
        """
        Read a project by id.

        Parameters
        ----------
        id : str, required
            The project UUID

        Returns
        -------
        project : dict
            The project attributes.

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HERODataRepoProjectNotFound
            If the project does not exists

        Notes
        -----
        New in version 0.2.0.
        """
        if id is None:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project/{id}"
        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 404:
                raise HERODataRepoProjectNotFound()
            raise e

    def read_project_by_name(self, name=None, data_repo_id=None, metatype="Project"):
        """
        Read a project by name.

        This returns a single project even if there are many with the same name and returns an 404 error if there are no projects, nice!

        Parameters
        -----------
        data_repo_id : str, optional
            The Data Repo UUID.

        name : str, required
            The project name

        metadata : dict, required
            Project metadata

        Returns
        --------
        project : dict
            The project attributes.

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        HERODataRepoProjectNotFound
            If the project does not exist

        Notes
        -----
        Changed in version 0.3.0:

        - Added support to uniquely qualify this resource in the data repo hierarchy by providing the parent resource id.
        - Improved building the set API params.

        New in version 0.2.0.
        """
        # TODO: eventually this will be required.
        if data_repo_id is None:
            data_repo_id = self.data_repo_id

        if name is None:
            raise MissingRequiredAttribute('Missing required attribute: "name"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project/metatype/{metatype}"

        params = kwargs_to_json_for_request(name=name, dataRepoId=data_repo_id)

        try:
            response = self.api.request("GET", url, headers=headers, params=params)
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 404:
                raise HERODataRepoProjectNotFound()
            raise e

    def read_project_datasets(self, project_id=None):
        """
        List datasets in a project.

        Parameters
        -----------
        project_id : str, required
            The project UUID

        Returns
        --------
        datasets : list of dict
            A list of datasets where each dict is dataset attributes.

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        Notes
        -----
        New in version 0.2.0.
        """
        if project_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "project_id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project/{project_id}/datasets"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def delete_project(self, id=None, cascade=False):
        """
        Delete a project.

        This method only deletes a project. It does not remove any related resources and may result in orphaned resources. See the remove methods if you want to delete this an all related content.

        Parameters
        -----------
        id : str, required
            The project UUID to delete.

        cascade : bool, optional
            A flag to delete all realted resources of the project.

        Returns
        --------
        None

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        Notes
        -----
        New in version 0.2.0.
        """

        if cascade:
            return self._delete_project_with_cascade(id, cascade)

        if id is None:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project/{id}"
        response = self.api.request("DELETE", url, headers=headers)
        return None

    def _delete_project_with_cascade(self, id, cascade):
        """
        Remove a project and all of its related resources.

        This method will remove all objects in the project from the bottom up using the delete methods.

        Parameters
        -----------
        id : str, required
            The UUID of the project to remove.

        metatype : str, required
            The project's metatype.

        cascase : bool, required
            A flag to delete all realted resources of the project.

        Returns
        --------
        None

        Notes
        -----
        Changed in version 0.3.0: Forward arguments to subsequent methods that need them.

        New in version 0.2.0.
        """
        try:
            datasets = self.read_project_datasets(project_id=id)
            for dataset in datasets:
                self.delete_dataset(id=dataset["id"], cascade=cascade)
            self.delete_project(id)

        except HTTPError as e:
            # TODO: Is this what we want to do here? Too tired to think about it now
            # if the project doesn't exists return else raise
            if e.response.status_code == 404:
                return None
            raise e

    def remove_project_by_name(self, data_repo_id=None, name=None, metatype="Project"):
        """
        Remove a project and all of its related resources.

        This method will remove all objects in the project from the bottom up using the delete methods.

        Parameters
        -----------
        data_repo_id : str, optional
            The Data Repo UUID.

        name : str, required
            The name of the project to remove.

        metatype : str, required
            The project's metatype.

        Returns
        --------
        None

        Notes
        -----
        Changed in version 0.3.0: Added support to uniquely qualify this resource in the data repo hierarchy by providing the parent resource id.

        New in version 0.2.0.
        """
        project = self.read_project_by_name(
            data_repo_id=data_repo_id, name=name, metatype=metatype
        )
        self.delete_project(id=project["id"])
        return

    def add_project(
        self,
        name=None,
        data_repo_id=None,
        metatype="Project",
        metadata={},
        private=False,
        id=None,
    ):
        """
        Create a new project.

        Parameters
        -----------
        data_repo_id : str, optional
            The Data Repo name. In the future this will be the UUID of a Data Repo domain object in the Data Repo service. Defaults to self.data_repo_id.
            This is here to cover off expected updates to the Data Repo.

        name : str, required
            The name of the project.

        metatype : str, optional
            The project metatype. Defaults to "Project".

        metadata : dict, optional
            The project metadata. Defaults to an empty dictionary.

        private : bool, optional
            The visibility of the project. Defaults to False.

        id: str, optional
            User assigned Id of the project, require admin role

        Returns
        --------
        project : dict
            The project attributes

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        HERODataRepoProjectAlreadyExists
            If the resource already exists

        Notes
        -----
        Changed in version 0.3.0:

        - Added support to uniquely qualify this resource in the data repo hierarchy by providing the parent resource id.
        - Added new exception when trying to add a resource that already exists.

        New in version 0.2.0.
        """
        # TODO: name, and data_repo_id are out of order to support older code that uses positional arguments, eventually this will be deprecated and the order restored to project, name and both argument should be named
        if data_repo_id is None:
            data_repo_id = self.data_repo_id

        attributes = {
            "name": name,
            "metatype": metatype,
            "private": private,
            "metadata": metadata,
        }

        # add user assigned id if provided
        if id:
            attributes["id"] = id

        if "name" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "name"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/project"
        data = json.dumps(attributes)
        try:
            # test if the project already exists
            if id:
                # Try to see if the project exists by id
                # Catch error of project not found and continue
                try:
                    self.read_project(id=id)
                    raise HERODataRepoProjectAlreadyExists(
                        f"Project with id {id} already exists"
                    )
                except HERODataRepoProjectNotFound:
                    pass

            response = self.api.request("POST", url, headers=headers, data=data)
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 400:
                response_error = e.response.json()
                raise HERODataRepoProjectAlreadyExists(
                    response_error["error"]["message"]
                )
            raise e

    def update_project(self, id=None, name=None, metadata=None, private=None):
        """
        Update the attributes of a project.

        Parameters
        -----------
        id : str, required
            The UUID of a project

        name : str, required
            The project name

        metadata : dict, required
            Project metadata

        private : bool, optional
            A flag to set project visiblity to private (True) or public (False)

        Returns
        --------
        project : dict
            The project attributes

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            When there is a problem trying to parse the response as json

        HERODataRepoProjectAlreadyExists
            If an update is made and the name matches an existing resource

        Notes
        -----
        New in version 0.2.0.
        """

        # TODO: Problems with update_project:
        # * [API] doesn't update the name in the GSI
        # * [API] requires both name and metadata to be defined no matter what you want to update and the API doesn't throw an error but returns a 200 with an empty body if you one of name or metadata. it only works when you include both

        if id is None:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        attributes = {"name": name, "metadata": metadata, "private": private}

        # drop attributes that are None
        attributes = {k: v for k, v in attributes.items() if v is not None}

        # required attributes
        if "name" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "name"')
        if "metadata" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "metadata"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.data_repo_url}/project/{id}"
        data = json.dumps(attributes)
        try:
            response = self.api.request("PUT", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            if e.response.status_code == 400:
                response_error = e.response.json()
                raise HERODataRepoProjectAlreadyExists(
                    response_error["error"]["message"]
                )
            raise e

    def get_or_create_project(
        self,
        name=None,
        data_repo_id=None,
        metatype="Project",
        metadata={},
        private=False,
    ):
        """
        Attempt to read a project or create it if it does not exist.

        Parameters
        -----------
        data_repo_id : str, optional
            The Data Repo UUID.

        name : str, required
            The project name

        metatype : str, optional
            The project metatype. Defaults to "Project".

        metadata : dict, required
            Project metadata

        private : bool, optional
            A flag to set project visiblity to private (True) or public (False)

        Returns
        --------
        project : dict
            The project attributes

        Notes
        -----
        Changed in version 0.3.0: Added support to uniquely qualify this resource in the data repo hierarchy by providing the parent resource id.

        New in version 0.2.0.
        """
        try:
            project = self.read_project_by_name(
                data_repo_id=data_repo_id, name=name, metatype=metatype
            )
            return project
        except HERODataRepoProjectNotFound as e:
            project = self.add_project(
                name=name, metatype=metatype, metadata=metadata, private=private
            )
            return project

    def read_datasets(self):
        """
        List datasets.

        Returns
        --------
        datasets : list of dict
            A list of datasets where each dict is project attributes.

        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/datasets"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def read_dataset(self, id=None):
        """
        Read a dataset by id.

        Parameters
        -----------

        id : str, required
            The dataset UUID

        Returns
        --------
        dataset : dict
            The dataset attributes.

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        HERODataRepoDatasetNotFound
            If the dataset does not exists

        Notes
        -----
        New in version 0.2.0.
        """
        if id is None:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/dataset/{id}"
        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 404:
                raise HERODataRepoDatasetNotFound()
            raise e

    def read_dataset_by_name(self, name=None, project_id=None, metatype="Dataset"):
        """
        Read a dataset by name.

        Parameters
        -----------
        project_id : str, optional
            The parent project UUID

        name : str, required
            The dataset name

        metadata : dict, required
            Dataset metadata

        Returns
        --------
        dataset : dict

            The dataset attributes.

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        HERODataRepoDatasetNotFound
            If the dataset does not exist

        Notes
        -----
        Changed in version 0.3.0:

        - Added support to uniquely qualify this resource in the data repo hierarchy by providing the parent resource id.
        - Improved building the set API params.

        New in version 0.2.0.
        """
        # TODO: (name, project_id) need to be switched (there are several of these) it is this way to to not break existing code that uses postiional arguments.
        if name is None:
            raise MissingRequiredAttribute('Missing required attribute: "name"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.data_repo_url}/dataset/metatype/{metatype}"

        params = kwargs_to_json_for_request(name=name, projectId=project_id)

        try:
            response = self.api.request("GET", url, headers=headers, params=params)
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 404:
                raise HERODataRepoDatasetNotFound()
            raise e

    def read_dataset_files(self, dataset_id=None):
        """
        List files in a dataset.

        Parameters
        -----------

        dataset_id : str, required
            The dataset UUID

        Returns
        --------
        files : list of dict
            A list of files where each dict is file attributes.

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        Notes
        -----
        New in version 0.2.0.
        """
        if dataset_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "dataset_id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.data_repo_url}/dataset/{dataset_id}/files"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def delete_dataset(self, id: str = None, cascade: bool = False):
        """
        Delete a dataset.

        This method only deletes a dataset. It does not remove any related resources and may result in orphaned resources. See the remove methods if you want to delete this an all related content.

        Parameters
        ----------
        id : str, required
            The dataset UUID to delete.

        cascade : bool, optional
            A flag to delete all related resources of the dataset.

        Returns
        -------
        None

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        Notes
        -----
        New in version 0.2.0.
        """
        if cascade:
            return self._delete_dataset_with_cascade(id, cascade)

        if id is None:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.data_repo_url}/dataset/{id}"
        response = self.api.request("DELETE", url, headers=headers)
        return response

    def _delete_dataset_with_cascade(self, id=None, cascade=False):
        """
        Remove a dataset and all of its related resources.

        This method will remove all objects in the dataset from the bottom up using the delete methods.

        Parameters
        -----------
        id : str, required
            The UUID of the dataset to remove.

        cascade : bool, optional
            A flag to delete all realted resources of the dataset.

        Returns
        --------
        None

        Notes
        -----
        New in version 0.2.0.
        """
        try:
            files = self.read_dataset_files(id)
            for fileobj in files:
                self.delete_file(fileobj["id"])
            self.delete_dataset(id)

        except HTTPError as e:
            # if the project doesn't exists return else raise
            if e.response.status_code == 404:
                return []
            raise e

    def remove_dataset_by_name(
        self, project_id=None, name=None, metatype="Dataset", cascade=False
    ):
        """
        Remove a dataset and all of its related resources.

        This method will remove all objects in the dataset from the bottom up using the delete methods.

        Parameters
        -----------
        project_id : str, optional
            The parent project UUID

        name : str, required
            The name of the dataset to remove.

        metatype : str, optional
            The dataset metatype. Defaults to "Dataset".

        cascade : bool, optional
            A flag to delete all realted resources of the dataset.

        Returns
        --------
        None

        Notes
        -----
        Changed in version 0.3.0:

        - Added support to uniquely qualify this resource in the data repo hierarchy by providing the parent resource id.
        - Forward arguments to subsequent methods that need them

        New in version 0.2.0.
        """
        dataset = self.read_dataset_by_name(
            project_id=project_id, name=name, metatype=metatype
        )
        self.delete_dataset(id=dataset["id"], cascade=cascade)

    def add_dataset(
        self,
        project_id=None,
        name=None,
        metatype="Dataset",
        metadata={},
        private=True,
        id=None,
    ):
        """
        Create a new dataset.

        Parameters
        -----------
        project_id : str, required
            The project id.

        name : str, required
            The name of the dataset.

        metatype : str, optional
            The dataset metatype. Defaults to "Dataset".

        metadata : dict, optional
            The dataset metadata. Defaults to an empty dictionary.

        private : bool, optional
            The visibility of the dataset. Defaults to True.

        id: str, optional
            User assigned Id of the dataset, require admin role

        Returns
        --------
        dataset : dict
            The dataset attributes

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        HERODataRepoDatasetAlreadyExists
            If the resource already exists

        Notes
        -----
        Changed in version 0.3.0:

        - Added support to uniquely qualify this resource in the data repo hierarchy by providing the parent resource id.
        - Added new exception when trying to add a resource that already exists.

        New in version 0.2.0.
        """
        attributes = {
            "projectId": project_id,
            "name": name,
            "metatype": metatype,
            "metadata": metadata,
            "private": private,
        }
        if id:
            attributes["id"] = id

        if "projectId" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "project_id"')
        if "name" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "name"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.data_repo_url}/dataset"
        data = json.dumps(attributes)
        try:
            if id:
                try:
                    self.read_project(id=id)
                    raise HERODataRepoProjectAlreadyExists(
                        f"Project with id {id} already exists"
                    )
                except HERODataRepoProjectNotFound:
                    pass
            response = self.api.request("POST", url, headers=headers, data=data)
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 400:
                response_error = e.response.json()
                raise HERODataRepoDatasetAlreadyExists(
                    response_error["error"]["message"]
                )
            raise e

    def update_dataset(self, dataset_id=None, name=None, metadata=None, private=True):
        """
        Update the attributes of a dataset.

        Parameters
        -----------
        dataset_id : str, required
            The UUID of a dataset

        name : str, required
            The dataset name

        metadata : dict, required
            Dataset metadata

        private : bool, optional
            A flag to set dataset visiblity to private (True) or public (False)

        Returns
        --------
        dataset : dict
            The dataset attributes

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            When there is a problem trying to parse the response as json

        HERODataRepoDatasetAlreadyExists
            If the resource already exists

        Notes
        -----
        New in version 0.2.0.
        """
        attributes = {
            "datasetId": dataset_id,
            "name": name,
            "metadata": metadata,
            "private": private,
        }

        # drop attributes that are None
        attributes = {k: v for k, v in attributes.items() if v is not None}

        # required attributes
        if "name" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "name"')
        if "metadata" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "metadata"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/dataset/{dataset_id}"
        data = json.dumps(attributes)
        try:
            response = self.api.request("PUT", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            if e.response.status_code == 400:
                response_error = e.response.json()
                raise HERODataRepoDatasetAlreadyExists(
                    response_error["error"]["message"]
                )
            raise e

    def get_or_create_dataset(
        self, project_id=None, name=None, metatype="Dataset", metadata={}, private=True
    ):
        """
        Attempt to read a dataset or create it if it does not exist.

        Parameters
        -----------
        project_id : str, required
            The UUID of a project to create the dataset in if it does not exist.

        name : str, required
            The dataset name.

        metatype : str, optional
            The dataset metatype. Defaults to "Dataset".

        metadata : dict, required
            Dataset metadata. Defaults to an empty dict.

        private : bool, optional
            A flag to set dataset visiblity to private (True) or public (False). Defaults to True.

        Returns
        --------
        dataset : dict
            The dataset attributes

        Notes
        -----
        Changed in version 0.3.0: Added support to uniquely qualify this resource in the data repo hierarchy by providing the parent resource id.

        New in version 0.2.0.
        """
        try:
            dataset = self.read_dataset_by_name(
                project_id=project_id, name=name, metatype=metatype
            )
            return dataset
        except HERODataRepoDatasetNotFound as err:
            dataset = self.add_dataset(
                project_id=project_id,
                name=name,
                private=private,
                metadata=metadata,
                metatype=metatype,
            )
            return dataset

    def read_files(self):
        """
        List files.

        Returns
        --------
        files : list of dict
            A list of files where each dict is file attributes.

        """
        # TODO: this is broken for some reason, API is returning 404 on this endpoint.
        # This is because list all files across datasets and projects is not yet implemented in the data-repo-api
        # Listing all files in a datset is available, now added fn as read_dataset_files
        headers = self.get_headers(self.client.get_token())
        url = f"{self.data_repo_url}/files"
        response = self.api.request("GET", url, headers=headers)
        return response.json()

    def read_dataset_files(self, dataset_id=None):
        """
        List files of a given dataset.

        Parameters
        -----------
        dataset_id : str, required
            The dataset UUID

        Returns
        --------
        files : list of dict
            A list of files where each dict is file attributes.

        """
        headers = self.get_headers(self.client.get_token())
        if dataset_id is None:
            raise MissingRequiredAttribute(f"Missing required attribute: {dataset_id}")
        url = "/".join([self.data_repo_url, "dataset", dataset_id, "files"])
        try:
            response = self.api.request("GET", url, headers=headers)
        except HTTPError as e:
            if e.response.status_code == 404:
                raise HERODataRepoFileNotFound()
            raise e
        return response.json()

    def read_file(self, id=None):
        """
        Read a file by id.

        Parameters
        -----------

        id : str, required
            The file UUID

        Returns
        --------
        file : dict
            The file attributes.

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        HERODataRepoFileNotFound
            If the file does not exists

        Notes
        -----
        New in version 0.2.0.
        """

        if id is None:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/file/{id}"
        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 404:
                raise HERODataRepoFileNotFound()
            raise e

    def read_file_by_name(self, dataset_id=None, name=None, metatype="File"):
        """
        Read a file by name.

        Parameters
        -----------
        dataset_id : str, optional
            The dataset name.

        name : str, required
            The file name

        metadata : dict, required
            File metadata

        Returns
        --------
        file : dict

            The file attributes.

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        HERODataRepoFileNotFound
            If the project does not exist

        Notes
        -----
        Changed in version 0.3.0:

        - Added support to uniquely qualify this resource in the data repo hierarchy by providing the parent resource id.
        - Improved building the set API params.

        Notes
        -----
        New in version 0.2.0.
        """

        if name is None:
            raise MissingRequiredAttribute('Missing required attribute: "name"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/file/metatype/{metatype}"

        params = kwargs_to_json_for_request(name=name, datasetId=dataset_id)

        try:
            response = self.api.request("GET", url, headers=headers, params=params)
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 404:
                raise HERODataRepoFileNotFound()
            raise e

    def delete_file(self, id=None):
        """
        Delete a file.

        This method only deletes a file. It does not remove any related resources and may result in orphaned resources. See the remove methods if you want to delete this an all related content.

        Parameters
        -----------
        id : str, required
            The file UUID to delete.

        Returns
        --------
        None

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        Notes
        -----
        New in version 0.2.0.
        """
        # TODO: this doesn't remove the file from S3, right now nothing does...

        if id is None:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.data_repo_url}/file/{id}"
        response = self.api.request("DELETE", url, headers=headers)
        return None

    def add_file(
        self,
        dataset_id=None,
        name=None,
        path=None,
        metatype="File",
        metadata={},
        private=True,
        id=None,
    ):
        """
        Create a new file.

        Parameters
        ----------
        dataset_id : str, required
            The dataset name.

        name : str, required
            The name of the file.

        path: str, optional
            path of file on Vast, if not using Vast should be None

        metatype : str, optional
            The file metatype. Defaults to "File".

        metadata : dict, optional
            The file metadata. Defaults to an empty dictionary.

        private : bool, optional
            The visibility of the file. Defaults to True.

        id: str, optional
            User assigned Id of the file, require admin role

        Returns
        -------
        file : dict
            The file attributes

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HERODataRepoFileAlreadyExists
            If the resource already exists

        Notes
        -----
        Changed in version 0.3.0:

        - Added support to uniquely qualify this resource in the data repo hierarchy by providing the parent resource id.
        - Added new exception when trying to add a resource that already exists.

        New in version 0.2.0.
        """
        attributes = {
            "name": name,
            "datasetId": dataset_id,
            "metatype": metatype,
            "metadata": metadata,
            "private": private,
            "path": path,
        }

        # add user assigned id if provided
        if id:
            attributes["id"] = id

        if "datasetId" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "datasetId"')
        if "name" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "name"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/file"
        data = json.dumps(attributes)
        try:
            if id:
                try:
                    self.read_project(id=id)
                    raise HERODataRepoProjectAlreadyExists(
                        f"Project with id {id} already exists"
                    )
                except HERODataRepoProjectNotFound:
                    pass
            response = self.api.request("POST", url, headers=headers, data=data)
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 400:
                response_error = e.response.json()
                raise HERODataRepoFileAlreadyExists(response_error["error"]["message"])
            raise e

    def update_file(self, file_id=None, name=None, metadata=None, private=None):
        """
        Update the attributes of a file.

        Parameters
        -----------
        file_id : str, required
            The UUID of a file

        name : str, required
            The file name

        metadata : dict, required
            File metadata

        private : bool, optional
            A flag to set file visiblity to private (True) or public (False)

        Returns
        --------
        file : dict
            The file attributes

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            When there is a problem trying to parse the response as json

        HERODataRepoFileAlreadyExists
            If the resource already exists

        Notes
        -----
        New in version 0.2.0.
        """
        if file_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "file_id"')

        attributes = {
            "name": name,
            "metadata": metadata,
            "private": private,
        }

        # drop attributes that are None
        attributes = {k: v for k, v in attributes.items() if v is not None}

        # required attributes
        if "name" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "name"')
        if "metadata" not in attributes.keys():
            raise MissingRequiredAttribute('Missing required attribute: "metadata"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/file/{file_id}"
        data = json.dumps(attributes)
        try:
            response = self.api.request("PUT", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            if e.response.status_code == 400:
                response_error = e.response.json()
                raise HERODataRepoFileAlreadyExists(response_error["error"]["message"])
            raise e

    def get_or_create_file(
        self,
        dataset_id=None,
        name=None,
        path=None,
        metatype="File",
        metadata={},
        private=True,
    ):
        """
        Attempt to read a file or create it if it does not exist.

        Parameters
        -----------
        dataset_id : str, required
            The UUID of a dataset to create the file in if it does not exist.

        name : str, required
            The file name.

        path: str, optional
            path of file on Vast, if not using Vast should be None

        metatype : str, optional
            The file metatype. Defaults to "File".

        metadata : dict, required
            File metadata. Defaults to an empty dict.

        private : bool, optional
            A flag to set file visiblity to private (True) or public (False). Defaults to True.

        Returns
        --------
        file : dict
            The file attributes

        Notes
        -----
        New in version 0.3.0.
        """
        try:
            file = self.read_file_by_name(
                dataset_id=dataset_id, name=name, metatype=metatype
            )
            return file
        except HERODataRepoFileNotFound as err:
            file = self.add_file(
                dataset_id=dataset_id,
                name=name,
                path=path,
                private=private,
                metadata=metadata,
                metatype=metatype,
            )
            return file

    def read_file_download_url(self, file_id=None):
        """
        Get a signed S3 URL from where to download the file with a GET request.

        Parameters
        -----------
        file_id : str, required
            The UUID of a file

        Returns
        --------
        url : string
            The signed S3 URL

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            When there is a problem trying to parse the response as json

        Notes
        -----
        New in version 0.2.0.
        """
        # TODO: I feel like this should be get_file_download_url, Maybe we add both?

        if file_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "file_id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/files/download/{file_id}"
        response = self.api.request("GET", url, headers=headers)
        try:
            return response.json()["url"]
        except JSONDecodeError:
            raise HEROAPIResponseException()

    def read_file_upload_url(self, file_id=None):
        """
        Get a signed S3 URL from where to upload the file with a PUT request.

        Parameters
        -----------
        file_id : str, required
            The UUID of a file

        Returns
        --------
        url : string
            The signed S3 URL

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            When there is a problem trying to parse the response as json

        Notes
        -----
        New in version 0.2.0.
        """
        # TODO: I feel like this should be get_file_upload_url, Maybe we add both?

        if file_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "file_id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/{self.data_repo_id}/files/upload/{file_id}"
        response = self.api.request("GET", url, headers=headers)
        try:
            return response.json()["url"]
        except JSONDecodeError:
            raise HEROAPIResponseException()

    def add_file_if_not_exists(
        self,
        dataset_id=None,
        local_filepath=None,
        name=None,
        path=None,
        metatype="File",
        metadata={},
        private=True,
    ):
        """
        Creates a file resource and uploads the actual file to the data repo only if it doesn't exist.

        The file exists if there is a file resource with the same name already in the data repo.

        Parameters
        -----------
        dataset_id : str, required
            The UUID of a dataset.

        local_filepath : str, required
            The path to a file to upload.

        name : str, required
            The name to give the file resource. Defaults to the name of the file to upload.

        path: str, optional
            path of file on Vast, if not using Vast should be None

        metatype : str, optional
            The file metatype. Defaults to "File".

        metadata : dict, optional
            The file metadata. Defaults to an empty dictionary.

        private : bool, optional
            The visibility of the project. Defaults to True.

        Returns
        --------
        file : dict
            The file attributes

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        Notes
        -----
        Changed in version 0.3.0: Forward arguments to subsequent methods that need them

        New in version 0.2.0.
        """
        if dataset_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "dataset_id"')
        if local_filepath is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "local_filepath"'
            )

        # TODO: what does this throw? add it to the docs.
        assert os.path.exists(local_filepath)
        if name is None:
            # TODO: this replace call seems oddly specific, what's it for?
            name = os.path.basename(local_filepath).replace("&", "and")

        try:
            file_resource = self.read_file_by_name(
                dataset_id=dataset_id, name=name, metatype=metatype
            )
            return file_resource
        except HERODataRepoFileNotFound as e:
            file_resource = self.add_file(
                dataset_id, name, path, metatype, metadata, private=private
            )
            try:
                url = self.read_file_upload_url(file_resource["id"])
                self.upload_file(url, local_filepath)
                return file_resource
            except:
                # TODO: if there is a problem uploading the file to S3 after the file resource is created we should clean it up and remove it so this call will work next time.
                self.delete_file(id=file_resource["id"])

    def add_or_replace_file(
        self,
        dataset_id=None,
        local_filepath=None,
        path=None,
        name=None,
        metatype="File",
        metadata={},
        private=True,
    ):
        """
        Creates a file resource and uploads the actual file to the data repo or replace the file if it exists.

        Parameters
        -----------
        dataset_id : str, required
            The UUID of a dataset.

        local_filepath : str, required
            The path to a file to upload.

        path: str, optional
            path of file on Vast, if not using Vast should be None

        name : str, required
            The name to give the file resource. Defaults to the name of the file to upload.

        metatype : str, optional
            The file metatype. Defaults to "File".

        metadata : dict, optional
            The file metadata. Defaults to an empty dictionary.

        private : bool, optional
            The visibility of the project. Defaults to True.

        Returns
        --------
        file : dict
            The file attributes

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        Notes
        -----
        Changed in version 0.3.0: Forward arguments to subsequent methods that need them.

        New in version 0.2.0.
        """

        if dataset_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "dataset_id"')
        if local_filepath is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "local_filepath"'
            )

        # TODO: see todo in add_file_if_not_exists
        assert os.path.exists(local_filepath)
        if name is None:
            name = os.path.basename(local_filepath).replace("&", "and")

        try:
            file_resource = self.read_file_by_name(
                dataset_id=dataset_id, name=name, metatype=metatype
            )
        except HERODataRepoFileNotFound as err:
            file_resource = self.add_file(
                dataset_id,
                name=name,
                path=path,
                metatype=metatype,
                metadata=metadata,
                private=private,
            )
        finally:
            url = self.read_file_upload_url(file_resource["id"])
            self.upload_file(url, local_filepath)
            return file_resource

    def download_file_by_name(
        self, dataset_id=None, name=None, metatype="File", local_filepath=None
    ):
        """
        Download a file with the file resource name.

        Parameters
        -----------
        dataset_id : str, optional
            The dataset name.

        name : str, required
            The name of the file.

        metatype : str, optional
            The file metatype. Defaults to "File".

        local_filepath : str, required
            The path to save the file download.

        Returns
        --------
        None

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        HERODataRepoFileNotFound
            If the project does not exist

        Notes
        -----
        Changed in version 0.3.0: Forward arguments to subsequent methods that need them

        New in version 0.2.0.
        """

        if name is None:
            raise MissingRequiredAttribute('Missing required attribute: "name"')
        if local_filepath is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "local_filepath"'
            )

        file_resource = self.read_file_by_name(
            dataset_id=dataset_id, name=name, metatype=metatype
        )
        self.download_file_by_id(file_resource["id"], local_filepath)

    def download_file_by_id(self, file_id=None, local_filepath=None):
        """
        Download a file with the file resource id.

        Parameters
        -----------
        file_id : str, required
            The file resource id.

        local_filepath : str, required
            The path to save the file download.

        Returns
        --------
        None

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        Notes
        -----
        New in version 0.2.0.
        """

        if file_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "file_id"')
        if local_filepath is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "local_filepath"'
            )

        url = self.read_file_download_url(file_id)
        self.download_file(url, local_filepath)

    def upload_file(self, url=None, local_filepath=None):
        """
        Utility function to call a signed url for file upload.

        Parameters
        -----------
        url : str, required
            The sign S3 URL.

        local_filepath : str, required
            The path to the file to upload.

        Returns
        --------
        None

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        Notes
        -----
        New in version 0.2.0.
        """

        if url is None:
            raise MissingRequiredAttribute('Missing required attribute: "url"')
        if local_filepath is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "local_filepath"'
            )

        # Read the file data
        with open(local_filepath, "rb") as file:
            file_data = file.read()

        # Make a PUT request to the signed URL
        response = self.api.put(url, data=file_data)
        return response

    def download_file(self, url=None, local_filepath=None):
        """
        Utility function to call a signed url for file download.

        Parameters
        -----------
        url : str, required
            The sign S3 URL.

        file_path : str, required
            The path to save the file download.

        Returns
        --------
        None

        Raises
        -------
        MissingRequiredAttribute
            If a required attribute is missing

        Notes
        -----
        New in version 0.2.0.
        """

        if url is None:
            raise MissingRequiredAttribute('Missing required attribute: "url"')
        if local_filepath is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "local_filepath"'
            )

        with self.api.get(url, stream=True) as r:
            r.raise_for_status()
            try:
                with open(local_filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            except Exception as e:
                # TODO: need a better exception here
                print(f"File write to disk failed with error: {str(e)}")
