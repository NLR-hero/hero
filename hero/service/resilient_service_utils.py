import os
from tenacity import stop_after_attempt, wait_fixed, wait_exponential

from ..errors import HeroRetryError

def track_calls(func):
    def wrapper(self, *args, **kwargs):
        self._calls += 1
        return func(self, *args, **kwargs)

    return wrapper


def retry_method(func, errFunc):
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

