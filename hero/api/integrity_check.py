import time
from botocore.exceptions import ClientError
from . integrity import QueueDoesNotExits, RetryAttemptsExceeded, QueueNotInDynamo

from . queue import get_queue_url

import logging

log = logging.getLogger(__name__)

def integrity_check(func):
    def wrapper(self, *args, **kwargs):
        try:
            self.login()
            return func(self, *args, **kwargs)
        
        except ClientError as e:
            log.debug(f"ClientError {e.response['Error']['Code']}")
            if e.response["Error"]["Code"] == "ExpiredTokenException":
                log.error(f"AWS token expired ")
                self.aws_credentials = None
                self.login()
                return func(self, *args, **kwargs)
            
            if e.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
                time.sleep(1)
                try:
                    self._queue_url = get_queue_url(self._session, self._project, self._queue_name)
                    self._queue_count = 0
                    log.debug("new queue url", self._queue_url)
                    return func(self, *args, **kwargs)
                except QueueDoesNotExits as e:
                    log.debug("QueueDoesNotExits")
                    return None 
                
        except RetryAttemptsExceeded as e:
            try:
                self._queue_url = get_queue_url(self._session, self._project, self._queue_name)
                self._queue_count = 0
                log.debug(f"RetryAttemptsExceeded: using queue ending in {self._queue_url[-10:]}")
                return None
            except QueueDoesNotExits as e:
                    log.debug("QueueDoesNotExits")
                    self._queue_url = get_queue_url(self._session, self._project, self._queue_name)
                    self._queue_count = 0
                    return None 
            except QueueNotInDynamo as e:
                log.debug("QueueNotInDynamo")
                self._queue_url = None
                self._queue_count = 0
                return None
                
        except QueueDoesNotExits as e:
            log.debug("QueueDoesNotExits")
            self._queue_url = get_queue_url(self._session, self._project, self._queue_name)
            self._queue_count = 0
            return None
        
        except QueueNotInDynamo as e:
            log.debug("QueueDoesNotExits")
            self._queue_url = None
            self._queue_count = 0
            return None
        
    return wrapper