import hero
import os
import json
import time

HERO_ENV = "dev"
HERO_APP_NAME = "hero-test-framework"


def get_data_repo():
    # slow down for localhost testing...
    time.sleep(1)
    hero_client = hero.HeroClient()
    data_repo = hero_client.DataRepo()
    hero_client.authenticate()
    return data_repo


def test_delete():
    data_repo = get_data_repo()
    data_repo.remove_project_by_name("testing")
    projects = data_repo.get_projects()
    assert "testing" not in [p["name"] for p in projects]


def test_create_project_dataset_file():
    data_repo = get_data_repo()
    project = data_repo.get_or_create_project("testing")
    assert project["name"] == "testing"

    dataset = data_repo.get_or_create_dataset(project["id"], "testing_dataset")
    assert dataset["name"] == "testing_dataset"

    fileobj = data_repo.add_file_if_not_exists(
        dataset["id"], "pyproject.toml", "testing_file"
    )
    assert fileobj["name"] == "testing_file"


def test_read_by_name():
    data_repo = get_data_repo()
    project2 = data_repo.read_project_by_name("testing")
    assert project2["name"] == "testing"

    dataset2 = data_repo.read_dataset_by_name("testing_dataset")
    assert dataset2["name"] == "testing_dataset"

    fileobj2 = data_repo.read_file_by_name("testing_file")
    assert fileobj2["name"] == "testing_file"


def test_get_projects():
    data_repo = get_data_repo()
    projects = data_repo.get_projects()
    assert projects is not None


def test_create_public_file():
    """
    The API doesn't return `private` in the fileobj, so I uesed the web app to verify.
    Also
    """
    data_repo = get_data_repo()
    data_repo.remove_project_by_name("testing_public")
    project = data_repo.get_or_create_project("testing_public", private=False)
    assert project["name"] == "testing_public"
    assert project["private"] == False

    dataset = data_repo.get_or_create_dataset(
        project["id"], "testing_dataset_public", private=False
    )
    print("testing_dataset_public", dataset)
    assert dataset["name"] == "testing_dataset_public"
    assert dataset["private"] == False

    fileobj = data_repo.add_file_if_not_exists(
        dataset["id"], "pyproject.toml", "testing_file_public", private=False
    )
    assert fileobj["name"] == "testing_file_public"
    print(fileobj)


def test_create_private_file():
    """
    The API doesn't return `private` in the fileobj, so I uesed the web app to verify.
    BUG: Also, setting a project to private means it no longer is visible in the web app
    even when logged in.
    """
    data_repo = get_data_repo()
    data_repo.remove_project_by_name("testing_private")
    project = data_repo.get_or_create_project("testing_private", private=True)
    assert project["name"] == "testing_private"
    assert project["private"] == True

    dataset = data_repo.get_or_create_dataset(
        project["id"], "testing_dataset_private", private=True
    )
    print("testing_dataset_private", dataset)
    assert dataset["name"] == "testing_dataset_private"
    assert dataset["private"] == True

    fileobj = data_repo.add_file_if_not_exists(
        dataset["id"], "pyproject.toml", "testing_file_private", private=True
    )
    assert fileobj["name"] == "testing_file_private"
    print(fileobj)


def test_file_update():
    """
    The updateItem method fails on the API
    Error inserting item: TypeError: Cannot read properties of undefined (reading 'S')
    at AttributeValue.visit (/Users/mlunacek/research/hero/hero-data-repo-api/node_modules/@aws-sdk/client-dynamodb/dist-cjs/models/models_0.js:620:19)
    at se_AttributeValue (/Users/mlunacek/research/hero/hero-data-repo-api/node_modules/@aws-sdk/client-dynamodb/dist-cjs/protocols/Aws_json1_0.js:2948:38)
    at /Users/mlunacek/research/hero/hero-data-repo-api/node_modules/@aws-sdk/client-dynamodb/dist-cjs/protocols/Aws_json1_0.js:3151:20
    at Array.reduce (<anonymous>)
    at se_ExpressionAttributeValueMap (/Users/mlunacek/research/hero/hero-data-repo-api/node_modules/@aws-sdk/client-dynamodb/dist-cjs/protocols/Aws_json1_0.js:3147:34)
    at ExpressionAttributeValues (/Users/mlunacek/research/hero/hero-data-repo-api/node_modules/@aws-sdk/client-dynamodb/dist-cjs/protocols/Aws_json1_0.js:3535:43)
    at applyInstruction (/Users/mlunacek/research/hero/hero-data-repo-api/node_modules/@aws-sdk/client-dynamodb/node_modules/@smithy/smithy-client/dist-cjs/object-mapping.js:73:33)
    at take (/Users/mlunacek/research/hero/hero-data-repo-api/node_modules/@aws-sdk/client-dynamodb/node_modules/@smithy/smithy-client/dist-cjs/object-mapping.js:44:9)
    at se_UpdateItemInput (/Users/mlunacek/research/hero/hero-data-repo-api/node_modules/@aws-sdk/client-dynamodb/dist-cjs/protocols/Aws_json1_0.js:3529:37)
    at se_UpdateItemCommand (/Users/mlunacek/research/hero/hero-data-repo-api/node_modules/@aws-sdk/client-dynamodb/dist-cjs/protocols/Aws_json1_0.js:357:27)
    """
    data_repo = get_data_repo()
    data_repo.remove_project_by_name("testing_public")
    project = data_repo.get_or_create_project("testing_public", private=False)
    assert project["name"] == "testing_public"
    assert project["private"] == False

    dataset = data_repo.get_or_create_dataset(
        project["id"], "testing_dataset_public", private=False
    )
    print("testing_dataset_public", dataset)
    assert dataset["name"] == "testing_dataset_public"
    assert dataset["private"] == False

    fileobj = data_repo.add_file_if_not_exists(
        dataset["id"], "pyproject.toml", "testing_file_public", private=False
    )
    assert fileobj["name"] == "testing_file_public"

    fileobj = data_repo.update_file(fileobj["id"], {"private": True})
    print(fileobj)


# Previous tests that use the original attributes API.

# previously created project
# TESTABLE_PROJECT_ID = "d16c1abb-b9a9-449e-aef4-af48d4958826"
# def test_get_project():
#     hero_client = hero.HeroClient()
#     data_repo = hero_client.DataRepo()
#     hero_client.authenticate()
#     project = data_repo.get_project(APP_ID, TESTABLE_PROJECT_ID)
#     assert project["name"] == "example_project"


# def test_add_and_delete_project():
#     hero_client = hero.HeroClient()
#     data_repo = hero_client.DataRepo()
#     hero_client.authenticate()

#     # add a project
#     project_attributes = {
#         "name": "example_project",
#         "description": "example_description",
#     }
#     project = data_repo.add_project(APP_ID, project_attributes)
#     tmp_project_id = project["id"]
#     assert project["name"] == "example_project"

#     # now delete the same project
#     project = data_repo.delete_project(APP_ID, tmp_project_id)
#     tmp_project_id = None
#     assert project is None


# # this fails, not sure what the correct usage of underlying update_project api
# def test_update_project():
#     hero_client = hero.HeroClient()
#     data_repo = hero_client.DataRepo()
#     hero_client.authenticate()

#     project_attributes = {"name": "tmp_example_project"}
#     project = data_repo.add_project(APP_ID, project_attributes)
#     tmp_project_id = project["id"]

#     project_attributes = {"name": "new_example_project"}
#     project = data_repo.update_project(APP_ID, tmp_project_id, project_attributes)
#     # project = data_repo.get_project(APP_ID, tmp_project_id)
#     assert project["name"] == "new_example_project"

#     project = data_repo.delete_project(APP_ID, tmp_project_id)
#     tmp_project_id = None
#     assert project is None
