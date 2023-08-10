import pytest
import hero as hq
import os

from testing_environment import HERO_CLIENT_ID, HERO_CLIENT_SECRET, HERO_PROJECT, HERO_QUEUE, HERO_QUEUE_VISIBILITY_TIMEOUT

@pytest.fixture
def queue_prefix(aws_session):
    queue_name = f'hero-{HERO_PROJECT}-dynamo-unit-test-000'
    visibility_timeout = '60'
    queue_url = hq.aws.sqs.create_queue(aws_session, queue_name, '60')
    hq.api.queue.update_queue_url(f'hero-{HERO_PROJECT}-dynamo-unit-test-000', queue_url)
    yield queue_name
    hq.aws.sqs.delete_queue(aws_session, queue_url)

def test_get_table(aws_session):
    hq.aws.dynamodb.get_table(aws_session, f'hero-{HERO_PROJECT}')

    table = hq.aws.dynamodb.get_table(aws_session, "hero-dynamodb-project-queue-names")
    try:
        table = hq.aws.dynamodb.get_table(aws_session, "hero-gantry-test-does-not-exist")
    except Exception as e:
        assert True

def test_get_queue_url(aws_session, queue_prefix):
    hq.aws.dynamodb.get_queue_url(aws_session, f'hero-{HERO_PROJECT}', queue_prefix)
    

def test_dynamo_put_item(aws_session, queue_prefix):
    queue = hq.config.config.get_queue()
    queue_url = hq.aws.dynamodb.get_queue_url(aws_session, f'hero-{HERO_PROJECT}', queue_prefix)
    data = {"name": "test-packet"}
    task = hq.task.Task(HERO_PROJECT, queue, queue_url, data)


    table = hq.aws.dynamodb.get_project_table(aws_session, HERO_PROJECT)
    hq.aws.dynamodb.put_item(table, task)

def test_dynamo_update_status(aws_session, queue_prefix):
    project = HERO_PROJECT
    queue = hq.config.config.get_queue()
    queue_url = hq.aws.dynamodb.get_queue_url(aws_session, f'hero-{HERO_PROJECT}', queue_prefix)

    data = {"name": "test-packet"}
    task = hq.task.Task(project, queue, queue_url, data)
    table = hq.aws.dynamodb.get_project_table(aws_session, project)
    hq.aws.dynamodb.put_item(table, task)

    assert hq.aws.dynamodb.update_item_claimed(table, task.id, queue) == True
    assert hq.aws.dynamodb.update_item_claimed(table, task.id, queue) == False
    assert hq.aws.dynamodb.update_item_claimed(table, task.id, queue) == False