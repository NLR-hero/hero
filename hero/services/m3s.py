import os

from ..lib import ServiceBase

from ..config import get_m3s_api

class M3SService(ServiceBase):

    def __init__(self, clientInstance, m3s_name):
        if not m3s_name:
            raise ValueError('m3s_name must be provided')
        self.m3s_name = m3s_name
        super().__init__(clientInstance)

    def _configure(self):
        '''
        Sets the API and adds the user scope
        '''
        self.client.add_scope('m3s/user')

    def get_tracking_uri(self):
        '''
        Sets the MLFlow tracking token in the environment and returns the tracking URI
        '''
        os.environ['MLFLOW_TRACKING_TOKEN'] = self.client.get_token()
        return f'{get_m3s_api()}/{self.m3s_name}'