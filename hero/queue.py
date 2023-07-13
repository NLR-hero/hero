import os
import boto3
import botocore
import logging
import time
import json
import uuid

from .session import get_project, get_queue, get_queue_visibility_timeout

logging.basicConfig(level=os.environ.get("LOGLEVEL", "ERROR"))
log = logging.getLogger("gantry:sqs")


def receive_messages(queue_url, num=1):
    client = boto3.client("sqs")
    message_packet = client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=num)
    return message_packet


def delete_message(queue_url, message):
    client = boto3.client("sqs")
    response = client.delete_message(
        QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"]
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def list_queues(project=None, queue=None):
    project = get_project(project)
    queue = get_queue(queue)
    queue_prefix = f"hero-{project}-{queue}-"
    client = boto3.client("sqs")
    response = client.list_queues(QueueNamePrefix=queue_prefix)
    for queue_url in response.get("QueueUrls", []):
        yield queue_url


def delete_other_queues(queue_url, project=None, queue=None):
    queue_list = list(list_queues(project, queue))
    for temp_queue_url in queue_list:
        temp_queue_name = temp_queue_url.split("/")[-1]
        if temp_queue_name != queue_url:
            try:
                log.info(f"deleting {temp_queue_url}")
                client = boto3.client("sqs")
                client.delete_queue(QueueUrl=temp_queue_url)
            except botocore.exceptions.ClientError as err:
                log.error(str(err))


def create_queue(project=None, queue=None):
    """Creates virtual queue"""
    project = get_project(project)
    queue = get_queue(queue)
    visibility_timeout = get_queue_visibility_timeout()

    queue_name = f"hero-{project}-{queue}-{str(uuid.uuid4())}"

    client = boto3.client("sqs")
    delete_other_queues(queue_name, project, queue)
    client.create_queue(
        QueueName=queue_name,
        Attributes={"VisibilityTimeout": visibility_timeout},
    )

    response = client.get_queue_url(QueueName=queue_name)
    while response.get("QueueUrl") is None:
        time.sleep(1)
        response = client.get_queue_url(QueueName=queue_name)
    queue_url = response.get("QueueUrl")
    log.info(f"created queue: {queue_url}")
    return queue_url
