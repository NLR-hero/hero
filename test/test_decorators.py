import os
import logging
from functools import wraps
import pytest

from hero.lib.decorators import decorate_all, log_errors

# Enable error logging via env var
os.environ["HERO_LOG_ALL_ERRORS"] = "True"
log = logging.getLogger("hero")


@decorate_all(log_errors)
class ServiceBase:
    def base_method(self):
        raise RuntimeError("Base method failed")


@decorate_all(log_errors)
class MyService(ServiceBase):
    def my_method(self):
        raise ValueError("My method failed")


@pytest.fixture
def service():
    return MyService()


@pytest.mark.parametrize(
    "method_name, expected_exception",
    [
        ("base_method", RuntimeError),
        ("my_method", ValueError),
    ],
)
def test_decorated_methods_raise_and_log(
    service, method_name, expected_exception, caplog
):
    method = getattr(service, method_name)
    with caplog.at_level(logging.ERROR, logger="hero"):
        with pytest.raises(expected_exception):
            method()
        assert f"Hero Service Error in {method_name}" in caplog.text
