import hero
import pytest
import uuid
import os

APP_ID = "hero-test-framework"

# previously created queue
TESTABLE_QUEUE_ID = "4427b372-67a5-46c8-9e82-52fa979553d7"


def test_read_queues():
    hero_client = hero.HeroClient()
    task_engine = hero_client.TaskEngine()
    hero_client.authenticate()
    queues = task_engine.read_queues(APP_ID)
    assert queues is not None


def test_create_queue():
    hero_client = hero.HeroClient()
    task_engine = hero_client.TaskEngine()
    hero_client.authenticate()

    queue_attributes = {"name": "example_queue", "description": "example_description"}
    queue = task_engine.create_queue(APP_ID, queue_attributes)
    assert queue["name"] == "example_queue"


# def test_read_queue():
#     hero_client = hero.HeroClient()
#     task_engine = hero_client.TaskEngine()
#     hero_client.authenticate()
#     queue = task_engine.read_queue(APP_ID, TESTABLE_QUEUE_ID)
#     print(queue)
#     assert queue['id'] == TESTABLE_QUEUE_ID

# def test_add_and_delete_queue():
#     hero_client = hero.HeroClient()
#     task_engine = hero_client.TaskEngine()
#     hero_client.authenticate()

#     # add a queue
#     queue_attributes = {
#         'name': 'example_queue',
#         'description': 'example_description'
#     }
#     queue = task_engine.add_queue(APP_ID, queue_attributes)
#     tmp_queue_id = queue['id']
#     assert queue['name'] == 'example_queue'

#     # now delete the same queue
#     queue = task_engine.delete_queue(APP_ID, tmp_queue_id)
#     tmp_queue_id = None
#     assert queue['GSI1SK'] == 'METATYPE#Queue|deleted'
