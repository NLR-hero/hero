import hero
import pytest
import uuid
import os

APP_ID = 'dev-hero-test-framework'

# previously created queue
TESTABLE_QUEUE_ID = 'f465d37c-8de9-4f39-8e91-70a00dcd4d45'

def test_get_queues():
    hero_client = hero.HeroClient()
    task_engine = hero_client.TaskEngine()
    hero_client.authenticate()
    queues = task_engine.get_queues(APP_ID)
    assert queues is not None

def test_get_queue():
    hero_client = hero.HeroClient()
    task_engine = hero_client.TaskEngine()
    hero_client.authenticate()
    queue = task_engine.get_queue(APP_ID, TESTABLE_QUEUE_ID)
    assert queue['id'] == TESTABLE_QUEUE_ID

def test_add_and_delete_queue():
    hero_client = hero.HeroClient()
    task_engine = hero_client.TaskEngine()
    hero_client.authenticate()

    # add a queue
    queue_attributes = {
        'name': 'example_queue',
        'description': 'example_description'
    }
    queue = task_engine.add_queue(APP_ID, queue_attributes)
    print(queue)
    tmp_queue_id = queue['id']
    assert queue['name'] == 'example_queue'

    # now delete the same queue
    queue = task_engine.delete_queue(APP_ID, tmp_queue_id)
    tmp_queue_id = None
    assert queue['GSI1SK'] == 'METATYPE#Queue|deleted'

