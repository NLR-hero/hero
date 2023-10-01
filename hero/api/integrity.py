import time
from botocore.exceptions import ClientError

class RetryAttemptsExceeded(Exception):
    def __init__(self):
        super().__init__('Failed due to number of retry attempts.')

class QueueDoesNotExits(Exception):
    def __init__(self):
        super().__init__('Queue does not exist.')

class QueueNotInDynamo(Exception):
    def __init__(self):
        super().__init__('Queue does not exist.')




