import time
import os
import signal
import sys
import subprocess
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
                        prog='GantryWorker',
                        description='Lanches a gantry worker that pulls jobs from a queue.')
    
    parser.add_argument('--queue', type=str, help='name of queue') 
    parser.add_argument('--workers', type=int, help='number of workers to run')
    args = parser.parse_args()
    return args


if __name__ == "__main__":



    args = parse_args()

    WORKERS = args.workers
    QUEUE = args.queue
    print("Running HERO with ", WORKERS, " workers", " on queue ", QUEUE)

    try:

        # lanch the workers
        workers = subprocess.Popen(f"mpirun --oversubscribe -np {WORKERS} python hero_worker.py --queue  {QUEUE} --max_wait_time 1800", 
                                shell=True, 
                                env=os.environ)
        
        time.sleep(10)

        # launch the controller
        controller = subprocess.Popen(f"python hero_controller.py --queue {QUEUE} --num_tasks {WORKERS}", 
                                    shell=True, 
                                    env=os.environ)

    
        controller.wait()
        workers.wait()

    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        controller.send_signal(signal.SIGINT)
        workers.send_signal(signal.SIGINT)

