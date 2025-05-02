import os
import logging
from functools import wraps
from tenacity import stop_after_attempt, wait_fixed, wait_exponential

from .errors import HeroRetryError

log = logging.getLogger("hero:service")


def decorate_all(decorator):

    def decorate(cls):
        for name, attr in cls.__dict__.items():
            if name.startswith("__"):
                continue
            if isinstance(attr, staticmethod):
                setattr(cls, name, staticmethod(decorator(attr.__func__)))
            elif isinstance(attr, classmethod):
                setattr(cls, name, classmethod(decorator(attr.__func__)))
            elif callable(attr):
                setattr(cls, name, decorator(attr))
        return cls

    return decorate


def log_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            if os.getenv("HERO_LOG_ALL_ERRORS") == "True":
                log.error(f"Hero Service Error in {func.__name__}", exc_info=True)
            raise

    return wrapper


def track_calls(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self._calls += 1
        return func(self, *args, **kwargs)

    return wrapper


def retry_method(func, errFunc):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # attempts order: kwargs -> EVN -> default

        attempts = int(
            kwargs.get(
                "attempts",
                os.environ.get("HERO_RETRY_ATTEMPTS", self.default_attempts),
            )
        )

        wait_schedule = str(
            kwargs.get(
                "wait",
                os.environ.get("HERO_RETRY_WAIT", self.default_wait),
            )
        )

        # print(str(func.__name__), wait_schedule)
        wait = wait_fixed(1)
        if wait_schedule == "exp":
            wait = wait_exponential(multiplier=1, min=1, max=60)

        try:
            local_instance = errFunc.retry_with(
                stop=stop_after_attempt(attempts), wait=wait
            )
            results = local_instance.__call__(self, func, *args, **kwargs)
            return results

        except Exception as e:
            raise HeroRetryError(
                str(e),
                local_instance.retry.statistics.get("attempt_number"),
                local_instance.retry.statistics.get("idle_for"),
            )

    return wrapper
