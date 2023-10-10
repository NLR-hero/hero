import os
import time
import random
import datetime

from hero import Hero

from dask.distributed import Client, LocalCluster
from dask.distributed import get_worker

def dask_function(task):
    sleep_time = float(task.inputs["sleep_time"])
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time.sleep(sleep_time)
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    task.results = { "results": "complete", 
                     "worker": f"{get_worker().id}",
                     "group": f"{task.claimed_worker_id}",
                     "start_time": start_time, 
                     "end_time": end_time }
    return task

def execute_dask_task(hero, tasks, dask_client):

    # Dask takes over
    futures = dask_client.map(dask_function, tasks)
    # wait for dask to finish
    results = dask_client.gather(futures)
    for task in results:
        hero.update_task(task, task.results)



if __name__ == "__main__":

    QUEUE = os.environ["HERO_QUEUE"]

    # If after 45 attemps where there are no tasks, the worker will exit
    attempts = 0
    hero = Hero(queue=QUEUE)
    hero_exit = Hero(queue=f"exit_{QUEUE}")

    # dask needs to be started in __main__
    cluster = LocalCluster(n_workers=5, processes=True, threads_per_worker=1, memory_limit='1GB')
    dask_client = Client(cluster)

    while True:
        tasks = hero.pull_tasks(attempts=1, num_tasks=10)
        print('Task:', tasks)
        if tasks:
            attempts=1
            execute_dask_task(hero, tasks, dask_client)
        else:
            exit_task = hero_exit.pull_task(attempts=1)
            if exit_task and exit_task.inputs.get('exit', False):
                dask_client.shutdown()
                exit()
            attempts += 1
        hero.wait(1)

        if attempts > 45:
            break
