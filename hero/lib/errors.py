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


class TokenInvalidSignatureError(Exception):
    def __init__(self, message="Invalid token signature"):
        super().__init__(message)


class TokenDecodeError(Exception):
    def __init__(self, message="Token decode error"):
        super().__init__(message)


class TokenInvalidError(Exception):
    def __init__(self, message="Invalid token"):
        super().__init__(message)


class TokenGeneralError(Exception):
    def __init__(self, message="Token error"):
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


class HEROMLModelRegistryResourceAlreadyExists(Exception):
    def __init__(self, message="HERO ML Model Registry resource already exists"):
        super().__init__(message)


class HEROMLModelRegistryResourceNotFound(Exception):
    def __init__(self, message="HERO ML Model Registry resource not found"):
        super().__init__(message)


class HEROMLModelRegistryForbiddenError(Exception):
    def __init__(self, registry_name=None, operation=None, message=None):
        if message is None:
            if registry_name and operation:
                message = (
                    f"HERO ML Model Registry access denied for registry '{registry_name}' "
                    f"during '{operation}'"
                )
            elif registry_name:
                message = f"HERO ML Model Registry access denied for registry '{registry_name}'"
            else:
                message = "HERO ML Model Registry access denied"
        super().__init__(message)
        self.registry_name = registry_name
        self.operation = operation
