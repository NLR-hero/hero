from hero import Hero
from hero.api.task import COMPLETE
from hero.api.queue import create_queue, list_queues

if __name__ == "__main__":
    # create_queue(queue='lf')
    # create_queue(queue='hf')
    # list_queues()

    hero_lf = Hero(queue='lf')
    hero_hf = Hero(queue='hf')
    hero_lf.clear_tasks()
    hero_hf.clear_tasks()

    # push items                                                                                                  
    items_lf = [
        {"name": "test_lf_1", "args": [1, 2, 3]},
        {"name": "test_lf_2", "args": [1, 2, 3]},
        {"name": "test_lf_3", "args": [1, 2, 3]},
    ]
    items_hf = [
        {"name": "test_hf_a", "args": [1, 2, 3]},
        {"name": "test_hf_b", "args": [1, 2, 3]},
        {"name": "test_hf_c", "args": [1, 2, 3]},
    ]

    task_ids_lf = hero_lf.put_tasks(items_lf)
    print(task_ids_lf)
    task_ids_hf = hero_hf.put_tasks(items_hf)
    print(task_ids_hf)

    # wait for tasks to be available                                                                              
    while True:
        count_finished = hero_lf.get_task_status_count(COMPLETE)
        print(f"Number of completed tasks: {count_finished}")
        if count_finished == len(items_lf):
            print(f"All {count_finished} low fidelity tasks complete.")
            break
        hero_lf.wait(1)
    while True:
        count_finished = hero_hf.get_task_status_count(COMPLETE)
        print(f"Number of completed tasks: {count_finished}")
        if count_finished == len(items_hf):
            print(f"All {count_finished} high fidelity tasks complete.")
            break
        hero_hf.wait(1)

    print("All tasks are done.")