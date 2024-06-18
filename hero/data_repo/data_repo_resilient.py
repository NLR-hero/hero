from .errors import retry_method
from . import errors
from .data_repo import DataRepo
from tenacity import TryAgain
from ..service import ResilientServiceMeta

class DataRepoResilient(DataRepo, metaclass=ResilientServiceMeta):
    def __init__(self):
        super().__init__()

    def handle_resilient_catchable_exceptions(self, func, *args, **kwargs):
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



