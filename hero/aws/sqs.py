import botocore
from botocore.exceptions import ClientError
import logging
from typing import Dict
# Types
from boto3.session import Session

log = logging.getLogger('hero:aws:sqs')

def create_queue(session: Session, queue_name: str, visibility_timeout: str='60') -> Dict[str, any]:
    '''
    Creates a new SQS Queue.
    '''
    log.debug('create_queue')
    client = session.client("sqs")
    result = client.create_queue(
        QueueName=queue_name,
        Attributes={"VisibilityTimeout": visibility_timeout},
    )
    return result

def receive_messages(session: Session, queue_url: str, max_number_of_messages: int=1):
    """
    Call this from a worker to get a task.

    Returns some number of messages from a specific `queue_url`.
    """
    log.debug('receive_messages')
    client = session.client("sqs")
    message_packet = client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=max_number_of_messages)

    if "Messages" in message_packet.keys():
        return message_packet["Messages"]

    return []


def delete_message(session, queue_url, message):
    """
    Call this from a worker after a task is clamied by that worker.

    Deletes a message from a specific `queue_url`.
    """
    log.debug('delete_message')
    client = session.client("sqs")
    response = client.delete_message(
        QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"]
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def list_queues(session, queue_prefix):
    log.debug('list_queues')
    client = session.client("sqs")
    response = client.list_queues(QueueNamePrefix=queue_prefix)
    for queue_url in response.get("QueueUrls", []):
        yield queue_url


def delete_queue(session: Session, queue_url: str) -> None:
    """
    Delete a queue
    """
    log.debug('delete_queue')
    try:
        log.info(f"deleting {queue_url}")
        client = session.client("sqs")
        client.delete_queue(QueueUrl=queue_url)
        return True
    except botocore.exceptions.ClientError as err:
        log.error(str(err))
        return False


def get_queue_url(session: Session, queue_name: str) -> str:
    '''
    Returns the queue url for a given `queue_name`.

    Attributes:
        session (str): A preconfigured boto3 session.
        queue_name (str): An error code representing the type of error.

    Returns:
        str: The queue url for the given queue name if it exists, None otherwise.
    '''
    log.debug('get_queue_url')
    try:
        client = session.client("sqs")
        response = client.get_queue_url(QueueName=queue_name)
        return response.get('QueueUrl')
    except ClientError as e:
            if e.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
                return None