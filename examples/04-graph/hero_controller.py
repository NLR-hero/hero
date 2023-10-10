import pandas as pd
import os
import networkx as nx
from collections import Counter
import random

from hero import Hero
from hero.aws import rds
from hero.api.task import COMPLETE

MAX_WORKERS=10

def create_task(index, lower=2, upper=4):
    return {
        "name": f"{index}", #index is a string this time
        "sleep_time": random.uniform(lower, upper)
    }

def create_exit_task(index):
    return {
        "name": f"test_{index:02d}",
        "exit": True,
        "stream_db": False
    }

def all_dependencies_ready(g, name):
    res = []
    for node in g.predecessors(name):
        res.append(g.nodes[node]['data'].get("status")=="done")
    return all(res)

def status_is_none(g, name):
    return g.nodes[name]['data'].get("status") is None

def next_jobs(g):
    return [ n for n in nx.topological_sort(g) if all_dependencies_ready(g, n) and status_is_none(g, n) ]


def create_complex_workflow():
    g = nx.DiGraph()
    rows = pd.read_csv("example_graph.csv").to_dict(orient="records")
    node_names = set()
    for row in rows:
        node_names.add(row['source'])
        node_names.add(row['destination'])

    for name in node_names:
        g.add_node(name, data={"status": None})

    for row in rows:
        g.add_edge(row['source'], row['destination'])
    return g



if __name__ == "__main__":

    PROJECT = os.environ["HERO_PROJECT"]
    QUEUE = os.environ["HERO_QUEUE"]

    hero = Hero()
    hero.clear_tasks()
    rds.delete_queue(PROJECT, QUEUE)

    # some kind of complex workflow capability (torc, PIPES, etc.)
    g = create_complex_workflow()
    print(f"There are {len(g.nodes())} nodes in the graph")

    all_task_ids = []
    while True:

        # what jobs are ready to run?
        names = next_jobs(g)
        if len(names)>0:  
            print("names", names)
            tasks = [ create_task(name) for name in names ]
            task_ids = hero.put_tasks(tasks)
            for name in names:
                g.nodes[name]['data']['status'] = "submitted"
            all_task_ids.extend(task_ids)
            all_task_ids = list(set(all_task_ids))
        else:
            print("no tasks ready to run")

        print("len(all_task_ids)", len(all_task_ids))
        # ask for updates
        res = rds.get_items_detail(all_task_ids)
        df = pd.DataFrame(res)
        for row in df.to_dict(orient="records"):  
            task_name = row['job_description']['name']
            if row['status'] == COMPLETE:
                g.nodes[task_name]['data']['status'] = "done"
            
        hero.wait(1)
        # check if we are done
        status = Counter([ x[1]['data'].get("status") for x in g.nodes(data=True) ])
        print(status)
        if status.get("done", 0) == len(g.nodes):
            break
    

    # tasks are done
    print("tasks done")

    # send the exit signal to workers
    items = [ create_exit_task(i) for i in range(int(10)) ]
    task_ids = hero.put_tasks(items)

    # get results.. simplify this in the future
    res = rds.get_items_detail(all_task_ids)
    df = pd.DataFrame(res)
    df.to_csv("results.csv", index=False)