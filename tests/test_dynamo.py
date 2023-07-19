import pytest
import hero as hq
import os

from testing_environment import HERO_CLIENT_ID, HERO_CLIENT_SECRET, HERO_PROJECT, HERO_QUEUE, HERO_QUEUE_VISIBILITY_TIMEOUT

@pytest.fixture
def queue_prefix(aws_session):
    queue_url = hq.queue.create_queue(aws_session, HERO_PROJECT, 'dynamo-unit-test-000')
    hq.dynamo.update_queue_url(aws_session, f'hero-{HERO_PROJECT}', f'hero-dynamo-unit-test-000', queue_url)
    yield 'hero-dynamo-unit-test-000'
    hq.queue.delete_queue(aws_session, queue_url)

def test_get_table(aws_session):
    hq.dynamo.get_table(aws_session, f'hero-{HERO_PROJECT}')

    table = hq.dynamo.get_table(aws_session, "hero-dynamodb-project-queue-names")
    try:
        table = hq.dynamo.get_table(aws_session, "hero-gantry-test-does-not-exist")
    except Exception as e:
        assert True

def test_get_queue_url(aws_session, queue_prefix):
    hq.dynamo.get_queue_url(aws_session, f'hero-{HERO_PROJECT}', queue_prefix)
    

def test_dynamo_put_item(aws_session, queue_prefix):
    queue = hq.session.get_queue()
    queue_url = hq.dynamo.get_queue_url(aws_session, f'hero-{HERO_PROJECT}', queue_prefix)
    data = {"name": "test-packet"}
    task = hq.task.Task(HERO_PROJECT, queue, queue_url, data)


    table = hq.dynamo.get_project_table(aws_session, HERO_PROJECT)
    hq.dynamo.put_item(table, task)

def test_dynamo_update_status(aws_session, queue_prefix):
    project = HERO_PROJECT
    queue = hq.session.get_queue()
    queue_url = hq.dynamo.get_queue_url(aws_session, f'hero-{HERO_PROJECT}', queue_prefix)

    data = {"name": "test-packet"}
    task = hq.task.Task(project, queue, queue_url, data)
    table = hq.dynamo.get_project_table(aws_session, project)
    hq.dynamo.put_item(table, task)

    assert hq.dynamo.update_item_claimed(table, task.id, queue) == True
    assert hq.dynamo.update_item_claimed(table, task.id, queue) == False
    assert hq.dynamo.update_item_claimed(table, task.id, queue) == False