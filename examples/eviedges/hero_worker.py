import sys
import os
import pandas as pd
import datetime
import pytz
import numpy as np
import time
import subprocess

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import logging

logging.basicConfig(level=os.environ.get("LOGLEVEL", logging.INFO))
logging.getLogger("urllib3").setLevel(logging.WARNING)

log = logging.getLogger("worker")

import argparse

from hero import Hero


# function to print current time
def now_time():
    return datetime.datetime.now().strftime("%m-%d %H:%M:%S")


def parse_args():
    parser = argparse.ArgumentParser(
        prog="GantryWorker",
        description="Lanches a gantry worker that pulls jobs from a queue.",
    )

    parser.add_argument("--queue", type=str, help="name of queue")
    parser.add_argument("--max_run_time", type=int, help="max run time of any job")
    parser.add_argument(
        "--max_wait_time", type=int, help="max time to wait without any jobs"
    )

    args = parser.parse_args()
    return args


def execute_task(hero, task):
    command = task.inputs["command"]
    log.info(f"Hero worker {hero._worker_id} executing task {task.inputs['name']} {hero.count} from queue {hero._queue_url[-10:]}")

    # print("command ---> ", command)

    if command == "exit":
        log.info(f'Command was "exit". Exiting. {now_time()}.')
        exit()

    # log.info(command)
    try:
        subprocess.run(command, shell=True, capture_output=False, check=True)
    except subprocess.CalledProcessError as s_error:
        print(s_error.args[1])
        print(s_error.stderr)
    except:
        print("Runs could not be executed.")

    hero.update_task(task, {"results": "complete"})
    # log.info(f"Task {task.task_id} updated to complete. {now_time()}.")


def worker(queue="test", max_wait_time=120):
    queue_name = queue

    # command line args
    hero = Hero(queue=queue_name)
    # g = Gantry(queue_name=queue_name)

    # try to fetch a job
    tic = time.time()
    total_wait = time.time() - tic
    attempts = 0
    while True and total_wait < max_wait_time:

        # get the inputs
        task = hero.pull_task(attempts=10)
        if task is not None:
            execute_task(hero, task)
            attempts = 0
            tic = time.time()
        else:
            attempts += 1
            total_wait = time.time() - tic

        log.info(f"Worker waiting for {round(min(attempts, 15))} seconds on {hero._queue_url[-10:]}, total wait time = {round(total_wait/60, 2)} minutes.")
        hero.wait(min(attempts, 15))

 
    log.info(f"Worker waited too long and logged off: {round(total_wait)} seconds. {now_time()}.")


if __name__ == "__main__":
    args = parse_args()
    worker(args.queue, args.max_wait_time)
