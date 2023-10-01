import time
import os
import signal
import subprocess

WORKERS = 2

try:

    os.environ['HERO_QUEUE'] = 'test23443'

    # clear the queue if you are using exit messages
    subprocess.Popen("hero_clear_queue", shell=True, env=os.environ).wait()


    # launch the controller
    controller = subprocess.Popen(['python', 'hero_controller.py'], 
                                  env=os.environ)

    # lanch the workers
    workers = subprocess.Popen(f"mpirun -np {WORKERS} python hero_worker.py", 
                               shell=True, 
                               env=os.environ)
    
    controller.wait()
    workers.wait()

except KeyboardInterrupt:
    print("KeyboardInterrupt")
    controller.send_signal(signal.SIGINT)
    workers.send_signal(signal.SIGINT)

