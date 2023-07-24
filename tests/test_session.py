import hero as hq

from testing_environment import HERO_CLIENT_ID, HERO_CLIENT_SECRET, HERO_PROJECT, HERO_QUEUE, HERO_QUEUE_VISIBILITY_TIMEOUT

def test_get_session():
    assert True

def test_get_client_credentials():
    client_id, client_secret = hq.config.get_client_credentials()
    assert client_id == HERO_CLIENT_ID
    assert client_secret == HERO_CLIENT_SECRET

def test_get_project():
    project = hq.config.get_project()
    assert project == HERO_PROJECT

    project = hq.config.get_project('custom-project')
    assert project == 'custom-project'

def test_get_queue():
    queue = hq.config.get_queue()
    assert queue == HERO_QUEUE

    queue = hq.config.get_queue('custom-queue')
    assert queue == 'custom-queue'

def test_get_queue_visibility_timeout():
    queue_visibility_timeout = hq.config.get_queue_visibility_timeout()
    assert queue_visibility_timeout == HERO_QUEUE_VISIBILITY_TIMEOUT