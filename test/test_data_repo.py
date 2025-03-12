import pytest
import hero
import os
import json
import time


def test_project():

    hero_client = hero.HeroClient()
    data_repo = hero_client.DataRepo()
    hero_client.authenticate()

    project_name = "Test Project"

    # project does not exists
    with pytest.raises(hero.lib.errors.HERODataRepoProjectNotFound) as e:
        project = data_repo.read_project_by_name(name=project_name)

    project = data_repo.get_or_create_project(name=project_name)
    assert project["name"] == project_name

    project = data_repo.read_project_by_name(name=project_name)
    assert project["name"] == project_name

    exists = False
    projects = data_repo.read_projects()
    for project in projects:
        if project["name"] == project_name:
            exists = True
            break

    assert exists == True

    # clean up
    data_repo.remove_project_by_name(name="Test Project")

    with pytest.raises(hero.lib.errors.HERODataRepoProjectNotFound) as e:
        project = data_repo.read_project_by_name(name=project_name)


def test_datasets():

    hero_client = hero.HeroClient()
    data_repo = hero_client.DataRepo()
    hero_client.authenticate()
    project_name = "Test Project"
    dataset_name = "Test Dataset"

    # ensure we can create and get, so 2x
    project = data_repo.get_or_create_project(name=project_name)
    assert project["name"] == project_name

    project = data_repo.get_or_create_project(name=project_name)
    assert project["name"] == project_name

    dataset = data_repo.get_or_create_dataset(
        project_id=project["id"], name=dataset_name
    )
    assert dataset["name"] == dataset_name

    dataset = data_repo.read_dataset_by_name(
        name=dataset_name, project_id=project["id"]
    )
    assert dataset["name"] == dataset_name

    data_repo.delete_project(id=project["id"], cascade=True)

    with pytest.raises(hero.lib.errors.HERODataRepoDatasetNotFound) as e:
        project = data_repo.read_dataset_by_name(
            name=dataset_name, project_id=project["id"]
        )

    # This endpoint does not exists: Not Found for url: https://dev-hero.nrel.gov/data-repo/api/v1/PROJECT-NAME/datasets
    datasets = data_repo.read_datasets()
    for dataset in datasets:
        print(dataset)


def test_files():

    hero_client = hero.HeroClient()
    data_repo = hero_client.DataRepo()
    hero_client.authenticate()
    project_name = "Test Project"
    dataset_name = "Test Dataset"
    file_name = "Test File"

    project = data_repo.get_or_create_project(name=project_name)
    assert project["name"] == project_name

    dataset = data_repo.get_or_create_dataset(
        project_id=project["id"], name=dataset_name
    )
    assert dataset["name"] == dataset_name

    file_obj = data_repo.get_or_create_file(dataset_id=dataset["id"], name=file_name)
    assert file_obj["name"] == file_name

    with open("tmp", "w") as outfile:
        outfile.write("This is just a test file")

    file_obj = data_repo.add_or_replace_file(
        dataset_id=dataset["id"], name=file_name, local_filepath="tmp"
    )
    assert file_obj["name"] == file_name

    data_repo.download_file_by_name(
        dataset_id=dataset["id"], name=file_name, local_filepath="tmp_download"
    )

    os.remove("tmp")
    os.remove("tmp_download")
    data_repo.delete_project(id=project["id"], cascade=True)

def test_create_entity_by_id():
    hero_client = hero.HeroClient()
    data_repo = hero_client.DataRepo()
    # add scope for special permissions
    data_repo.client.add_scope("data-repo/admin")
    hero_client.authenticate()
    project_name = "testing-project-uuid-name"
    project_id = "testing-project-uuid"
    dataset_name = "testing-dataset-uuid-name"
    dataset_id = "testing-dataset-uuid"
    file_name = "testing-file-uuid-name"
    file_id = "testing-file-uuid"

    project = data_repo.add_project(id=project_id, name=project_name)
    assert project["name"] == project_name
    assert project["id"] == project_id

    dataset = data_repo.add_dataset(id=dataset_id, project_id=project_id, name=dataset_name)
    assert dataset["name"] == dataset_name
    assert dataset["id"] == dataset_id

    file_obj = data_repo.add_file(id=file_id, dataset_id=dataset_id, name=file_name)
    assert file_obj["name"] == file_name
    assert file_obj["id"] == file_id
    
    data_repo.delete_project(id=project["id"], cascade=True)
    
