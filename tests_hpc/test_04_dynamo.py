import hero as hq

hq.session.get_session()


def test_dynamo_delete():
    project = hq.session.get_project()
    table = hq.dynamo.get_project_table(project)
    hq.dynamo.delete_table(table)


def test_dynamod_get_table():
    table = hq.dynamo.get_table("hero-dynamodb-project-queue-names")
    try:
        table = hq.dynamo.get_table("hero-gantry-test-does-not-exist")
    except Exception as e:
        assert True


def test_dynamo_put_item():
    project = hq.session.get_project()
    queue = hq.session.get_queue()
    queue_url = hq.dynamo.get_queue_url(project, queue)
    data = {"name": "test-packet"}
    task = hq.task.Task(project, queue, queue_url, data)
    project = hq.session.get_project()
    table = hq.dynamo.get_project_table(project)
    hq.dynamo.put_item(table, task)


def test_dynamo_get_item():
    project = hq.session.get_project()
    queue = hq.session.get_queue()
    queue_url = hq.dynamo.get_queue_url(project, queue)
    data = {"name": "test-packet"}
    task = hq.task.Task(project, queue, queue_url, data)
    project = hq.session.get_project()
    table = hq.dynamo.get_project_table(project)
    hq.dynamo.put_item(table, task)
    results = hq.dynamo.get_item(table, task.id, queue)
    print(results)


def test_dynamo_put_items():
    project = hq.session.get_project()
    queue = hq.session.get_queue()
    queue_url = hq.dynamo.get_queue_url(project, queue)
    data = {"name": "test-packet"}
    tasks = []
    for i in range(5):
        tasks.append(hq.task.Task(project, queue, queue_url, data))
    project = hq.session.get_project()
    table = hq.dynamo.get_project_table(project)
    hq.dynamo.put_items(table, tasks)


def test_dynamo_update_status():
    project = hq.session.get_project()
    queue = hq.session.get_queue()
    queue_url = hq.dynamo.get_queue_url(project, queue)

    data = {"name": "test-packet"}
    task = hq.task.Task(project, queue, queue_url, data)
    table = hq.dynamo.get_project_table(project)
    hq.dynamo.put_item(table, task)

    assert hq.dynamo.update_item_claimed(table, task.id, queue) == True
    assert hq.dynamo.update_item_claimed(table, task.id, queue) == False
    assert hq.dynamo.update_item_claimed(table, task.id, queue) == False
