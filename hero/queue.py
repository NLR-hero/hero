"""
Queues are a main component of the Task Engine. This modules provides direct access to SQS via boto3.

Key Features:

* Queues are ephemeral. They can be created and destroyed at any time.
* The SQS API and boto3 are very fast with high scalability expected.
* Queues act as the bridge between services that presist task state and results.
"""
import os
import boto3
import botocore
import logging
import time
import json
import uuid

from .session import get_project, get_queue, get_queue_visibility_timeout

logging.basicConfig(level=os.environ.get("LOGLEVEL", "ERROR"))
log = logging.getLogger("hero:queue")


def receive_messages(session, queue_url, num=1):
    """
    Call this from a worker to get a task.

    Returns some number of messages from a specific `queue_url`.
    """
    client = session.client("sqs")
    message_packet = client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=num)
    return message_packet


def delete_message(session, queue_url, message):
    """
    Call this from a worker after a task is clamied by that worker.

    Deletes a message from a specific `queue_url`.
    """
    client = session.client("sqs")
    response = client.delete_message(
        QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"]
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def list_queues(session, project=None, queue=None):
    '''
    Each time a queue is created a UUID is attached to the end of the full queue name. This allows clients to create multiple unique queues with a consistent and predictable prefix.

    Yields queue urls for all queues with the hero-project-queue prefix.
    '''
    project = get_project(project)
    queue = get_queue(queue)
    queue_prefix = f"hero-{project}-{queue}-"
    client = session.client("sqs")
    response = client.list_queues(QueueNamePrefix=queue_prefix)
    for queue_url in response.get("QueueUrls", []):
        yield queue_url


def delete_other_queues(session, queue_url, project=None, queue=None):
    """
    Workers can optionally remove all previously created queues to start a fresh campaign. This will remove all other queues with a hero-project prefix.

    For example, say in campaign A you created a queue "hero-project-queue000". This campaign completed but the queue was not cleaned up. Then you want to start a new campaign with the same input parameters, but you don't want to reuse an old queue. Calling this function will find all of the queues that start with "hero-project-queue000" and delete them as long as they are not the current queue. Remember, each time a queue is crated a uuid is attached to the end of the queue name.
    """
    queue_list = list(list_queues(session, project, queue))
    for temp_queue_url in queue_list:
        if temp_queue_url != queue_url:
            delete_queue(session, temp_queue_url)


def delete_queue(session, queue_url):
    """
    Delete a queue
    """
    try:
        log.info(f"deleting {queue_url}")
        client = session.client("sqs")
        client.delete_queue(QueueUrl=queue_url)
    except botocore.exceptions.ClientError as err:
        log.error(str(err))


def create_queue(session, project=None, queue=None):
    """
    Creates a new unique queue.
    """
    project = get_project(project)
    queue = get_queue(queue)
    visibility_timeout = get_queue_visibility_timeout()

    queue_name = f"hero-{project}-{queue}-{str(uuid.uuid4())}"

    client = session.client("sqs")
    #NOTE: this is a pretty big side effect, the function to create queues should only be responsible for creating queues. There should be another function that connects these dots together.
    # delete_other_queues(session, queue_name, project, queue)
    client.create_queue(
        QueueName=queue_name,
        Attributes={"VisibilityTimeout": visibility_timeout},
    )

    response = client.get_queue_url(QueueName=queue_name)
    while response.get("QueueUrl") is None:
        # Wait for the queue to get created.
        #TODO: wrap this in the retry function and eventually error out if we are waiting too long.
        time.sleep(1)
        response = client.get_queue_url(QueueName=queue_name)
    queue_url = response.get("QueueUrl")
    log.info(f"created queue: {queue_url}")
    return queue_url
