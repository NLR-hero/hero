import hero
import pytest
import uuid
import os

ATTEMPT_NUMBER = 2
os.environ["HERO_RETRY_ATTEMPTS"] = f"{ATTEMPT_NUMBER}"
os.environ["HERO_RETRY_WAIT"] = "fix"  # ["fix", "exp"]


# def test_bad_token():
#     hero_client = hero.HeroClient()
#     task_engine = hero_client.TaskEngine("queue-003")
#     task_engine.clear_queue()
#     task_engine._token = "badtoken"
#     queue_id = task_engine.queue_id
#     assert queue_id is not None


# def test_no_active_queue():
#     hero_client = hero.HeroClient()
#     queue_name = f"queue-{str(uuid.uuid4())}"
#     task_engine = hero_client.TaskEngine(queue_name)
#     with pytest.raises(hero.errors.HeroRetryError) as e_info:
#         queue_id = task_engine.queue_id
#         assert e_info.value.message == f"{queue_name} queue not active in DynamoDB"
#         assert e_info.value.attempt_number == ATTEMPT_NUMBER


# def test_bad_queue():
#     task_engine = hero.TaskEngine("queue-003")
#     task_engine.clear_queue()
#     task_engine._queue = "bad_queue"
#     queue_id = task_engine.queue_id
#     assert queue_id is not None


# def test_old_sqs_queue():
#     task_engine = hero.TaskEngine("queue-003")
#     task_engine.clear_queue()

#     task_worker = hero.TaskEngine("queue-003")
#     queue_id = task_worker.queue_id
#     task_engine.clear_queue()

#     assert queue_id == task_worker.queue_id
#     assert task_engine.queue_id != task_worker.queue_id
#     tasks = task_worker.estimate_ready_tasks()
#     assert task_engine.queue_id == task_worker.queue_id


# def test_put_tasks():
#     task_engine = hero.TaskEngine("queue-003")
#     task_engine.clear_queue()
#     task_engine.put_tasks([{}])


# def test_pull_task_from_old_queue():
#     task_engine = hero.TaskEngine("queue-003")
#     task_engine.clear_queue()

#     task_worker = hero.TaskEngine("queue-003")
#     queue_id = task_worker.queue_id
#     task_engine.clear_queue()
#     task_engine.put_tasks([{}])

#     assert queue_id == task_worker.queue_id
#     assert task_engine.queue_id != task_worker.queue_id
#     tasks = task_worker.pull_tasks(attempts=4)
#     assert len(tasks) == 1


# def test_put_tasks_deleted_queue():
#     task_engine = hero.TaskEngine("queue-003")
#     task_engine.add_or_get_queue()
#     task_engine.delete_queue()
#     with pytest.raises(hero.errors.HeroRetryError) as e_info:
#         task_engine.put_tasks([{}], attempts=1)
#         assert e_info.value.attempt_number == 1
#         assert e_info.value.message == "queue-003 queue not active in DynamoDB"


# def test_update_task():
#     task_engine = hero.TaskEngine("queue-003")
#     task_engine.add_or_get_queue()
#     task_engine.put_tasks([{}])
#     tasks = task_engine.pull_tasks()
#     for task in tasks:
#         task_engine.update_task(task, {"results": "done"})


# def test_pull_tasks():
#     task_engine = hero.TaskEngine("queue-003")
#     task_engine.clear_queue()
#     with pytest.raises(hero.errors.HeroRetryError) as e_info:
#         task_engine.pull_tasks(attempts=5, wait="exp")
#         assert e_info.value.message == "queue-003 queue is not active"
#         assert e_info.value.attempt_number == 2
