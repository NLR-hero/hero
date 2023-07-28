from hero import Hero

from hero.api.task import COMPLETE

if __name__ == "__main__":
    hero = Hero()
    hero.clear_tasks()

    # push items
    items = [
        {"name": "test_1"},
        {"name": "test_2"},
        {"name": "test_3"},
        {"name": "test_4"},
        {"name": "test_5"},
    ]

    task_ids = hero.put_tasks(items)
    print(task_ids)

    # wait for tasks to be available
    while True:
        done = hero.get_task_status_count(COMPLETE)
        print(f"done: {done}")
        if done == 5:
            break
        hero.wait(1)

    # tasks are done
    print("tasks done")
