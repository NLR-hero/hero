import os

from ...service import ServiceBase
from ...api import ApiBase

from ...config import get_m3s_id, get_m3s_scopes, get_mlflow_tracking_uri

class M3SService(ServiceBase):

    def __init__(self):
        self.tracking_uri = get_mlflow_tracking_uri()
        super().__init__()

    def _configure(self):
        self.api = ApiBase() #used for auth, base is adequate for this
        self._m3s_id = get_m3s_id() #not used, do we need this?
        self._scopes = get_m3s_scopes()

    def _after_init(self):
        self.set_mlflow_tracking_token(self._access_token)

    def set_mlflow_tracking_token(self, token=None):
        """Sets the MLFlow tracking token in the environment"""
        os.environ['MLFLOW_TRACKING_TOKEN'] = token