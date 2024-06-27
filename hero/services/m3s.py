import os

from ..url_map import URL_MAP
from ..lib import ServiceBase, get_conf_from_collection

class M3SService(ServiceBase):

    def __init__(self, clientInstance, m3s_name):
        if not m3s_name:
            raise ValueError('m3s_name must be provided')
        self.base_url = get_conf_from_collection(URL_MAP, 'HERO_M3S_TRACKER_URL')
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
        return f'{self.base_url}/{self.m3s_name}'