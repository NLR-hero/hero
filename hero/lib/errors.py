import difflib

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


class HeroConfigurationError(Exception):
    """Base class for errors caused by a misconfigured HERO client."""


class InvalidEnvironmentError(HeroConfigurationError):
    def __init__(
        self,
        env,
        valid_environments,
        source="the HERO_ENV environment variable",
    ):
        valid = tuple(valid_environments)
        message = (
            f"Invalid HERO environment {env!r} (from {source}). "
            f"Valid environments are: {', '.join(valid)}."
        )
        close_match = difflib.get_close_matches(str(env), valid, n=1, cutoff=0.3)
        if close_match:
            message += f" Did you mean {close_match[0]!r}?"
        super().__init__(message)
        self.env = env
        self.valid_environments = valid


class InvalidPoolError(HeroConfigurationError):
    def __init__(self, pool, valid_pools):
        valid = tuple(valid_pools)
        super().__init__(
            f"Invalid HERO user pool {pool!r}. Valid pools are: {', '.join(valid)}."
        )
        self.pool = pool
        self.valid_pools = valid


class MissingConfigurationError(HeroConfigurationError):
    def __init__(self, key, env, available_keys=()):
        message = (
            f"Configuration key {key!r} is not defined for HERO environment {env!r}. "
            f"Set the {key} environment variable to provide it explicitly."
        )
        if available_keys:
            message += f" Keys available for {env!r}: {', '.join(available_keys)}."
        super().__init__(message)
        self.key = key
        self.env = env
