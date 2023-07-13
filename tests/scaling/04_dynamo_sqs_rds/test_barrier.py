"""
Test the DynamoDB, SQS, and RDS scaling.
Author: Monte Lunacek

Note: We are using MPI only to launch and run the workers.
"""
import os
import time
import json
import hero as hq
from mpi4py import MPI

comm = MPI.COMM_WORLD
RANK = comm.Get_rank()
SIZE = comm.Get_size()

NUM_MESSAGES = 50


def delete_dynamo(project, RANK=0):
    if RANK < 10:
        table = hq.dynamo.get_project_table(project)
        hq.dynamo.delete_table(table, 10, RANK)


def initial_setup(project, queue):
    if RANK == 0:
        # create queue
        queue_url = hq.queue.create_queue(project, queue)
        hq.dynamo.update_queue_url(project, queue, queue_url)
        hq.rds.delete_queue(project, queue)


def add_tasks(project, queue, queue_url, num_messages=NUM_MESSAGES):
    # add data to dynamo table
    tasks = []
    for i in range(NUM_MESSAGES):
        data = {"name": "test-packet", "rank": RANK * i}
        tasks.append(hq.task.Task(project, queue, queue_url, data))
    table = hq.dynamo.get_project_table(project)
    hq.dynamo.put_items(table, tasks)


def pull_messages(project, queue_url, num_messages=NUM_MESSAGES):
    messages = []
    while len(messages) < num_messages:
        task = hq.pull.pull_task_sqs_dynamo(project, queue_url)
        if task is not None:
            messages.append(task)
    return messages


def wait_for_rds(project, queue, status):
    if RANK == 0:
        res = hq.rds.get_jobs_status_count_by_queue_url(project, queue, status=status)
        while res < NUM_MESSAGES * SIZE:
            res = hq.rds.get_jobs_status_count_by_queue_url(
                project, queue, status=status
            )
            time.sleep(1)


def update_dynamo(project, queue, messages):
    for message in messages:
        job_id = message["id"]
        table = hq.dynamo.get_project_table(project)
        hq.dynamo.update_item_results(table, job_id, queue, results={})


if __name__ == "__main__":
    hq.session.get_session()
    project = hq.session.get_project()
    queue = hq.session.get_queue()

    results = {}
    results["kind"] = "DynamoSqsRds"
    results["size"] = SIZE
    results["messages"] = NUM_MESSAGES

    # initial setup
    tic = time.time()
    initial_setup(project, queue)
    comm.Barrier()
    results["setup"] = round(time.time() - tic, 2)
    if RANK == 0:
        print(f"{RANK} init done", results["setup"])

    # all ranks add NUM_MESSAGES to dynamo
    tic = time.time()
    queue_url = hq.dynamo.get_queue_url(project, queue)
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

    # wait for rds to update
    tic = time.time()
    wait_for_rds(queue_url, "claimed")
    comm.Barrier()
    results["rds_claimed"] = round(time.time() - tic, 2)
    if RANK == 0:
        print(f"{RANK} RDS claimed done", results["rds_claimed"])

    # update dynamo
    tic = time.time()
    update_dynamo(project, queue, messages)
    comm.Barrier()
    results["update_tasks"] = round(time.time() - tic, 2)
    if RANK == 0:
        print(f"{RANK} update tasks done", results["update_tasks"])

    # wait for rds to update
    tic = time.time()
    wait_for_rds(queue_url, "done")
    comm.Barrier()
    results["rds_done"] = round(time.time() - tic, 2)
    if RANK == 0:
        print(f"{RANK} RDS done", results["rds_done"])

        print(results)
        # q: How do I compute the file location of this file in code? __file__
        # a:
        with open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "results_dsr_barrier"
            ),
            "a",
        ) as outfile:
            outfile.write(json.dumps(results) + "\n")

        table = hq.dynamo.get_project_table(project)
        hq.dynamo.delete_table(table)
