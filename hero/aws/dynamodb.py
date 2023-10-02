import boto3
import botocore
import logging
from decimal import Decimal
import json

from ..api.task import READY, CLAIMED, COMPLETE, FAILED

log = logging.getLogger(__name__)

def get_table(session, table_name):
    """Gets the table opject for table_name"""
    dyn_resource = session.resource("dynamodb")
    table = dyn_resource.Table(table_name)
    table.load()
    return table


#TODO: this goes in <???>
def get_project_table(session, project):
    """Gets the table opject for a specific project"""
    table_name = f"hero-{project}"
    return get_table(session, table_name)


#TODO: this has logic for dynamo and the task, can we make this more focused?
def put_item(session, project, item):
    """Puts an item into the table"""
    table = get_project_table(session, project)
    tmp = json.loads(json.dumps(item), parse_float=Decimal)
    response = table.put_item(Item=tmp)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    return item.task_id


#TODO: this has logic for dynamo and the task, can we make this more focused?
#TODO: use boto3 dyanmodb marshaler?
def put_items(session, project, items):
    """Puts a list of items into the table using batch writer"""
    table = get_project_table(session, project)
    ids = []
    with table.batch_writer() as batch:
        for item in items:
            tmp = json.loads(json.dumps(item.data), parse_float=Decimal)
            batch.put_item(Item=tmp)
            ids.append(item.task_id)
    return ids


#TODO: this has logic for dynamo and the task, can we make this more focused?
def get_item(table, job_id, queue):
    """Gets an item from the table"""
    return table.get_item(Key={"id": job_id, "queue": queue})


#TODO: this has logic for dynamo and the task, can we make this more focused?
def update_item_claimed(table, job_id, queue, resource_name, worker_id):
    """
    Updates the status of an item to claimed only if it is ready.
    Returns True if the item was updated, False if it was not.
    """
    try:
        response = table.update_item(
            Key={"id": job_id, "queue": queue},
            UpdateExpression="SET #status = :val, #claimed_resource_name = :val2,  #claimed_worker_id = :val3", 
            ExpressionAttributeValues={
                ":val": CLAIMED, 
                ":ready": READY, 
                ":val2": resource_name,
                ":val3": worker_id
            },
            ExpressionAttributeNames={
                "#status": "status", 
                "#claimed_resource_name": "claimed_resource_name",
                "#claimed_worker_id": "claimed_worker_id"
            },
            ConditionExpression="#status = :ready",
        )
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False
        else:
            raise e.response["Error"]
    return True

#TODO: this has logic for dynamo and the task, can we make this more focused?
def update_item_results(session, project, job_id, queue, results={}):
    """Updates the status of an item to done and adds the results"""
    table = get_project_table(session, project)
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
    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        return True


#TODO: this probably doesn't belong anymore since we are managing infra in the CDK
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
    return True