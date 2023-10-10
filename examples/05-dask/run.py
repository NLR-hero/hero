import time
import os
import signal
import subprocess

WORKERS = 5

try:

    # clear the queue if you are using exit messages
    subprocess.Popen("hero_clear_queue", shell=True, env=os.environ).wait()


    # launch the controller
    controller = subprocess.Popen(['python', 'hero_controller.py'], 
                                  env=os.environ)

    # lanch the workers
    worker1 = subprocess.Popen("python hero_worker.py", 
                               shell=True, 
                               env=os.environ)
    worker2 = subprocess.Popen("python hero_worker.py", 
                               shell=True, 
                               env=os.environ)

    controller.wait()
    worker1.wait()
    worker2.wait()

except KeyboardInterrupt:
    print("KeyboardInterrupt")
    controller.send_signal(signal.SIGINT)
    worker1.send_signal(signal.SIGINT)
    worker2.send_signal(signal.SIGINT)
