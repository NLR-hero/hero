from hero import Hero

if __name__ == "__main__":
    hero = Hero(queue='hf')
    while True:
        task = hero.pull_task(attempts=1)
        print('Task:', task.data['inputs'])
        if task:
            hero.claim_task(task)
            hero.update_task(task, {"results": "complete"})
        else:
            print("No tasks")
        hero.wait(1)
