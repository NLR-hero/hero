
import pandas as pd
import time
import os
import random
from functools import partial
from mpi4py import MPI

random.seed(0)

from hero import Hero
from hero.aws import rds
from hero.api.task import COMPLETE


comm = MPI.COMM_WORLD
RANK = comm.Get_rank()
SIZE = comm.Get_size()

NUM_MESSAGES_PER_WORKER = 10



def create_task(index, lower=0, upper=0.1):
    return {
        "name": f"test_{index:02d}",
        "sleep_time": random.uniform(lower, upper)
    }

def execute_task(hero, task):
    sleep_time = float(task.inputs["sleep_time"])
    # print(f"Sleeping for {sleep_time} seconds")
    time.sleep(sleep_time)
    hero.update_task(task, {"results": "complete"})


if __name__ == "__main__":

    results = {}
    results['size'] = SIZE
    tic = time.time()
    hero = Hero()

    # push tasks
    if RANK == 0:
        # This is the old queue with tasks
        total_tasks = int(NUM_MESSAGES_PER_WORKER*SIZE)
        print(f"creating {total_tasks} tasks")
        hero.clear_tasks()
        items = [ create_task(i) for i in range(total_tasks) ]
        task_ids = hero.put_tasks(items)
        results['push_tasks'] = time.time() - tic

    comm.Barrier()

    # Each worker pulls exactly NUM_MESSAGES_PER_WORKER tasks.  This is
    # only for testing.  In practice, workers should pull tasks until
    # there are no more tasks to pull.
    tic = time.time()
    while hero.count < NUM_MESSAGES_PER_WORKER:
        
        task = hero.pull_task(attempts=1)
        while not task:
            time.sleep(1)
            task = hero.pull_task(attempts=1)
        print(f"Hero worker {hero._worker_id} executing task {task.inputs['name']} {hero.count} of {NUM_MESSAGES_PER_WORKER} from queue {hero._queue_url[-10:]}")
        execute_task(hero, task)

    comm.Barrier()
    results['pull_tasks'] = time.time() - tic

    if RANK == 0:
        print("workers done waiting for results")
        tic = time.time()
        res = hero.wait_for_tasks(task_ids)
        results['verify'] = time.time() - tic
        print("number of tasks", len(res))
        print("tasks done")
        print(results)

