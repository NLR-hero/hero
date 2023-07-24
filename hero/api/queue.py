"""
Queues are a main component of the Task Engine. This modules provides direct access to SQS via boto3.

Key Features:

* Queues are ephemeral. They can be created and destroyed at any time.
* The SQS API and boto3 are very fast with high scalability expected.
* Queues act as the bridge between services that presist task state and results.
"""
from .. import aws
from ..config import config
from .utils import retry

import time
import json
import uuid
import logging

log = logging.getLogger('hero:api:queue')

def update_queue_url(queue_url, project=None, queue=None):
    """
    Sets the current queue_url in the dynamodb table
    """
    log.debug('update_queue_url')
    session = aws.utils.get_session()
    table_name = 'hero-dynamodb-project-queue-names'
    table = aws.dynamodb.get_table(session, table_name)
    project = config.get_project(project)
    queue = config.get_queue(queue)
    
    response = table.update_item(
        Key={"queue_prefix": queue, "project_name": project},
        UpdateExpression="set  #queue_url=:s",
        ExpressionAttributeNames={
            "#queue_url": "queue_url",
        },
        ExpressionAttributeValues={":s": queue_url},
        ReturnValues="UPDATED_NEW",
    )
    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        # Make this look like it is an API call for now, until the actualy api is ready
        return response['Attributes']
    else:
        raise Exception('Error updating queue URL')


def get_queue_url(project=None, queue=None):
    log.debug('get_queue_url')
    session = aws.utils.get_session()
    table_name = 'hero-dynamodb-project-queue-names'
    table = aws.dynamodb.get_table(session, table_name)
    project = config.get_project(project)
    queue = config.get_queue(queue)

    response = table.get_item(Key={"queue_prefix": queue, "project_name": project})
    return response["Item"]["queue_url"]


def list_queues(project=None, queue=None):
    '''
    Each time a queue is created a UUID is attached to the end of the full queue name. This allows clients to create multiple unique queues with a consistent and predictable prefix.

    Yields queue urls for all queues with the hero-project-queue prefix.
    '''
    log.debug('list_queues')
    session = aws.utils.get_session()
    project = config.get_project(project)
    queue = config.get_queue(queue)
    queue_prefix = f"hero-{project}-{queue}-"

    return aws.sqs.list_queues(session, queue_prefix)


def delete_other_queues(queue_url, project=None, queue=None):
    """
    Workers can optionally remove all previously created queues to start a fresh campaign. This will remove all other queues with a hero-project prefix.

    For example, say in campaign A you created a queue "hero-project-queue000". This campaign completed but the queue was not cleaned up. Then you want to start a new campaign with the same input parameters, but you don't want to reuse an old queue. Calling this function will find all of the queues that start with "hero-project-queue000" and delete them as long as they are not the current queue. Remember, each time a queue is crated a uuid is attached to the end of the queue name.
    """
    log.debug('delete_other_queues')
    session = aws.utils.get_session()
    queue_list = list(list_queues(project, queue))
    for temp_queue_url in queue_list:
        if temp_queue_url != queue_url:
            aws.sqs.delete_queue(session, temp_queue_url)


def create_queue(project=None, queue=None):
    """
    Creates a new unique queue.
    """
    log.debug('create_queue')
    session = aws.utils.get_session()
    project = config.get_project(project)
    queue = config.get_queue(queue)

    queue_name = f"hero-{project}-{queue}-{str(uuid.uuid4())}"
    visibility_timeout = config.get_queue_visibility_timeout()
    aws.sqs.create_queue(session, queue_name, visibility_timeout)

    def _get_queue_url(project, queue):
        result = aws.sqs.get_queue_url(session, queue_name)
        return result

    queue_url = retry(_get_queue_url, project, queue, attempts=1)
    update_queue_url(queue_url, project, queue)
    return queue_url
