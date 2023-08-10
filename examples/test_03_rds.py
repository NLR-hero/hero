import hero as hq
import time

hq.session.get_session()


def test_rds_delete():
    """Create virutal queue"""
    project = hq.session.get_project()
    queue = hq.session.get_queue()
    hq.rds.delete_queue(project, queue)


def test_rds_put_item():
    project = hq.session.get_project()
    queue = hq.session.get_queue()

    data = {"name": "test-packet"}
    task = hq.task.Task(project, queue, queue, data)
    print(task.task_id)
    hq.rds.put_item(task)


def test_rds_get_item():
    project = hq.session.get_project()
    queue = hq.session.get_queue()

    data = {"name": "test-packet-2"}
    time.sleep(1)
    task = hq.task.Task(project, queue, queue, data)
    print(task.task_id)
    hq.rds.put_item(task)

    results = hq.rds.get_item(task.task_id, queue)
    print(results)


def test_rds_put_items():
    project = hq.session.get_project()
    queue = hq.session.get_queue()

    data = {"name": "test-packet"}
    tasks = []
    for i in range(5):
        tasks.append(hq.task.Task(project, queue, queue, data))

    hq.rds.put_items(tasks)
