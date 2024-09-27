import os
import logging
from functools import wraps
from tenacity import stop_after_attempt, wait_fixed, wait_exponential

from .errors import HeroRetryError

log = logging.getLogger("hero:service")


def decorate_all(decorator):
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)) and not attr.startswith("__"):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate


def log_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # print('Hi, im about to do the function, woop woop')
            res = func(*args, **kwargs)
            # print('Function complete, woop woop')
            return res
        except:
            log.error("Hero Service Error: \n", exc_info=True)

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
