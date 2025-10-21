import hero

# previously created queue
TESTABLE_QUEUE_ID = "4427b372-67a5-46c8-9e82-52fa979553d7"


def test_read_queues():
    hero_client = hero.HeroClient()
    task_engine = hero_client.TaskEngine()
    queues = task_engine.read_queues()
    assert queues is not None


def test_read_queue():
    hero_client = hero.HeroClient()
    task_engine = hero_client.TaskEngine()
    queue = task_engine.read_queue(TESTABLE_QUEUE_ID)
    assert queue["id"] == TESTABLE_QUEUE_ID


def test_add_and_delete_queue():
    hero_client = hero.HeroClient()
    task_engine = hero_client.TaskEngine()

    # add a queue
    metadata = {"description": "example_description"}
    queue = task_engine.add_queue(name="example_queue", metadata=metadata)
    tmp_queue_id = queue["id"]
    assert queue["name"] == "example_queue"

    # now delete the same queue
    queue = task_engine.delete_queue(tmp_queue_id)
    assert queue["GSI1SK"] == "METATYPE#Queue|deleted"
