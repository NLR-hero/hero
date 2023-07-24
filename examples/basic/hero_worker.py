import hero as hr
import time

if __name__ == "__main__":
    hero = hr.Hero()
    while True:
        task = hero.pull_task(attempts=1)
        print('Task:', task)
        if task:
            hero.claim_task(task)
            hero.update_task(task, {"results": "complete"})
        else:
            print("No tasks")
        time.sleep(1)
