import os
import time
import json
import hero as hq
from mpi4py import MPI

comm = MPI.COMM_WORLD
RANK = comm.Get_rank()
SIZE = comm.Get_size()

NUM_MESSAGES = 10

from test_barrier import (
    delete_dynamo,
    initial_setup,
    add_tasks,
    pull_messages,
    wait_for_rds,
    update_dynamo,
)


if __name__ == "__main__":
    hq.session.get_session()
    project = hq.session.get_project()
    queue = hq.session.get_queue()

    results = {}
    results["kind"] = "DynamoSqsRds"
    results["size"] = SIZE
    results["messages"] = NUM_MESSAGES

    tic = time.time()
    delete_dynamo(project, RANK)
    comm.Barrier()
    if RANK == 0:
        print(f"deleted dynamo in {round(time.time() - tic, 2)} seconds")

    # initial setup
    tic = time.time()
    initial_setup(project, queue)
    comm.Barrier()

    queue_url = hq.dynamo.get_queue_url(project, queue)
    # print(RANK, queue_url)

    # don't wait for barrier
    add_tasks(project, queue, queue_url, NUM_MESSAGES)
    messages = pull_messages(project, queue_url, NUM_MESSAGES)
    if len(messages) < NUM_MESSAGES:
        print(RANK, "not enough messages")

    update_dynamo(project, queue, messages)
    comm.Barrier()
    results["almost"] = round(time.time() - tic, 2)
    if RANK == 0:
        print(results)

    # wait for rds to update
    wait_for_rds(project, queue, "done")
    comm.Barrier()

    results["dsr"] = round(time.time() - tic, 2)
    if RANK == 0:
        print(results)
        with open(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_dsr"),
            "a",
        ) as outfile:
            outfile.write(json.dumps(results) + "\n")
