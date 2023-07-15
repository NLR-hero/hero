"""
Contains wrappers for dynamodb functions
"""
import os
import boto3
import logging
import botocore
from botocore.exceptions import ClientError

from .session import get_project, get_queue
from .task import READY, CLAIMED, COMPLETE

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger("gantry:dynamo")


class Dynamo:
    def __init__(self, session):
        self.session = session
        self.table_name = 'hero-table'

    def get_table(self, table_name):
        """Gets the table opject for table_name"""
        dyn_resource = self.session.resource('dynamodb')
        table = dyn_resource.Table(table_name)
        table.load()
        return table



def get_table(session, table_name):
    """Gets the table opject for table_name"""
    dyn_resource = session.resource("dynamodb")
    table = dyn_resource.Table(table_name)
    table.load()
    return table


def get_project_table(session, project):
    """Gets the table opject for a specific project"""
    table_name = f"hero-{project}"
    return get_table(session, table_name)


def update_queue_url(session, project, queue, queue_url, table_name="hero-dynamodb-project-queue-names"):
    """Sets the current queue_url in the dynamodb table"""
    table = get_table(session, table_name)
    response = table.update_item(
        Key={"queue_prefix": queue, "project_name": project},
        UpdateExpression="set  #queue_url=:s",
        ExpressionAttributeNames={
            "#queue_url": "queue_url",
        },
        ExpressionAttributeValues={":s": queue_url},
        ReturnValues="UPDATED_NEW",
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def get_queue_url(session, project, queue, table_name="hero-dynamodb-project-queue-names"):
    table = get_table(session, table_name)
    response = table.get_item(Key={"queue_prefix": queue, "project_name": project})
    return response["Item"]["queue_url"]


def put_item(table, item):
    """Puts an item into the table"""
    print(item.data)
    response = table.put_item(Item=item.data)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    return item.task_id


def put_items(table, items):
    """Puts a list of items into the table using batch writer"""
    ids = []
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item.data)
            ids.append(item.task_id)
    return ids


def get_item(table, job_id, queue):
    """Gets an item from the table"""
    return table.get_item(Key={"id": job_id, "queue": queue})


def update_item_claimed(table, job_id, queue):
    """Updates the status of an item to claimed only if it is ready.
    Returns True if the item was updated, False if it was not.
    """
    try:
        response = table.update_item(
            Key={"id": job_id, "queue": queue},
            UpdateExpression="SET #status = :val",
            ExpressionAttributeValues={":val": CLAIMED, ":ready": READY},
            ExpressionAttributeNames={"#status": "status"},
            ConditionExpression="#status = :ready",
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False
        else:
            raise e.response["Error"]
    return True


def update_item_results(table, job_id, queue, results={}):
    """Updates the status of an item to done and adds the results"""
    response = table.update_item(
        Key={"id": job_id, "queue": queue},
        UpdateExpression="set #status=:s, #results=:r",
        ExpressionAttributeNames={
            "#status": "status",
            "#results": "results",
        },
        ExpressionAttributeValues={
            ":s": COMPLETE,
            ":r": results,
        },
        ReturnValues="UPDATED_NEW",
    )


def delete_table(table, tototal_segments=1, rank=0):
    """deletes the table in batches of up to 10 parallel workers"""
    tableKeyNames = [key.get("AttributeName") for key in table.key_schema]

    # Only retrieve the keys for each item in the table (minimize data transfer)
    projectionExpression = ", ".join("#" + key for key in tableKeyNames)
    expressionAttrNames = {"#" + key: key for key in tableKeyNames}

    counter = 0
    page = table.scan(TotalSegments=tototal_segments, Segment=rank)
    log.info(f"{rank}     Deleting dynamo table")
    with table.batch_writer() as batch:
        while page["Count"] > 0:
            log.info(f"{rank}     deleting {page['Count']} from dynamo table")
            counter += page["Count"]
            # Delete items in batches
            for itemKeys in page["Items"]:
                # print(itemKeys)
                try:
                    batch.delete_item(
                        Key={"id": itemKeys["id"], "queue": itemKeys["queue"]}
                    )
                except Exception as e:
                    log.error(str(e))
            # Fetch the next page
            if "LastEvaluatedKey" in page:
                page = table.scan(
                    ProjectionExpression=projectionExpression,
                    ExpressionAttributeNames=expressionAttrNames,
                    ExclusiveStartKey=page["LastEvaluatedKey"],
                    TotalSegments=tototal_segments,
                    Segment=rank,
                )
            else:
                break

    log.info(f"{rank}     Deleted {counter}")
