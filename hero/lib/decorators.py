import os
import logging
from functools import wraps
from tenacity import stop_after_attempt, wait_fixed, wait_exponential
import boto3
from .errors import HeroRetryError

log = logging.getLogger("hero:service")


def decorate_all(decorator):

    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)) and not attr.startswith("__"):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate


def log_errors(func):
    log_all_errors = bool(os.environ.get("HERO_LOG_ALL_ERRORS", "True"))

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # print('Hi, im about to do the function, woop woop')
            res = func(*args, **kwargs)
            # print('Function complete, woop woop')
            return res
        except:
            if log_all_errors:
                log.error("Hero Service Error: \n", exc_info=True)
            raise

    return wrapper


def track_calls(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self._calls += 1
        return func(self, *args, **kwargs)

    return wrapper


def retry_method(func, errFunc):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # attempts order: kwargs -> EVN -> default

        attempts = int(
            kwargs.get(
                "attempts",
                os.environ.get("HERO_RETRY_ATTEMPTS", self.default_attempts),
            )
        )

        wait_schedule = str(
            kwargs.get(
                "wait",
                os.environ.get("HERO_RETRY_WAIT", self.default_wait),
            )
        )

        # print(str(func.__name__), wait_schedule)
        wait = wait_fixed(1)
        if wait_schedule == "exp":
            wait = wait_exponential(multiplier=1, min=1, max=60)

        try:
            local_instance = errFunc.retry_with(
                stop=stop_after_attempt(attempts), wait=wait
            )
            results = local_instance.__call__(self, func, *args, **kwargs)
            return results

        except Exception as e:
            raise HeroRetryError(
                str(e),
                local_instance.retry.statistics.get("attempt_number"),
                local_instance.retry.statistics.get("idle_for"),
            )

    return wrapper


def delete_sqs_messages(func):
    """Deletes all task engine messages when they are used as an event source to lambda."""

    @wraps(func)
    def wrapper(event, context):
        # Initialize the SQS client

        sqs = boto3.client("sqs")

        for record in event.get("Records", []):
            try:
                # Extract the queue ARN and receipt handle
                queue_arn = record["eventSourceARN"]
                receipt_handle = record["receiptHandle"]
            except Exception as e:
                print(f"Key error in record: {str(e)}")
                continue

            # Convert ARN to Queue URL
            try:
                queue_url = sqs.get_queue_url(QueueName=queue_arn.split(":")[-1])[
                    "QueueUrl"
                ]
            except Exception as e:
                print(f"Error resolving Queue URL from ARN: {str(e)}")
                continue

            # Delete the message
            try:
                response = sqs.delete_message(
                    QueueUrl=queue_url, ReceiptHandle=receipt_handle
                )
                print(f"Message deleted successfully: {response}")
            except Exception as e:
                print(f"Error deleting message: {str(e)}")

        # Pass the remaining logic to the original Lambda handler
        return func(event, context)

    return wrapper
