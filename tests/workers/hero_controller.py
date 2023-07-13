import hero as hr
import time

from hero.rds import get_jobs_status_count_by_queue_url
from hero.task import COMPLETE

hr.session.get_session()

if __name__ == "__main__":
    hero = hr.Hero("test-project", "queue-001")
    hero.clear_tasks()
    hr.rds.delete_queue(hero._project, hero._queue)

    # push items
    items = [
        {"name": "test_1"},
        {"name": "test_2"},
        {"name": "test_3"},
        {"name": "test_4"},
        {"name": "test_5"},
        {"name": "test_6"},
        {"name": "test_7"},
        {"name": "test_8"},
        {"name": "test_9"},
        {"name": "test_10"},
    ]

    task_ids = hero.put_tasks(items)
    print(task_ids)

    # wait for tasks to be available
    while True:
        done = get_jobs_status_count_by_queue_url(hero._project, hero._queue, COMPLETE)
        print(f"done: {done}")
        if done == 10:
            break
        time.sleep(1)

    # tasks are done
    print("tasks done")
