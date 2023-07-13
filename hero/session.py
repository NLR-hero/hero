import os
import boto3
import botocore.session

import logging

logging.getLogger("botocore").setLevel(logging.CRITICAL)


def get_session():
    """Returns a boto3 session"""
    botocore.session.get_session()


def get_project(project=None):
    """Returns the project name from the environment variable HERO_PROJECT"""
    if project is None:
        project = os.environ["HERO_PROJECT"]
    return project


def get_queue(queue=None):
    """Returns the queue name from the environment variable HERO_QUEUE"""
    if queue is None:
        queue = os.environ["HERO_QUEUE"]
    return queue


def get_queue_visibility_timeout(queue=None):
    """Returns the queue visibility timeout from the environment variable HERO_QUEUE_VISIBILITY_TIMEOUT"""
    return os.environ.get("HERO_QUEUE_VISIBILITY_TIMEOUT", "60")
