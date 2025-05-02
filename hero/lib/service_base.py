import os
from requests import Session

from .config import get_resilient_session
from .resilient_session import ResilientSession
from .session_hooks import log_request, check_for_errors
from .decorators import decorate_all, log_errors


@decorate_all(log_errors)
class ServiceBase:
    def __init__(self, clientInstance, application_id=None, resilient_session=False):
        self.client = clientInstance
        self.application_id = (
            application_id
            if application_id is not None
            else f"{os.environ.get('HERO_ENV')}-{os.environ.get('HERO_PROJECT')}"
        )
        self.client.authenticate()
        self._configure()
        is_resilient = resilient_session or get_resilient_session()
        self.api = self.get_request_session(is_resilient)
        self._after_init()

    def _configure(self):
        return None

    def _after_init(self):
        return None

    def get_request_session(self, is_resilient):
        if is_resilient:
            api = ResilientSession()
        else:
            api = Session()

        api.hooks["response"] = [log_request, check_for_errors]
        return api

    def get_headers(self, token):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
