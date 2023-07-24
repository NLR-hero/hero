#TODO: Use https://github.com/theskumar/python-dotenv
#TODO: setup so any module can import config and get the json for the config.

import os
import logging

log = logging.getLogger('hero:config')

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

def export_session_to_env(aws_credentials):
    """
    Set the three AWS credentials environment variables from an assumed role.
    """
    os.environ['AWS_ACCESS_KEY_ID'] = aws_credentials['AccessKeyId']
    os.environ['AWS_SECRET_ACCESS_KEY'] = aws_credentials['SecretAccessKey']
    os.environ['AWS_SESSION_TOKEN'] = aws_credentials['SessionToken']

def get_aws_credentials(aws_credentials=None):
    """
    Get the three AWS credentials from environment varabiles.
    """
    if aws_credentials is None:
        aws_credentials = {}

        access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        session_token = os.environ.get('AWS_SESSION_TOKEN')

        if access_key_id is None or secret_access_key is None or session_token is None:
            # incomplete credentials
            return None

        aws_credentials['AccessKeyId'] = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_credentials['SecretAccessKey'] = os.environ.get('AWS_SECRET_ACCESS_KEY')
        aws_credentials['SessionToken'] = os.environ.get('AWS_SESSION_TOKEN')
        return aws_credentials

    return aws_credentials # Pass through
