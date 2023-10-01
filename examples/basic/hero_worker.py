import os
import time
import random

from hero import Hero

def execute_task(hero, task):
    sleep_time = float(task.inputs["sleep_time"])
    print(f"Sleeping for {sleep_time} seconds")
    time.sleep(sleep_time)
    hero.update_task(task, {"results": "complete"})


if __name__ == "__main__":

    # If after 45 attemps where there are no tasks, the worker will exit
    attempts = 0
    hero = Hero()

    while True:
        print("--------------- Waiting for tasks ---------------")
        task = hero.pull_task(attempts=10)
        if task:
            if task.inputs.get('exit', False):
                print("hero._queue_count", hero._queue_count)
                exit()
                # if hero._queue_count > 5:
                #     exit()
            else:            
                execute_task(hero, task)
                attempts = 0
        else:
            attempts += 1
        hero.wait(1)

