from hero import Hero
from hero.aws import rds
from hero.api.task import COMPLETE

import pandas as pd
import os
import random
from functools import partial

random.seed(0)

def create_dask_task(index, lower=2, upper=4):
    return {
        "name": f"test_{index:02d}",
        "sleep_time": random.uniform(lower, upper)
    }

def create_exit_task(index):
    return {
        "name": f"test_{index:02d}",
        "exit": True,
        "stream_db": False
    }


if __name__ == "__main__":

    NUM_TASKS = 100  
    PROJECT = os.environ["HERO_PROJECT"]
    QUEUE = os.environ["HERO_QUEUE"]

    # clear the queue
    hero = Hero(queue=QUEUE)
    hero.clear_tasks()
    rds.delete_queue(PROJECT, QUEUE)

    hero_exit = Hero(queue=f"exit_{QUEUE}")
    hero_exit.clear_tasks()

    # push items
    items = [ create_dask_task(i) for i in range(int(NUM_TASKS)) ]
    task_ids = hero.put_tasks(items)

    results = hero.wait_for_tasks(task_ids)
    # tasks are done
    print("tasks done")


    # get results
    res = rds.get_items_detail(task_ids)
    df = pd.DataFrame(res)
    df.to_csv("results.csv", index=False)

    # send the exit signal to workers
    items = [ create_exit_task(i) for i in range(int(2)) ]
    task_ids = hero.put_tasks(items)
