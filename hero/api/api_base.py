from ..config import get_resilient_session
from .resilient_session import ResilientSession
from .standard_session import StandardSession

class ApiBase:
    def __init__(self, resilient_session=False):
        self._resilient_session = resilient_session or get_resilient_session()
        self.session = self.getRequestSession()

    def getRequestSession(self):
        if self._resilient_session:
            return ResilientSession()
        else:
            return StandardSession()

    def getHeaders(self, token):
        return {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}