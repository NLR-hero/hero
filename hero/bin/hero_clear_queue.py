import os
import argparse

from hero import Hero

def parse_args():
    parser = argparse.ArgumentParser(
                        prog='GantryWorker',
                        description='Lanches a gantry worker that pulls jobs from a queue.')
    
    parser.add_argument('--queue', type=str, help='name of queue', default=os.environ["HERO_QUEUE"]) 
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    hero = Hero(queue=args.queue)
    hero.clear_tasks()


if __name__ == "__main__":

    main()

