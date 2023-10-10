from hero import Hero
from hero.aws import rds
from hero.api.task import COMPLETE

import pandas as pd
import os
import time
import random
from functools import partial

random.seed(0)

def create_task(index, iteration, lower=2, upper=4):
    return {
        "name": f"test_{index:02d}",
        "group": iteration,
        "sleep_time": random.uniform(lower, upper)
    }

def create_exit_task(index):
    return {
        "name": f"test_{index:02d}",
        "exit": True,
        "stream_db": False
    }

if __name__ == "__main__":

    NUM_TASKS_PER_ITERATION = 20
    NUM_ITERATIONS = 5
    PROJECT = os.environ["HERO_PROJECT"]
    QUEUE = os.environ["HERO_QUEUE"]

    # clear the queue
    hero = Hero(queue=QUEUE)
    hero.clear_tasks()
   
    task_ids = []
    # start the optimzation
    for iteration in range(NUM_ITERATIONS):
        
        print("===================================================")
        print(f"iteration: {iteration}")
        print("===================================================")
        
        # push cadidate solutions
        items = [ create_task(i, iteration) for i in range(int(NUM_TASKS_PER_ITERATION)) ]
        res = hero.map(items)
        task_ids.extend([r["id"] for r in res])

        print( [r["status"] for r in res])
        print("===================================================")


    # tasks are done
    print("tasks done")
    
    # get results
    res = rds.get_items_detail(task_ids)
    df = pd.DataFrame(res)
    df.to_csv("results.csv", index=False)

    # send the exit signal to workers
    items = [ create_exit_task(i) for i in range(int(10)) ]
    task_ids = hero.put_tasks(items)