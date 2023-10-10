import os
import time
import random
import datetime
import pandas as pd

from dask.distributed import Client, LocalCluster
from dask.distributed import get_worker

random.seed(0)

def dask_function(task):
    sleep_time = float(task["sleep_time"])
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time.sleep(sleep_time)
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results = { "dask_resource_name": f"{get_worker().id}",
                     "task_id": task["name"],
                     "start_time": start_time, 
                     "end_time": end_time }
    return results

def execute_dask_task(tasks, dask_client):

    # Dask takes over
    futures = dask_client.map(dask_function, tasks)
    # wait for dask to finish
    results = dask_client.gather(futures)
    return results

def create_dask_task(index, lower=2, upper=4):
    return {
        "name": f"test_{index:02d}",
        "sleep_time": random.uniform(lower, upper)
    }


if __name__ == "__main__":

    # dask needs to be started in __main__
    cluster = LocalCluster(n_workers=10, processes=True, threads_per_worker=1, memory_limit='1GB')
    dask_client = Client(cluster)
    print(dask_client)

    tasks = [ create_dask_task(i) for i in range(100) ]
    results = execute_dask_task(tasks, dask_client)
    pd.DataFrame(results).to_csv("dask_results.csv", index=False)


   
