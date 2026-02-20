""" event_trigger.py
Emulate the Event Source Trigger that start Lambda in AWS to instead run a local version of your worker entry point.
This will long poll the SQS queue using boto3. Create your queue and tasks in the queue using the TaskEngine.

To get this set up I ran `python bin/create_test_queue.py` to create the queue we will listen to. Then I copy and paste the queueUrl from the TaskEngine Queue here.

To run this you will need to both activate the virtual environment `source .venv/bin/activate` and use your AWS access keys. Then run:

```
export SECRET_NAME="dev-gates-appDevGatesAssistan" python event_trigger.py
```

Author: Nick Wunder
Version: February 2026
"""

import uuid
import time
import math
import tracemalloc

from ..client import HeroClient
from .loaders import load_environment, load_runtime_config

def invoke_lambda(handler, event, context):
    ''' Dynamically load the worker on every poll
    '''
    print(f"START RequestId: {context.aws_request_id}")
    start_time = time.perf_counter()
    tracemalloc.start()

    try:
        handler(event, context)
    except Exception as e:
        raise
    finally:
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        duration_ms = (time.perf_counter() - start_time) * 1000

        # Lambda bills in 1 ms increments now (used to be 100ms)
        billed_duration_ms = math.ceil(duration_ms)

        max_memory_mb = peak / (1024 * 1024)

        print(f"END RequestId: {context.aws_request_id}")
        print(
            f"REPORT RequestId: {context.aws_request_id} "
            f"Duration: {duration_ms:.2f} ms "
            f"Billed Duration: {billed_duration_ms} ms "
            f"Memory Size: {context.memory_limit_in_mb} MB "
            f"Max Memory Used: {max_memory_mb:.2f} MB"
        )

class LocalContext:
    def __init__(self, memory_limit_in_mb=128):
        self.function_name = "local-sqs-lambda"
        self.memory_limit_in_mb = memory_limit_in_mb
        self.invoked_function_arn = "arn:aws:lambda:local:0:function:local-sqs-lambda"
        self.aws_request_id = f"local-request-id-{uuid.uuid4()}"


def build_lambda_event(messages):
    return {
        "Records": [
            {
                "messageId": msg["MessageId"],
                "receiptHandle": msg["ReceiptHandle"],
                "body": msg["Body"],
                "attributes": msg.get("Attributes", {}),
                "messageAttributes": msg.get("MessageAttributes", {}),
                "md5OfBody": msg["MD5OfBody"],
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:local:000000000000:local-queue",
                "awsRegion": "us-west-2",
            }
            for msg in messages
        ]
    }

def event_trigger(queue_name, handler):
    """
    Emulate the Event Source Trigger that start Lambda in AWS

    Parameters
    ----------
    queue_name : string
        The name of a TaskEngine queue
    
    handler : function
        The lambda handler entry point
    """
    try:
        import boto3
    except ImportError as e:
        raise ImportError(
            "AssistantService requires the optional dependency 'boto3'.\n"
            "Install with: uv add boto3"
        ) from e

    runtime_config = load_runtime_config()
    application_id = load_environment(runtime_config)
    sqs = boto3.client("sqs", region_name="us-west-2")
    hero_client = HeroClient()
    task_engine = hero_client.TaskEngine(application_id)
    hero_client.authenticate()

    queue_record = task_engine.read_queue_by_name(name=queue_name)
    QUEUE_URL = queue_record['queueUrl']

    print(f"Listening for messages on '{queue_record['name']}'...")

    while True:
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=5,
            WaitTimeSeconds=10
        )

        messages = response.get("Messages", [])
        if not messages:
            continue

        event = build_lambda_event(messages)
        context = LocalContext()

        invoke_lambda(handler, event, context)

        # delete messages after processing
        for msg in messages:
            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=msg["ReceiptHandle"]
            )

