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


class MissingRequiredAttribute(Exception):
    def __init__(self, message="Missing required attribute"):
        super().__init__(message)


class HEROAPIResponseException(Exception):
    def __init__(
        self, message="An error occoured trying to parse the response from the API"
    ):
        super().__init__(message)


class HERODataRepoProjectNotFound(Exception):
    def __init__(self, message="HERO Data Repo project not found"):
        super().__init__(message)


class HERODataRepoProjectAlreadyExists(Exception):
    def __init__(self, message="HERO Data Repo project already exists"):
        super().__init__(message)


class HERODataRepoDatasetNotFound(Exception):
    def __init__(self, message="HERO Data Repo dataset not found"):
        super().__init__(message)


class HERODataRepoDatasetAlreadyExists(Exception):
    def __init__(self, message="HERO Data Repo dataset already exists"):
        super().__init__(message)


class HERODataRepoFileNotFound(Exception):
    def __init__(self, message="HERO Data Repo file not found"):
        super().__init__(message)


class HERODataRepoFileAlreadyExists(Exception):
    def __init__(self, message="HERO Data Repo file already exists"):
        super().__init__(message)


class HEROTaskEngineQueueNotFound(Exception):
    def __init__(self, message="HERO Task Engine queue not found"):
        super().__init__(message)


class HEROTaskEngineTaskNotFound(Exception):
    def __init__(self, message="HERO Task Engine task not found"):
        super().__init__(message)


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
