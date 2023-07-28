import pytest
import hero as hq

def test_get_aws_credentials_is_empty():
    aws_credentials = hq.config.config.get_aws_credentials()
    assert aws_credentials is None

def test_get_aws_credentials(aws_credentials):
    hq.config.config.export_session_to_env(aws_credentials)
    aws_credentials = hq.config.config.get_aws_credentials()
    assert 'AccessKeyId' in aws_credentials
    assert 'SecretAccessKey' in aws_credentials
    assert 'SessionToken' in aws_credentials


from testing_environment import HERO_CLIENT_ID, HERO_CLIENT_SECRET, HERO_PROJECT, HERO_QUEUE, HERO_QUEUE_VISIBILITY_TIMEOUT

def test_get_session():
    assert True

def test_get_client_credentials():
    client_id, client_secret = hq.config.config.get_client_credentials()
    assert client_id == HERO_CLIENT_ID
    assert client_secret == HERO_CLIENT_SECRET

def test_get_project():
    project = hq.config.config.get_project()
    assert project == HERO_PROJECT

    project = hq.config.config.get_project('custom-project')
    assert project == 'custom-project'

def test_get_queue():
    queue = hq.config.config.get_queue()
    assert queue == HERO_QUEUE

    queue = hq.config.config.get_queue('custom-queue')
    assert queue == 'custom-queue'

def test_get_queue_visibility_timeout():
    queue_visibility_timeout = hq.config.config.get_queue_visibility_timeout()
    assert queue_visibility_timeout == HERO_QUEUE_VISIBILITY_TIMEOUT