import time
from botocore.exceptions import ClientError
from . integrity import QueueDoesNotExits, RetryAttemptsExceeded, QueueNotInDynamo

from . import api



def integrity_check(func):
    def wrapper(self, *args, **kwargs):
        try:
            self.login()
            return func(self, *args, **kwargs)
        
        except ClientError as e:
            print("ClientError", e.response["Error"]["Code"])
            if e.response["Error"]["Code"] == "ExpiredTokenException":
                print("token expired, getting new token")
                self.aws_credentials = None
                self.login()
                return func(self, *args, **kwargs)
            
            if e.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
                time.sleep(1)
                try:
                    self._queue_url = api.queue.get_queue_url(self._session, self._project, self._queue_name)
                    self._queue_count = 0
                    print("new queue url", self._queue_url)
                    return func(self, *args, **kwargs)
                except QueueDoesNotExits as e:
                    print("QueueDoesNotExits")
                    return None 
                
        except RetryAttemptsExceeded as e:
            try:
                self._queue_url = api.queue.get_queue_url(self._session, self._project, self._queue_name)
                self._queue_count = 0
                print(f"RetryAttemptsExceeded: using queue ending in {self._queue_url[-10:]}")
                return None
            except QueueDoesNotExits as e:
                    print("QueueDoesNotExits")
                    self._queue_url = api.queue.get_queue_url(self._session, self._project, self._queue_name)
                    self._queue_count = 0
                    return None 
            except QueueNotInDynamo as e:
                print("QueueNotInDynamo")
                self._queue_url = None
                self._queue_count = 0
                return None
                
        except QueueDoesNotExits as e:
            print("QueueDoesNotExits")
            self._queue_url = api.queue.get_queue_url(self._session, self._project, self._queue_name)
            self._queue_count = 0
            return None
        
        except QueueNotInDynamo as e:
            print("QueueDoesNotExits")
            self._queue_url = None
            self._queue_count = 0
            return None
        
    return wrapper