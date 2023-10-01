from hero import Hero
from hero.aws import rds
from hero.api.task import COMPLETE

import pandas as pd
import os
import random
from functools import partial

random.seed(0)
import logging

logging.getLogger("hero").setLevel(logging.DEBUG)

def create_task(index, lower=2, upper=4):
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

    NUM_WORKERS = 2
    NUM_TASKS = 10

    print(os.environ['HERO_QUEUE'])
 
    # clear the queue
    hero = Hero()
    hero.clear_tasks()

    # push items
    items = [ create_task(i) for i in range(int(NUM_TASKS)) ]
    task_ids = hero.put_tasks(items)
    print(task_ids)

    results = hero.wait_for_tasks(task_ids)
    df = pd.DataFrame(results)
    df.to_csv("results.csv", index=False)
    print("tasks done")
    
    # send the exit signal to workers
    items = [ create_exit_task(i) for i in range(int(NUM_WORKERS)) ]
    task_ids = hero.put_tasks(items)

    
    