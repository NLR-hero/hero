import os
import time
import json
import hero as hq
from mpi4py import MPI

comm = MPI.COMM_WORLD
RANK = comm.Get_rank()
SIZE = comm.Get_size()

NUM_MESSAGES = 50


def initial_setup(queue):
    if RANK == 0:
        hq.rds.delete_queue(queue)


def add_tasks(project, queue, queue_url):
    # add data to rds table
    tasks = []
    for i in range(NUM_MESSAGES):
        data = {"name": "test-packet", "rank": RANK * i}
        tasks.append(hq.task.Task(project, queue, queue_url, data))
    hq.rds.put_items(tasks)


def pull_messages(project, queue_url):
    messages = []
    while len(messages) < NUM_MESSAGES:
        task = hq.pull.pull_task_rds(project, queue_url)
        if task is not None:
            messages.append(task)
    return messages


def update_rds(project, queue, messages):
    # update rds
    for task in messages:
        hq.rds.update_item(task[0], hq.task.COMPLETE)


if __name__ == "__main__":
    hq.session.get_session()
    project = hq.session.get_project()
    queue = hq.session.get_queue()

    results = {}
    results["kind"] = "Rds"
    results["size"] = SIZE
    results["messages"] = NUM_MESSAGES

    queue_url = f"{project}-{queue}"

    # initial setup
    tic = time.time()
    initial_setup(queue_url)
    comm.Barrier()
    results["setup"] = round(time.time() - tic, 2)
    if RANK == 0:
        print(f"{RANK} init done", results["setup"])

    # all ranks add NUM_MESSAGES to dynamo
    tic = time.time()
    add_tasks(project, queue, queue_url)
    comm.Barrier()
    results["insert_tasks"] = round(time.time() - tic, 2)
    if RANK == 0:
        print(f"{RANK} insert tasks done", results["insert_tasks"])

    # all ranks pull NUM_MESSAGES from dynamo
    tic = time.time()
    messages = pull_messages(project, queue_url)
    comm.Barrier()
    results["pull_tasks"] = round(time.time() - tic, 2)
    if RANK == 0:
        print(f"{RANK} pull tasks done", results["pull_tasks"])

    # update rds
    tic = time.time()
    update_rds(project, queue, messages)
    comm.Barrier()
    results["update_tasks"] = round(time.time() - tic, 2)
    if RANK == 0:
        print(f"{RANK} update tasks done", results["update_tasks"])

    if RANK == 0:
        print(results)
        with open(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_rds"),
            "a",
        ) as outfile:
            outfile.write(json.dumps(results) + "\n")
