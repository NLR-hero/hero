import argparse

from hero import Hero
import random

def parse_args():
    parser = argparse.ArgumentParser(
                        prog='GantryWorker',
                        description='Lanches a gantry worker that pulls jobs from a queue.')
    
    parser.add_argument('--queue', type=str, help='name of queue') 
    parser.add_argument('--num_tasks', type=int, help='number of tasks to run')
    parser.add_argument('--time', type=str, help='s')
    args = parser.parse_args()
    return args

def create_task(iteration, index, command):
    return {
        "name": f"test_{iteration:03d}_{index:02d}",
        "command": command,
    }

def create_exit_task(iteration, index):
    return {
        "name": f"test_{iteration:03d}_{index:02d}",
        "command": "exit",
        "stream_db": False
    }

def send_exit_command(queue_name, n):
    hero = Hero(queue=queue_name)
    exit_tasks = [ create_exit_task(5, i) for i in range(n)]
    hero.put_tasks(exit_tasks)

def create_command():
    rand = random.randint(1, 3)
    return f"sleep {rand}"

def edges_hero_execute_commands(queue_name, iteration, commands):

    print("===================================================")
    print(f"iteration: {iteration}")
    print("===================================================")
        
    print(list(commands.values()))

    hero = Hero(queue=queue_name)
    hero.clear_tasks()

    items = [ create_task(iteration, i, c) for i, c in enumerate(commands.values())]
    res = hero.map(items)
    print( [r["status"] for r in res])
    print("===================================================")

if __name__ == "__main__":

    args = parse_args()

    hero = Hero(queue=args.queue)
    hero.clear_tasks()

    for iteration in range(5):
        commands = {str(i): create_command() for i in range(args.num_tasks*2)}
        edges_hero_execute_commands(args.queue, iteration, commands)

    print("Controller done")
    
    send_exit_command(args.queue, args.num_tasks)

   

