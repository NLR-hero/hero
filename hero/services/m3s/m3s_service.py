import os

from ...service import ServiceBase
from ...api import ApiBase

from ...config import get_m3s_id, get_mlflow_tracking_uri

class M3SService(ServiceBase):

    def __init__(self, clientInstance, m3s_name):
        if not m3s_name:
            raise ValueError("m3s_name must be provided")
        self.tracking_uri = get_mlflow_tracking_uri()
        super().__init__(clientInstance)

    def _configure(self):
        self.api = ApiBase()
        self._m3s_id = get_m3s_id() #not used, do we need this?
        self.client.add_scope('m3s/user')


    def _after_init(self):
        self.set_mlflow_tracking_token(self.client.get_token())

    def set_mlflow_tracking_token(self, token=None):
        """Sets the MLFlow tracking token in the environment"""
        os.environ['MLFLOW_TRACKING_TOKEN'] = token