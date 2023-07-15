import os
import boto3
import botocore.session

import logging

logging.getLogger("botocore").setLevel(logging.CRITICAL)


def get_session(aws_credentials=None, region_name='us-west-2'):
    """Returns a boto3 session"""
    if aws_credentials is not None:
    #     os.environ['AWS_ACCESS_KEY_ID'] = aws_credentials['AccessKeyId']
    #     os.environ['AWS_SECRET_ACCESS_KEY'] = aws_credentials['SecretAccessKey']
    #     os.environ['AWS_SESSION_TOKEN'] = aws_credentials['SessionToken']
        session = boto3.Session(
            region_name=region_name,
            aws_access_key_id=aws_credentials['AccessKeyId'],
            aws_secret_access_key=aws_credentials['SecretAccessKey'],
            aws_session_token=aws_credentials['SessionToken']
        )
        return session
    return None


def get_client_credentials(client_credentials=None):
    """Returns the client credentials tuple (client_id, client_secret) from the environment variables HERO_CLIENT_ID and HERO_CLIENT_SECRET"""
    if client_credentials is None:
        client_credentials = (os.environ["HERO_CLIENT_ID"], os.environ["HERO_CLIENT_SECRET"])
    return client_credentials


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


def get_queue_visibility_timeout():
    """Returns the queue visibility timeout from the environment variable HERO_QUEUE_VISIBILITY_TIMEOUT"""
    return os.environ.get("HERO_QUEUE_VISIBILITY_TIMEOUT", "60")
