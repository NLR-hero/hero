import pytest
import hero
import os
import json
import time


def test_project():

    hero_client = hero.HeroClient()
    data_repo = hero_client.DataRepo()

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
