import os

from tenacity import retry, stop_after_attempt, wait_fixed, TryAgain, wait_exponential
from ..errors import HeroRetryError, data_repo_exceptions
from .. import errors

DEFAULT_ATTEMPTS = 10
DEFAULT_WAIT = "fix"


@retry(
    stop=stop_after_attempt(4),
    wait=wait_fixed(1),
    reraise=True,
    retry=data_repo_exceptions,
)
def data_repo_handle_exceptions(self, func, *args, **kwargs):
    """Functions, such as self._login and self._get_active_queue should
    not trigger a retry because this will cause an infinite loop.
    """

    try:
        return func(self, *args, **kwargs)

    # for issues with the infrastructure, we can attempt to
    # fix the issues
    except (errors.ApiUnauthorized, errors.ApiQueueDoesNotExist) as e:
        # print("     ApiUnauthorized")
        self._login()
        raise TryAgain(str(e))


def retry_method(func):

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
            local_instance = data_repo_handle_exceptions.retry_with(
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
