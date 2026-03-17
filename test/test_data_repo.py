import pytest
import hero
import os
import datetime
import time


class TestDataRepo:
    """Comprehensive test suite for DataRepo service based on JavaScript SDK tests."""

    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Setup test client and track projects for cleanup."""
        self.hero_client = hero.HeroClient()
        self.data_repo = self.hero_client.DataRepo()
        self.test_projects = set()
        yield
        # Cleanup all test projects with cascade delete
        for project_name in self.test_projects:
            try:
                self.data_repo.remove_project_by_name(name=project_name)
            except (hero.lib.errors.HERODataRepoProjectNotFound, Exception):
                pass  # Project may already be deleted

    def register_project_for_cleanup(self, project_name):
        """Register a project for cleanup after test completion."""
        self.test_projects.add(project_name)

    def test_create_project_dataset_file(self):
        """Test creating project, dataset, and file with file data."""
        project_name = f"testing-{int(time.time())}"
        self.register_project_for_cleanup(project_name)

        # Create project
        project = self.data_repo.get_or_create_project(name=project_name)
        assert project is not None
        assert project["name"] == project_name

        # Create dataset
        dataset = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name="testing_dataset"
        )
        assert dataset is not None
        assert dataset["name"] == "testing_dataset"

        # Use local pyproject.toml file for upload
        test_file_path = os.path.join(
            os.path.dirname(__file__), "test_files", "pyproject.toml"
        )
        assert os.path.exists(test_file_path)

        # Add file with data
        file_obj = self.data_repo.add_or_replace_file(
            dataset_id=dataset["id"],
            name="pyproject.toml",
            local_filepath=test_file_path,
        )
        assert file_obj is not None
        assert file_obj["name"] == "pyproject.toml"

        # Test file download URL
        download_url = self.data_repo.read_file_download_url(file_id=file_obj["id"])
        assert download_url is not None
        assert "s3.us-west-2.amazonaws.com" in download_url

        # Test file download URL by name (parity with JS SDK)
        download_url_by_name = self.data_repo.read_file_download_url_by_name(
            datarepo_id=self.data_repo.data_repo_id,
            dataset_id=dataset["id"],
            name="pyproject.toml",
        )
        assert download_url_by_name is not None
        assert "s3.us-west-2.amazonaws.com" in download_url_by_name

    def test_create_entity_by_id(self):
        """Test creating entities with custom IDs using admin scope."""
        self.data_repo.client.add_scope("data-repo/admin")
        self.hero_client.authenticate()

        project_name = f"testing-project-uuid-name-{int(time.time())}"
        project_id = f"testing-project-uuid-{int(time.time())}"
        dataset_name = "testing-dataset-uuid-name"
        dataset_id = f"testing-dataset-uuid-{int(time.time())}"
        file_name = "testing-file-uuid-name"
        file_id = f"testing-file-uuid-{int(time.time())}"

        self.register_project_for_cleanup(project_name)

        # Create project with custom ID
        project = self.data_repo.add_project(id=project_id, name=project_name)
        assert project is not None
        assert project["name"] == project_name
        assert project["id"] == project_id

        # Create dataset with custom ID
        dataset = self.data_repo.add_dataset(
            id=dataset_id, project_id=project_id, name=dataset_name
        )
        assert dataset is not None
        assert dataset["name"] == dataset_name
        assert dataset["id"] == dataset_id

        # Create file with custom ID
        file_obj = self.data_repo.add_file(
            id=file_id, dataset_id=dataset_id, name=file_name
        )
        assert file_obj is not None
        assert file_obj["name"] == file_name
        assert file_obj["id"] == file_id

    def test_read_entity_by_name(self):
        """Test reading entities by name after creating them."""
        project_name = f"testing-read-{int(time.time())}"
        self.register_project_for_cleanup(project_name)

        # Create test data
        project = self.data_repo.get_or_create_project(name=project_name)
        assert project is not None
        assert project["name"] == project_name

        dataset = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name="testing_dataset"
        )
        assert dataset is not None
        assert dataset["name"] == "testing_dataset"

        # Use local pyproject.toml file for upload
        test_file_path = os.path.join(
            os.path.dirname(__file__), "test_files", "pyproject.toml"
        )
        assert os.path.exists(test_file_path)

        file_obj = self.data_repo.add_or_replace_file(
            dataset_id=dataset["id"],
            name="pyproject.toml",
            local_filepath=test_file_path,
        )
        assert file_obj is not None
        assert file_obj["name"] == "pyproject.toml"

        # Test reading by name
        read_project = self.data_repo.read_project_by_name(name=project_name)
        assert read_project is not None
        assert read_project["name"] == project_name

        read_dataset = self.data_repo.read_dataset_by_name(
            project_id=read_project["id"], name="testing_dataset"
        )
        assert read_dataset is not None
        assert read_dataset["name"] == "testing_dataset"

        read_file = self.data_repo.read_file_by_name(
            dataset_id=read_dataset["id"], name="pyproject.toml"
        )
        assert read_file is not None
        assert read_file["name"] == "pyproject.toml"

    def test_read_projects(self):
        """Test reading all projects."""
        projects = self.data_repo.read_projects()
        assert projects is not None
        assert isinstance(projects, list)

    def test_delete_project_by_name(self):
        """Test deleting a project by name."""
        project_name = f"testing-delete-{int(time.time())}"

        # Create project to delete (don't register for cleanup since we're testing deletion)
        project = self.data_repo.get_or_create_project(name=project_name)
        assert project is not None
        assert project["name"] == project_name

        # Delete by name
        self.data_repo.remove_project_by_name(name=project_name)

        # Verify it's gone
        with pytest.raises(hero.lib.errors.HERODataRepoProjectNotFound):
            self.data_repo.read_project_by_name(name=project_name)

    def test_create_public_entities(self):
        """Test creating public projects, datasets, and files."""
        project_name = f"testing-public-{int(time.time())}"
        self.register_project_for_cleanup(project_name)

        # Create public project
        project = self.data_repo.get_or_create_project(name=project_name, private=False)
        assert project is not None
        assert project["name"] == project_name
        assert project.get("private") == False

        # Create public dataset
        dataset = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name="testing_dataset_public", private=False
        )
        assert dataset is not None
        assert dataset["name"] == "testing_dataset_public"
        assert dataset.get("private") == False

        # Use local pyproject.toml file for upload
        test_file_path = os.path.join(
            os.path.dirname(__file__), "test_files", "pyproject.toml"
        )
        assert os.path.exists(test_file_path)

        file_obj = self.data_repo.add_or_replace_file(
            dataset_id=dataset["id"],
            name="pyproject.toml",
            local_filepath=test_file_path,
            private=False,
        )
        assert file_obj is not None
        assert file_obj["name"] == "pyproject.toml"

        # Test file deletion
        self.data_repo.delete_file(id=file_obj["id"])

    def test_create_private_entities(self):
        """Test creating private projects, datasets, and files."""
        project_name = f"testing-private-{int(time.time())}"
        self.register_project_for_cleanup(project_name)

        # Create private project
        project = self.data_repo.get_or_create_project(name=project_name, private=True)
        assert project is not None
        assert project["name"] == project_name
        assert project.get("private") == True

        # Create private dataset
        dataset = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name="testing_dataset_private", private=True
        )
        assert dataset is not None
        assert dataset["name"] == "testing_dataset_private"
        assert dataset.get("private") == True

        # Use local pyproject.toml file for upload
        test_file_path = os.path.join(
            os.path.dirname(__file__), "test_files", "pyproject.toml"
        )
        assert os.path.exists(test_file_path)

        file_obj = self.data_repo.add_or_replace_file(
            dataset_id=dataset["id"],
            name="pyproject.toml",
            local_filepath=test_file_path,
            private=True,
        )
        assert file_obj is not None
        assert file_obj["name"] == "pyproject.toml"

        # Test file deletion
        self.data_repo.delete_file(id=file_obj["id"])

    def test_add_file_with_path_parameter(self):
        """Test adding files with custom path parameters."""
        project_name = f"testing-path-param-{int(time.time())}"
        self.register_project_for_cleanup(project_name)

        # Create test project and dataset
        project = self.data_repo.get_or_create_project(name=project_name)
        assert project is not None

        dataset = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name="testing_dataset_path"
        )
        assert dataset is not None

        # Test add_file with path parameter (if supported by Python SDK)
        file_obj = self.data_repo.add_file(
            dataset_id=dataset["id"],
            name="test_path.txt",
            path="/path/test_path.txt",
            metadata={"source": "VAST"},
            private=False,
        )
        assert file_obj is not None
        assert file_obj["name"] == "test_path.txt"
        if "path" in file_obj:
            assert file_obj["path"] == "/path/test_path.txt"

        # Test add_file with null path parameter
        file_obj2 = self.data_repo.add_file(
            dataset_id=dataset["id"],
            name="no_path_file.txt",
            metadata={"source": "S3"},
            private=False,
        )
        assert file_obj2 is not None
        assert file_obj2["name"] == "no_path_file.txt"

    def test_delete_dataset_with_cascade(self):
        """Test cascade deletion of datasets."""
        project_name = f"testing-cascade-delete-dataset-{int(time.time())}"
        dataset_name = "testing_cascade_delete_dataset"
        file_name = "cascade_test_file.txt"

        self.register_project_for_cleanup(project_name)

        # Create project, dataset, and file
        project = self.data_repo.get_or_create_project(name=project_name)
        assert project["name"] == project_name

        dataset = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name=dataset_name
        )
        assert dataset["name"] == dataset_name

        # Use local pyproject.toml file for upload
        test_file_path = os.path.join(
            os.path.dirname(__file__), "test_files", "pyproject.toml"
        )
        assert os.path.exists(test_file_path)

        file_obj = self.data_repo.add_or_replace_file(
            dataset_id=dataset["id"], name=file_name, local_filepath=test_file_path
        )
        assert file_obj["name"] == file_name

        # Delete dataset with cascade
        self.data_repo.delete_dataset(id=dataset["id"], cascade=True)

        # Verify dataset is deleted
        with pytest.raises(hero.lib.errors.HERODataRepoDatasetNotFound):
            self.data_repo.read_dataset(id=dataset["id"])

        # Verify file is also deleted due to cascade
        with pytest.raises(hero.lib.errors.HERODataRepoFileNotFound):
            self.data_repo.read_file(id=file_obj["id"])

    def test_delete_project_with_cascade(self):
        """Test cascade deletion of projects."""
        project_name = f"testing-cascade-delete-project-{int(time.time())}"
        dataset_name = "testing_cascade_delete_dataset"
        file_name = "cascade_test_file.txt"

        # Create project, dataset, and file
        project = self.data_repo.get_or_create_project(name=project_name)
        assert project["name"] == project_name

        dataset = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name=dataset_name
        )
        assert dataset["name"] == dataset_name

        # Use local pyproject.toml file for upload
        test_file_path = os.path.join(
            os.path.dirname(__file__), "test_files", "pyproject.toml"
        )
        assert os.path.exists(test_file_path)

        file_obj = self.data_repo.add_or_replace_file(
            dataset_id=dataset["id"], name=file_name, local_filepath=test_file_path
        )
        assert file_obj["name"] == file_name

        # Delete project with cascade
        self.data_repo.delete_project(id=project["id"], cascade=True)

        # Verify project is deleted
        with pytest.raises(hero.lib.errors.HERODataRepoProjectNotFound):
            self.data_repo.read_project(id=project["id"])

        # Verify dataset is also deleted
        with pytest.raises(hero.lib.errors.HERODataRepoDatasetNotFound):
            self.data_repo.read_dataset(id=dataset["id"])

        # Verify file is also deleted
        with pytest.raises(hero.lib.errors.HERODataRepoFileNotFound):
            self.data_repo.read_file(id=file_obj["id"])

    def test_read_project_datasets(self):
        """Test reading datasets for a project."""
        project_name = f"testing-read-datasets-{int(time.time())}"
        dataset_name1 = "dataset_1"
        dataset_name2 = "dataset_2"

        self.register_project_for_cleanup(project_name)

        # Create project with datasets
        project = self.data_repo.get_or_create_project(name=project_name)
        assert project is not None
        assert project["name"] == project_name

        dataset1 = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name=dataset_name1
        )
        assert dataset1 is not None
        assert dataset1["name"] == dataset_name1

        dataset2 = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name=dataset_name2
        )
        assert dataset2 is not None
        assert dataset2["name"] == dataset_name2

        # Read datasets for the project
        datasets = self.data_repo.read_project_datasets(project_id=project["id"])
        assert datasets is not None
        assert len(datasets) >= 2
        dataset_names = [d["name"] for d in datasets]
        assert dataset_name1 in dataset_names
        assert dataset_name2 in dataset_names

    def test_update_project(self):
        """Test updating project properties."""
        project_name = f"testing-update-project-{int(time.time())}"
        self.register_project_for_cleanup(project_name)

        # Create project
        project = self.data_repo.get_or_create_project(name=project_name)
        assert project is not None
        assert project["name"] == project_name

        # Update project
        updated_name = f"updated-{project_name}"
        updated_project = self.data_repo.update_project(
            id=project["id"],
            name=updated_name,
            metadata={"description": "Updated project description"},
            private=True,
        )
        assert updated_project is not None
        assert updated_project["name"] == updated_name
        if "metadata" in updated_project:
            assert (
                updated_project["metadata"].get("description")
                == "Updated project description"
            )
        if "private" in updated_project:
            assert updated_project["private"] == True

        # Update cleanup name
        self.test_projects.remove(project_name)
        self.test_projects.add(updated_name)

    def test_read_datasets(self):
        """Test reading all datasets."""
        project_name = f"testing-read-datasets-{int(time.time())}"
        self.register_project_for_cleanup(project_name)

        # Create project with datasets
        project = self.data_repo.get_or_create_project(name=project_name)
        assert project is not None

        dataset1 = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name="dataset_1"
        )
        assert dataset1 is not None

        dataset2 = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name="dataset_2"
        )
        assert dataset2 is not None

        # Read all datasets
        datasets = self.data_repo.read_datasets()
        assert datasets is not None
        assert isinstance(datasets, list)

        # Check that our datasets are included
        dataset_ids = [d["id"] for d in datasets]
        assert dataset1["id"] in dataset_ids
        assert dataset2["id"] in dataset_ids

    def test_read_dataset_files(self):
        """Test reading files for a dataset."""
        project_name = f"testing-read-dataset-files-{int(time.time())}"
        dataset_name = "testing_dataset_files"

        self.register_project_for_cleanup(project_name)

        # Create project and dataset
        project = self.data_repo.get_or_create_project(name=project_name)
        assert project is not None

        dataset = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name=dataset_name
        )
        assert dataset is not None

        # Use local pyproject.toml file for upload
        test_file_path = os.path.join(
            os.path.dirname(__file__), "test_files", "pyproject.toml"
        )
        assert os.path.exists(test_file_path)

        file1 = self.data_repo.add_or_replace_file(
            dataset_id=dataset["id"],
            name="test_file_1.toml",
            local_filepath=test_file_path,
        )
        assert file1 is not None
        assert file1["name"] == "test_file_1.toml"

        file2 = self.data_repo.add_or_replace_file(
            dataset_id=dataset["id"],
            name="test_file_2.toml",
            local_filepath=test_file_path,
        )
        assert file2 is not None
        assert file2["name"] == "test_file_2.toml"

        # Read files for the dataset
        files = self.data_repo.read_dataset_files(dataset_id=dataset["id"])
        assert files is not None
        assert len(files) >= 2
        file_names = [f["name"] for f in files]
        assert "test_file_1.toml" in file_names
        assert "test_file_2.toml" in file_names
        file_ids = [f["id"] for f in files]
        assert file1["id"] in file_ids
        assert file2["id"] in file_ids

    def test_remove_dataset_by_name(self):
        """Test removing dataset by name with cascade."""
        project_name = f"testing-remove-dataset-by-name-{int(time.time())}"
        dataset_name = "testing_dataset_to_remove"

        self.register_project_for_cleanup(project_name)

        # Create project and dataset
        project = self.data_repo.get_or_create_project(name=project_name)
        assert project is not None

        dataset = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name=dataset_name
        )
        assert dataset is not None

        # Use local pyproject.toml file for upload
        test_file_path = os.path.join(
            os.path.dirname(__file__), "test_files", "pyproject.toml"
        )
        assert os.path.exists(test_file_path)

        file_obj = self.data_repo.add_or_replace_file(
            dataset_id=dataset["id"],
            name="test_file_cascade.toml",
            local_filepath=test_file_path,
        )
        assert file_obj is not None
        assert file_obj["name"] == "test_file_cascade.toml"

        # Remove dataset by name with cascade
        self.data_repo.remove_dataset_by_name(
            project_id=project["id"], name=dataset_name, cascade=True
        )

        # Verify dataset is deleted
        with pytest.raises(hero.lib.errors.HERODataRepoDatasetNotFound):
            self.data_repo.read_dataset_by_name(
                project_id=project["id"], name=dataset_name
            )

        # Verify file is also deleted due to cascade
        with pytest.raises(hero.lib.errors.HERODataRepoFileNotFound):
            self.data_repo.read_file(id=file_obj["id"])

    def test_update_dataset(self):
        """Test updating dataset properties."""
        project_name = f"testing-update-dataset-{int(time.time())}"
        dataset_name = "testing_dataset_update"

        self.register_project_for_cleanup(project_name)

        # Create project and dataset
        project = self.data_repo.get_or_create_project(name=project_name)
        assert project is not None

        dataset = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name=dataset_name
        )
        assert dataset is not None

        # Update dataset
        updated_name = f"updated_{dataset_name}"
        updated_dataset = self.data_repo.update_dataset(
            dataset_id=dataset["id"],
            name=updated_name,
            metadata={"description": "Updated dataset description"},
            private=True,
        )
        assert updated_dataset is not None
        assert updated_dataset["name"] == updated_name
        if "metadata" in updated_dataset:
            assert (
                updated_dataset["metadata"].get("description")
                == "Updated dataset description"
            )
        if "private" in updated_dataset:
            assert updated_dataset["private"] == True

    def test_read_files(self):
        """Test reading all files."""
        project_name = f"testing-read-files-{int(time.time())}"
        self.register_project_for_cleanup(project_name)

        # Create project, dataset and files first
        project = self.data_repo.get_or_create_project(name=project_name)
        assert project is not None

        dataset = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name="testing_dataset_files"
        )
        assert dataset is not None

        # Use existing pyproject.toml file for upload
        test_file_path = os.path.join(
            os.path.dirname(__file__), "test_files", "pyproject.toml"
        )
        assert os.path.exists(test_file_path)

        # Upload the same file twice with different names
        file1 = self.data_repo.add_or_replace_file(
            dataset_id=dataset["id"],
            name="global_test_file_1.toml",
            local_filepath=test_file_path,
            private=False,
        )
        assert file1 is not None

        file2 = self.data_repo.add_or_replace_file(
            dataset_id=dataset["id"],
            name="global_test_file_2.toml",
            local_filepath=test_file_path,
            private=False,
        )
        assert file2 is not None

        # Read all files in the dataset using read_files
        files = self.data_repo.read_files(dataset_id=dataset["id"])
        assert files is not None
        assert isinstance(files, list)

        # Check that our test files are included in the results
        file_ids = [f["id"] for f in files]
        file_names = [f["name"] for f in files]

        assert file1["id"] in file_ids
        assert file2["id"] in file_ids
        assert "global_test_file_1.toml" in file_names
        assert "global_test_file_2.toml" in file_names

    def test_update_file(self):
        """Test updating file properties."""
        project_name = f"testing-update-file-{int(time.time())}"
        self.register_project_for_cleanup(project_name)

        # Create project, dataset, and file
        project = self.data_repo.get_or_create_project(name=project_name)
        dataset = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name="test_dataset"
        )

        # Use local pyproject.toml file for upload
        test_file_path = os.path.join(
            os.path.dirname(__file__), "test_files", "pyproject.toml"
        )
        assert os.path.exists(test_file_path)

        file_obj = self.data_repo.add_or_replace_file(
            dataset_id=dataset["id"],
            name="test_file_update.toml",
            local_filepath=test_file_path,
            metadata={
                "description": "Original file description",
                "version": "1.0",
                "author": "Original Author",
            },
            private=False,
        )
        assert file_obj is not None
        assert file_obj["name"] == "test_file_update.toml"
        assert file_obj.get("private") == False

        # Update file
        updated_name = "updated_file_name.toml"
        updated_file = self.data_repo.update_file(
            file_id=file_obj["id"],
            name=updated_name,
            metadata={
                "description": "Updated file description",
                "version": "2.0",
                "author": "Updated Author",
                "lastModified": datetime.datetime.now().isoformat(),
            },
            private=True,
        )
        assert updated_file is not None
        assert updated_file["name"] == updated_name
        if "metadata" in updated_file:
            assert (
                updated_file["metadata"].get("description")
                == "Updated file description"
            )
            assert updated_file["metadata"].get("version") == "2.0"
            assert updated_file["metadata"].get("author") == "Updated Author"
            assert updated_file["metadata"].get("lastModified") is not None
        if "private" in updated_file:
            assert updated_file["private"] == True

    def test_file_upload_download_urls(self):
        """Test getting file upload and download URLs."""
        project_name = f"testing-upload-download-urls-{int(time.time())}"
        self.register_project_for_cleanup(project_name)

        # Create project, dataset, and file
        project = self.data_repo.get_or_create_project(name=project_name)
        dataset = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name="test_dataset"
        )
        file_obj = self.data_repo.get_or_create_file(
            dataset_id=dataset["id"], name="test_file_urls.txt"
        )

        # Test upload URL
        upload_url = self.data_repo.read_file_upload_url(file_id=file_obj["id"])
        assert upload_url is not None
        assert isinstance(upload_url, str)

        # Test download URL
        download_url = self.data_repo.read_file_download_url(file_id=file_obj["id"])
        assert download_url is not None
        assert isinstance(download_url, str)

    def test_upload_download_file(self):
        """Test complete upload and download file workflow."""
        project_name = f"testing-upload-download-{int(time.time())}"
        self.register_project_for_cleanup(project_name)

        # Create project, dataset, and file
        project = self.data_repo.get_or_create_project(name=project_name)
        dataset = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name="test_dataset"
        )

        # Use local pyproject.toml file for upload and download
        test_file_path = os.path.join(
            os.path.dirname(__file__), "test_files", "pyproject.toml"
        )
        assert os.path.exists(test_file_path)

        # Upload file
        file_obj = self.data_repo.add_or_replace_file(
            dataset_id=dataset["id"],
            name="upload_download_test.toml",
            local_filepath=test_file_path,
        )
        assert file_obj is not None
        assert file_obj["name"] == "upload_download_test.toml"

        # Download file by ID
        download_filepath = f"{test_file_path}.downloaded"
        self.data_repo.download_file_by_id(
            file_id=file_obj["id"], local_filepath=download_filepath
        )
        assert os.path.exists(download_filepath)
        with open(test_file_path, "r") as f:
            original_content = f.read()
        with open(download_filepath, "r") as f:
            downloaded_content = f.read()
        assert downloaded_content == original_content

        # Download file by name
        download_filepath2 = f"{test_file_path}.downloaded2"
        self.data_repo.download_file_by_name(
            dataset_id=dataset["id"],
            name="upload_download_test.toml",
            local_filepath=download_filepath2,
        )
        assert os.path.exists(download_filepath2)
        with open(download_filepath2, "r") as f:
            downloaded_content2 = f.read()
        assert downloaded_content2 == original_content

        # Cleanup only downloaded temp files, not the original local test file
        for filepath in [download_filepath, download_filepath2]:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_file_download_url_from_hierarchy(self):
        """Test getting file download URL from project/dataset/file hierarchy."""
        project_name = f"testing-hierarchy-{int(time.time())}"
        self.register_project_for_cleanup(project_name)

        # Create project
        project = self.data_repo.get_or_create_project(name=project_name)
        assert project is not None
        assert project["name"] == project_name

        # Create dataset
        dataset = self.data_repo.get_or_create_dataset(
            project_id=project["id"], name="testing_hierarchy_dataset"
        )
        assert dataset is not None
        assert dataset["name"] == "testing_hierarchy_dataset"

        # Use local pyproject.toml file for upload
        test_file_path = os.path.join(
            os.path.dirname(__file__), "test_files", "pyproject.toml"
        )
        assert os.path.exists(test_file_path)

        # Add file
        file_obj = self.data_repo.add_or_replace_file(
            dataset_id=dataset["id"],
            name="hierarchy_test_file.toml",
            local_filepath=test_file_path,
        )
        assert file_obj is not None
        assert file_obj["name"] == "hierarchy_test_file.toml"

        # Get download URL from hierarchy
        download_url = self.data_repo.read_file_download_url_from_hierarchy(
            project_name=project_name,
            dataset_name=dataset["name"],
            project_metatype="Project",
            dataset_metatype="Dataset",
            file_metatype="File",
            file_name="hierarchy_test_file.toml",
        )
        assert download_url is not None
        assert "s3.us-west-2.amazonaws.com" in download_url

    def test_read_projects_with_pagination(self):
        """Test reading projects with pagination enabled."""
        result = self.data_repo.read_projects(use_pagination=True)
        assert result is not None
        assert "items" in result
        assert isinstance(result["items"], list)
        if result.get("lastEvaluatedKey") is not None:
            assert isinstance(result["lastEvaluatedKey"], str)

    def test_read_project_datasets_with_pagination(self):
        """Test reading project datasets with pagination enabled."""
        project_name = f"testing-pagination-datasets-{int(time.time())}"
        self.register_project_for_cleanup(project_name)

        project = self.data_repo.get_or_create_project(name=project_name)
        self.data_repo.add_dataset(
            project_id=project["id"], name="pagination-dataset-1"
        )
        self.data_repo.add_dataset(
            project_id=project["id"], name="pagination-dataset-2"
        )

        result = self.data_repo.read_project_datasets(
            project_id=project["id"], use_pagination=True
        )
        assert result is not None
        assert "items" in result
        assert isinstance(result["items"], list)
        assert len(result["items"]) >= 2

    def test_read_dataset_files_with_pagination(self):
        """Test reading dataset files with pagination enabled."""
        project_name = f"testing-pagination-files-{int(time.time())}"
        self.register_project_for_cleanup(project_name)

        project = self.data_repo.get_or_create_project(name=project_name)
        dataset = self.data_repo.add_dataset(
            project_id=project["id"], name="pagination-dataset"
        )
        self.data_repo.add_file(dataset_id=dataset["id"], name="file-1.txt")
        self.data_repo.add_file(dataset_id=dataset["id"], name="file-2.txt")

        result = self.data_repo.read_dataset_files(
            dataset_id=dataset["id"], use_pagination=True
        )
        assert result is not None
        assert "items" in result
        assert isinstance(result["items"], list)
        assert len(result["items"]) >= 2
