import os
import time
import random

from hero import Hero


def execute_task(hero, task):
    sleep_time = float(task.inputs["sleep_time"])
    print(f"{hero.resource_name} Sleeping for {sleep_time} seconds")
    time.sleep(sleep_time)
    hero.update_task(task, {"results": "complete"})


if __name__ == "__main__":

    QUEUE = os.environ["HERO_QUEUE"]

    # If after 45 attemps where there are no tasks, the worker will exit
    attempts = 0
    hero = Hero()

    while True:
        task = hero.pull_task(attempts=1)
        if task:

            # if the task accepts exit signals, then exit
            if task.inputs.get('exit', False):
                break
            
            if attempts > 15:
                break   

            execute_task(hero, task)
            attempts = 0

        else:
            attempts += 1
        
        hero.wait(attempts)

        
