# What is HERO?

HERO are Hybrid Environment Resources and Operations which consists of a set of systems, tools, infrastructure code, and micro frontend web applications. With HERO you can run your code autonoumously and asynchronously in any compute environment with an internet connection, monitor the progress of a workflow, and share your work with collaborators.

This Python client lets you tie your code into the HERO Task Engine which is a scalable system that decouples task descriptions from task execution. With the Task Engine you can easily manage complex workflows by tracking the state of tasks and dynamically defining new tasks.

# Getting Started

Install the HERO Python client:

`pip install git+https://github.nrel.gov/Hero/hero.git`

Next, setup a simple script:

```python
from hero import Hero

hr = Hero()
```

Next, set these required environment variables:

```shell
export HERO_PROJECT="<PROJECT>"
export HERO_QUEUE="<QUEUE>"
export HERO_CLIENT_ID="<CLIENT_ID>"
export HERO_CLIENT_SECRET="<CLIENT_SECRET>"
```

**`HERO_PROJECT`** is the name of your project's workload. This is a fixed value and is tied to your app client.

**`HERO_QUEUE`** is the name you give a queue for the current run of your workload. These queues are ephemeral and may be created and destroyed at anytime. When you create a queue it is given a unique identifier prefixed with this name.

**`HERO_CLIENT_ID`** and **`HERO_CLIENT_SECRET`** are your credentials to work with the set of HERO systems including the Task Engine.

# Examples 

## Basic Setup

### Basic Worker

```python
from hero import Hero

if __name__ == "__main__":
    hero = Hero()
    while True:
        task = hero.pull_task(attempts=1)
        print('Task:', task)
        if task:
            hero.claim_task(task)
            hero.update_task(task, {"results": "complete"})
        else:
            print("No tasks")
        hero.wait(1)
```

### Basic Controller

```python
from hero import Hero
from hero.api.task import COMPLETE

if __name__ == "__main__":
    hero = Hero()
    hero.clear_tasks()

    # push items
    items = [
        {"name": "test_1"},
        {"name": "test_2"},
        {"name": "test_3"},
        {"name": "test_4"},
        {"name": "test_5"},
    ]

    task_ids = hero.put_tasks(items)
    print(task_ids)

    # wait for tasks to be available
    while True:
        done = hero.get_task_status_count(COMPLETE)
        print(f"done: {done}")
        if done == 5:
            break
        hero.wait(1)

    # tasks are done
    print("tasks done")

```

## Optimization

```python
#TODO
```
