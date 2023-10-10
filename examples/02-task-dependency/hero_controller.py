from hero import Hero
from hero.aws import rds
from hero.api.task import COMPLETE

import pandas as pd
import os
import time
import random
from functools import partial

random.seed(0)

def create_task(index, group, lower=2, upper=4):
    return {
        "name": f"test_{index:02d}",
        "group": group,
        "sleep_time": random.uniform(lower, upper)
    }

def create_exit_task(index):
    return {
        "name": f"test_{index:02d}",
        "exit": True,
        "stream_db": False
    }


if __name__ == "__main__":

    NUM_TASKS_1 = 25
    NUM_TASKS_2 = 50
    NUM_TASKS_3 = 25

    PROJECT = os.environ["HERO_PROJECT"]
    QUEUE = os.environ["HERO_QUEUE"]

    # clear the queue
    hero = Hero(queue=QUEUE)
    hero.clear_tasks()

    task_ids = []

    # Step one
    print("===================================================")
    print(f"Step one")
    print("===================================================")
    items = [ create_task(i, 1) for i in range(int(NUM_TASKS_1)) ]
    res = hero.map(items)
    task_ids.extend([r["id"] for r in res])

    # Step two
    print("===================================================")
    print(f"Step two")
    print("===================================================")
    items = [ create_task(i, 2) for i in range(int(NUM_TASKS_2)) ]
    res = hero.map(items)
    task_ids.extend([r["id"] for r in res])


    # Step three
    print("===================================================")
    print(f"Step three")
    print("===================================================")
    items = [ create_task(i, 3) for i in range(int(NUM_TASKS_3)) ]
    res = hero.map(items)
    task_ids.extend([r["id"] for r in res])

    # get results
    res = rds.get_items_detail(task_ids)
    df = pd.DataFrame(res)
    df.to_csv("results.csv", index=False)
    print("tasks done")
    
    # send the exit signal to workers
    items = [ create_exit_task(i) for i in range(int(10)) ]
    task_ids = hero.put_tasks(items)