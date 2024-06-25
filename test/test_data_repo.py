import hero
import os
import json


def test_bad_token():
    hero_client = hero.HeroClient()
    data_repo = hero_client.DataRepo()
    hero_client.authenticate()
    data_repo._access_token = "bad_token"
    project = data_repo.add_or_get_project("example_project")
    assert project["name"] == "example_project"


# def test_bad_data_repo_id():
#     data_repo = hero.DataRepoResilient()
#     data_repo._datarepo_id = "bad_datarepo_id"
#     project = data_repo.add_or_get_project("example_project")
#     assert project["name"] == "example_project"


# def test_add_or_get_project():
#     data_repo = hero.DataRepo()
#     project = data_repo.add_or_get_project("example_project")
#     assert project["name"] == "example_project"


# def test_add_or_get_dataset():
#     data_repo = hero.DataRepo()
#     project = data_repo.add_or_get_project("example_project")
#     dataset = data_repo.add_or_get_dataset(project, "example_dataset")
#     assert dataset["name"] == "example_dataset"


# def test_add_or_get_file_object():
#     data_repo = hero.DataRepo()
#     project = data_repo.add_or_get_project("example_project")
#     dataset = data_repo.add_or_get_dataset(project, "example_dataset")
#     file_object = data_repo.add_or_get_file_object(dataset, "example.json")
#     assert file_object["name"] == "example.json"


# def test_upload_file():
#     data_repo = hero.DataRepo()
#     project = data_repo.add_or_get_project("example_project")
#     dataset = data_repo.add_or_get_dataset(project, "example_dataset")
#     file_object = data_repo.add_or_get_file_object(dataset, "example.json")

#     with open("example.json", "w") as outfile:
#         outfile.write(json.dumps({}))

#     data_repo.upload_file(file_object, "example.json")
#     os.remove("example.json")


# def test_download_file():
#     data_repo = hero.DataRepo()
#     project = data_repo.add_or_get_project("example_project")
#     dataset = data_repo.add_or_get_dataset(project, "example_dataset")
#     file_object = data_repo.add_or_get_file_object(dataset, "example.json")
#     data_repo.download_file(file_object, "download.json")
#     os.remove("download.json")
