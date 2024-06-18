from tenacity import (
    retry_if_exception_type,
)


class HeroRetryError(RuntimeError):
    def __init__(
        self,
        message,
        attempt_number,
        idle_for,
    ):
        super().__init__(message)
        self.attempt_number = attempt_number
        self.idle_for = idle_for


class ClientPullTasksEmpty(Exception):
    pass


class ApiUnauthorized(Exception):
    pass


class ApiQueueDoesNotExist(Exception):
    pass


class ApiItemNotFound(Exception):
    pass


class ClientQueueNotActive(Exception):
    pass


class ClientReadyTaskEstimate(Exception):
    pass


class ClientRetry(Exception):
    pass


class ClientNoQueueObject(Exception):
    pass


class ClientCreateProject(Exception):
    pass


class ClientCreateDataset(Exception):
    pass


class ClientCreateFileObject(Exception):
    pass
