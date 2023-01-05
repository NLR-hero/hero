import sys
import argparse
import json

from .gantry import Gantry


def get_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        help='list, remove, or create', dest='command')
    list_parser = subparsers.add_parser("list")
    remove_parser = subparsers.add_parser("purge")
    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("job")

    args = parser.parse_args(sys.argv[1:])
    return args


def main():

    args = get_args()
    print(args)

    g = Gantry()

    if args.command == "list":
        print(f"Listing all jobs in {g.resource_name}:")
        for j in g.jobs():
            print(j)

    elif args.command == "purge":
        print(f"Removing all jobs from {g.resource_name}:")

    elif args.command == "create":
        job = json.loads(args.job)
        print(f"Adding job to {g.resource_name}:")
        g.submit_job(job)
