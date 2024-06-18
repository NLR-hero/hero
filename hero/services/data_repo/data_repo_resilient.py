from tenacity import retry, TryAgain, stop_after_attempt, wait_fixed, retry_if_exception_type

from ... import errors
from ...service import retry_method, track_calls
from ...config import get_data_repo_scopes, get_data_repo_id

from .data_repo import DataRepo
from .data_repo_api import DataRepoApi

retryable_exceptions = (
    retry_if_exception_type(errors.ApiUnauthorized)
    | retry_if_exception_type(errors.ApiQueueDoesNotExist)
    | retry_if_exception_type(errors.ClientCreateProject)
    | retry_if_exception_type(errors.ClientCreateDataset)
    | retry_if_exception_type(errors.ClientCreateFileObject)
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
    except (errors.ApiUnauthorized, errors.ApiQueueDoesNotExist) as e:
        self._login()
        raise TryAgain(str(e))

    except (
        errors.ClientCreateProject,
        errors.ClientCreateDataset,
        errors.ClientCreateFileObject,
    ) as e:
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

class DataRepoResilient(DataRepo, metaclass=ResilientServiceMeta):
    def _configure(self):
        self.api = DataRepoApi(resilient_session=True)
        self._scopes = get_data_repo_scopes()
        self._datarepo_id = get_data_repo_id()




