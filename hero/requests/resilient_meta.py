import os
from tenacity import stop_after_attempt, wait_fixed, wait_exponential

from ..errors import HeroRetryError

DEFAULT_ATTEMPTS = 10
DEFAULT_WAIT = "fix"

def track_calls(func):
    def wrapper(self, *args, **kwargs):
        self._calls += 1
        return func(self, *args, **kwargs)

    return wrapper


def retry_method(self, func):
    def wrapper(self, *args, **kwargs):
        # attempts order: kwargs -> EVN -> default

        attempts = int(
            kwargs.get(
                "attempts",
                os.environ.get("HERO_RETRY_ATTEMPTS", DEFAULT_ATTEMPTS),
            )
        )

        wait_schedule = str(
            kwargs.get(
                "wait",
                os.environ.get("HERO_RETRY_WAIT", DEFAULT_WAIT),
            )
        )

        # print(str(func.__name__), wait_schedule)
        wait = wait_fixed(1)
        if wait_schedule == "exp":
            wait = wait_exponential(multiplier=1, min=1, max=60)

        try:
            local_instance = self.handle_resilient_catchable_exceptions.retry_with(
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


class ResilientMetaClass(type):
    def __init__(cls, name, bases, dct):
        cls._calls = 0
        super().__init__(name, bases, dct)

    def __new__(cls, name, bases, dct):
        for attr in dct:
            val = dct[attr]
            if callable(val):
                if not attr.startswith('__'):
                    if attr != '_login':
                        dct[attr] = retry_method(cls, val)
                    dct[attr] = track_calls(val)
        return super().__new__(cls, name, bases, dct)

