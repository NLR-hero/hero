import json
import boto3

from boto3.dynamodb.types import TypeDeserializer


def lambda_handler(event, context):
    """ Only handle insert events """
    sqs = boto3.client("sqs")
    deserializer = TypeDeserializer()
    
    insert_events = [x for x in event["Records"] if x["eventName"] == "INSERT"]
    modify_events = [x for x in event["Records"] if x["eventName"] == "MODIFY"]
    remove_events = [x for x in event["Records"] if x["eventName"] == "REMOVE"]

    print(
        f"INSERT --> {len(insert_events)}.  MODIFY --> {len(modify_events)}. REMOVE --> {len(remove_events)}"
    )

    # organize insert events
    collections = {}
    for record in insert_events:
        python_data = {k: deserializer.deserialize(v) for k,v in record['dynamodb']['NewImage'].items()}
        # print(python_data)
        queue_url = python_data.get("queue_url", None)
        if queue_url is not None:
            collections[queue_url] = collections.get(queue_url, [])
            collections[queue_url].append({
                    'Id': python_data['id'],
                    'MessageBody': json.dumps(python_data, default=str)
                })
        
    # send to sqs 
    max_batch_size = 10
    for key in collections.keys():
        # print(key)
        list_data = collections[key]
        insert_chunks = [list_data[x:x+max_batch_size] for x in range(0, len(list_data), max_batch_size)]
        for records in insert_chunks:
            try:
                response = sqs.send_message_batch(QueueUrl=key,
                                              Entries=records)
            except Exception as e:
                print(str(e))
    

    return {"statusCode": 200, "body": json.dumps("Processed DynamoDB to SQS")}
