import os
import json
import time
import logging
import botocore
from boto3.dynamodb.conditions import Key, Attr

from ..resilent_session import ResilientSession
from .task_engine_queue_api import ACTIVE, DELETED
from ..auth.boto import get_table

log = logging.Logger(__file__)


def delete_table(session, task_engine_id, rank=0, total_segments=1):
    table = get_table(session, f"hero-task-engine-{task_engine_id}")
    tableKeyNames = [key.get("AttributeName") for key in table.key_schema]

    # Only retrieve the keys for each item in the table (minimize data transfer)
    projectionExpression = ", ".join("#" + key for key in tableKeyNames)
    expressionAttrNames = {"#" + key: key for key in tableKeyNames}

    counter = 0
    page = table.scan(TotalSegments=total_segments, Segment=rank)
    print(page["Count"])
    print(f"{rank}     Deleting dynamo table")
    with table.batch_writer() as batch:
        while page["Count"] > 0:
            print(f"{rank}     deleting {page['Count']} from dynamo table")
            counter += page["Count"]
            # Delete items in batches
            for itemKeys in page["Items"]:
                # print(itemKeys)
                try:
                    batch.delete_item(Key={"PK": itemKeys["PK"], "SK": itemKeys["SK"]})
                except Exception as e:
                    log.error("Error", str(e))
            # Fetch the next page
            if "LastEvaluatedKey" in page:
                page = table.scan(
                    ProjectionExpression=projectionExpression,
                    ExpressionAttributeNames=expressionAttrNames,
                    ExclusiveStartKey=page["LastEvaluatedKey"],
                    TotalSegments=total_segments,
                    Segment=rank,
                )
            else:
                break

    print(f"{rank}     Deleted {counter}")
    return True


def get_active_queue_gsi1(session, task_engine_id, queue_name, limit=1000):
    """
    Returns the active queue with queue_name
    """
    table = get_table(session, f"hero-task-engine-{task_engine_id}")
    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression=Key("GSI1PK").eq(f"TASKENGINE#{task_engine_id}")
        & Key("GSI1SK").begins_with("QUEUE"),
        Limit=limit,
        FilterExpression=Attr("state").eq("active"),
    )
    for queue in response["Items"]:
        if queue["name"] == queue_name:
            tmp = {
                "id": queue["id"],
                "name": queue["name"],
                "queueUrl": queue["queueUrl"],
            }
            return tmp


def get_active_queue(session, task_engine_id, queue_name, limit=1000):
    """
    Returns the active queue with queue_name
    """
    table = get_table(session, f"hero-task-engine-{task_engine_id}")
    response = table.query(
        IndexName="GSI2",
        KeyConditionExpression=Key("GSI2PK").eq("METATYPE#Queue")
        & Key("GSI2SK").eq(f"{queue_name}|{ACTIVE}"),
        Limit=limit,
    )

    for queue in response["Items"]:
        if queue["name"] == queue_name:
            tmp = {
                "id": queue["id"],
                "name": queue["name"],
                "queueUrl": queue["queueUrl"],
            }
            return tmp


def list_queues(session, queue_prefix):
    client = session.client("sqs")
    response = client.list_queues(QueueNamePrefix=queue_prefix)
    for queue_url in response.get("QueueUrls", []):
        yield queue_url


def delete_queue(session, queue_url, worker_id=0):
    try:
        log.info(f"{worker_id} deleting {queue_url}")
        client = session.client("sqs")
        client.delete_queue(QueueUrl=queue_url)
        return True
    except botocore.exceptions.ClientError as err:
        log.debug(f"{worker_id} {str(err)}")
        return False
