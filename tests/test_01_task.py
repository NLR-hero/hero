import hero as hq

hq.session.get_session()

def test_different_task_id():
    project = hq.session.get_project()
    queue = hq.session.get_queue()
    queue_url = hq.dynamo.get_queue_url(project, queue)

    data = {"name": "test-packet"}
    task1 = hq.task.Task(project, queue, queue_url, data)
    task2 = hq.task.Task(project, queue, queue_url, data)

    assert task1.task_id != task2.task_id


def test_same_task_id():
    project = hq.session.get_project()
    queue = hq.session.get_queue()
    queue_url = hq.dynamo.get_queue_url(project, queue)

    data = {"name": "test-packet"}
    task = hq.task.Task(project, queue, queue_url, data)

    # TODO this needs to be cleaned up on the project dynamo table.
    # in other words, we need to make sure that the dynamo table uses
    # task_id and queue_name not id and queue.
    raw_data = task.data
    del raw_data["id"]
    del raw_data["queue"]
    task2 = hq.task.Task(**raw_data)

    assert task.task_id == task2.task_id


def test_1000_task():
    project = hq.session.get_project()
    queue = hq.session.get_queue()
    queue_url = hq.dynamo.get_queue_url(project, queue)

    data = {"name": "test-packet"}
    tasks = []
    for i in range(1000):
        tasks.append(hq.task.Task(project, queue, queue_url, data))

    assert len(tasks) == 1000
    assert len(set([x.task_id for x in tasks])) == 1000
