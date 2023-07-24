import botocore
import logging

log = logging.getLogger('hero:aws:sqs')

def receive_messages(session, queue_url, num=1):
    """
    Call this from a worker to get a task.

    Returns some number of messages from a specific `queue_url`.
    """
    log.debug('receive_messages')
    client = session.client("sqs")
    message_packet = client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=num)

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


def delete_queue(session, queue_url):
    """
    Delete a queue
    """
    log.debug('delete_queue')
    try:
        log.info(f"deleting {queue_url}")
        client = session.client("sqs")
        client.delete_queue(QueueUrl=queue_url)
    except botocore.exceptions.ClientError as err:
        log.error(str(err))


def create_queue(session, queue_name, visibility_timeout):
    log.debug('create_queue')
    client = session.client("sqs")
    client.create_queue(
        QueueName=queue_name,
        Attributes={"VisibilityTimeout": visibility_timeout},
    )


def get_queue_url(session, queue_name):
    log.debug('get_queue_url')
    print(queue_name)
    client = session.client("sqs")
    response = client.get_queue_url(QueueName=queue_name)
    return response.get('QueueUrl')