import hero as hr


def _test_hero():
    hero = hr.Hero()
    item = {"name": "test"}
    task_id = hero.put_task(item)
    print(task_id)

    items = [{"name": "test_1"}, {"name": "test_2"}, {"name": "test_3"}]
    task_ids = hero.put_tasks(items)
    print(task_ids)

    tasks = []
    attempts = 0
    while len(tasks) < 3 and attempts < 9:
        print(len(tasks), attempts)
        task = hero.pull_task()
        attempts += 1
        if task:
            tasks.append(task)

    for task in tasks:
        task2 = hero.update_task(task, {"results": "complete"})
        print(task2)

    print(hero._queue_url)
    hero.clear_tasks()
    print(hero._queue_url)

    # pull jobs
    task = hero.pull_task()
    print("task", task)
    assert task is None
