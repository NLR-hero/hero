from ..config import get_resilient_session
from .resilient_session import ResilientSession
from .standard_session import StandardSession
from .session_hooks import log_request, check_for_errors

class ApiBase:
    def __init__(self, resilient_session=False):
        self._resilient_session = resilient_session or get_resilient_session()
        self.session = self.get_request_session()
        self._after_init()

    def get_request_session(self):
        if self._resilient_session:
            session = ResilientSession()
        else:
            session = StandardSession()

        session.hooks['response'] = [log_request, check_for_errors]
        return session

    def _after_init(self):
        pass

    def get_headers(self, token):
        return {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}