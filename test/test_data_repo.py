import hero
import os
import json

APP_ID = 'dev-hero-test-framework'

# previously created project
TESTABLE_PROJECT_ID = 'd16c1abb-b9a9-449e-aef4-af48d4958826'

def test_get_project():
    hero_client = hero.HeroClient()
    data_repo = hero_client.DataRepo()
    hero_client.authenticate()
    project = data_repo.get_project(APP_ID, TESTABLE_PROJECT_ID)
    assert project['name'] == 'example_project'

def test_get_projects():
    hero_client = hero.HeroClient()
    data_repo = hero_client.DataRepo()
    hero_client.authenticate()
    projects = data_repo.get_projects(APP_ID)
    assert projects is not None

def test_add_and_delete_project():
    hero_client = hero.HeroClient()
    data_repo = hero_client.DataRepo()
    hero_client.authenticate()

    # add a project
    project_attributes = {
        'name': 'example_project',
        'description': 'example_description'
    }
    project = data_repo.add_project(APP_ID, project_attributes)
    tmp_project_id = project['id']
    assert project['name'] == 'example_project'

    # now delete the same project
    project = data_repo.delete_project(APP_ID, tmp_project_id)
    tmp_project_id = None
    assert project is None

# this fails, not sure what the correct usage of underlying update_project api
def test_update_project():
    hero_client = hero.HeroClient()
    data_repo = hero_client.DataRepo()
    hero_client.authenticate()

    project_attributes = {
        'name': 'tmp_example_project'
    }
    project = data_repo.add_project(APP_ID, project_attributes)
    tmp_project_id = project['id']

    project_attributes = {
        'name': 'new_example_project'
    }
    project = data_repo.update_project(APP_ID, tmp_project_id, project_attributes)
    # project = data_repo.get_project(APP_ID, tmp_project_id)
    assert project['name'] == 'new_example_project'

    project = data_repo.delete_project(APP_ID, tmp_project_id)
    tmp_project_id = None
    assert project is None

