from tenacity import retry, TryAgain, stop_after_attempt, wait_fixed, retry_if_exception_type

from ... import errors
from ...service import retry_method, track_calls
from ...config import get_task_engine_id

from .queue import Queue
from .task_engine_api import TaskEngineApi
from .task_engine_service import TaskEngineService

retryable_exceptions = (
    retry_if_exception_type(errors.ApiUnauthorized)
    | retry_if_exception_type(errors.ApiQueueDoesNotExist)
    | retry_if_exception_type(errors.ApiItemNotFound)
    | retry_if_exception_type(errors.ClientQueueNotActive)
    | retry_if_exception_type(errors.ClientNoQueueObject)
    | retry_if_exception_type(errors.ClientPullTasksEmpty)
    | retry_if_exception_type(errors.ClientReadyTaskEstimate)
    | retry_if_exception_type(errors.ClientRetry)
)

@retry(
    stop=stop_after_attempt(4),
    wait=wait_fixed(1),
    reraise=True,
    retry=retryable_exceptions,
)
def handle_resilient_exceptions(self, func, *args, **kwargs):
    """Functions, such as self._login and self._get_active_queue should
    not trigger a retry because this will cause an infinite loop.
    """

    try:
        return func(self, *args, **kwargs)

    # for issues with the infrastructure, we can attempt to
    # fix the issues
    except errors.ApiUnauthorized as e:
        # print("     ApiUnauthorized")
        self._login()
        raise TryAgain(str(e))

    except (
        errors.ApiQueueDoesNotExist,
        errors.ApiItemNotFound,
        errors.ClientQueueNotActive,
        errors.ClientNoQueueObject,
    ) as e:
        # print(f"     {str(e)}")
        self._get_active_queue()
        raise TryAgain(str(e))

    # for operations, if everything else has passed, and we are here
    # then we just try again
    except (
        errors.ClientPullTasksEmpty,
        errors.ClientReadyTaskEstimate,
        errors.ClientRetry,
    ) as e:
        # print(f"     {str(e)}")
        raise TryAgain(str(e))


class ResilientServiceMeta(type):
    def __new__(cls, name, bases, dct):
        dct['_calls'] = 0
        dct['default_attempts']  = 10
        dct['default_wait']  = "fix"

        for attr in dct:
            if callable(dct[attr]):
                if not attr.startswith('__'):
                    if not attr.startswith('_'):
                        dct[attr] = retry_method(
                            dct[attr],
                            handle_resilient_exceptions)
                    dct[attr] = track_calls(dct[attr])

        return super().__new__(cls, name, bases, dct)


class TaskEngineResilientService(TaskEngineService, metaclass=ResilientServiceMeta):
    def __init__(self, queue_name):
        self._queue_name = queue_name
        self._queue = None
        super().__init__()

    def _configure(self):
        self.api = TaskEngineApi(resilient_session=True)
        self._task_engine_id = get_task_engine_id()


