import hero as hr
import time

hr.session.get_session()

if __name__ == "__main__":
    hero = hr.Hero("test-project", "queue-001")
    while True:
        task = hero.pull_task(attempts=1)
        print(task)
        if task:
            hero.update_task(task, {"results": "complete"})
        else:
            print("No tasks")
        time.sleep(1)
