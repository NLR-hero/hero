import os
import time
import random
import logging

logging.getLogger("hero").setLevel(logging.INFO)

from hero import Hero

def execute_task(hero, task):
    sleep_time = float(task.inputs["sleep_time"])
    print(f"Sleeping for {sleep_time} seconds")
    time.sleep(sleep_time)
    hero.update_task(task, {"results": "complete"})


if __name__ == "__main__":

#------------------------------------------------------------------------------

    attempts = 0
    hero = Hero()

    while True:
        task = hero.pull_task(attempts=10)
        if task:
            if task.inputs.get('exit', False):
                exit()
            else:            
                execute_task(hero, task)
                attempts = 0
        else:
            attempts += 1
        hero.wait(1)

