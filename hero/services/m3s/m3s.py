import os

from ...service import ServiceBase
from ... import errors
from ...api import ApiBase

from ...config import get_m3s_id, get_m3s_scopes

class M3S(ServiceBase):

    def __init__(self, queue_name):
        self._queue_name = queue_name
        self._queue = None
        super().__init__()

    def _configure(self):
        self.api = ApiBase() #used for auth, base is adequate for this
        self._m3s_id = get_m3s_id() #not used, do we need this?
        self._scopes = get_m3s_scopes()

    def _after_init(self):
        self.set_mlflow_tracking_token(self._access_token)

    def set_mlflow_tracking_token(token=None):
        """Sets the MLFlow tracking token in the environment"""
        os.environ['MLFLOW_TRACKING_TOKEN'] = token

    # Don't think we need this, but if so, it should probably live in 'auth'
    # def get_session(token, session_url):
    #     """
    #     Get a session token from the IAM session URL using the provided access token.
    #     """
    #     # Request access_token following client credentials grant flow
    #     bearer_auth = f'Bearer {token}'

    #     s = ResilientSession()
    #     print(session_url)
    #     print(bearer_auth)

    #     response = s.get(session_url,
    #                     headers={
    #                         'Authorization': bearer_auth,
    #                         'Content-Type': 'application/x-www-form-urlencoded'
    #                     }, verify=False)
    #     response.raise_for_status()

    #     return response.json()

    # def set_iam_session_data(roleRes):
    #     """Sets the IAM session data in the environment"""
    #     os.environ['AWS_ACCESS_KEY_ID'] = roleRes['AccessKeyId']
    #     os.environ['AWS_SECRET_ACCESS_KEY'] = roleRes['SecretAccessKey']
    #     os.environ['AWS_SESSION_TOKEN'] = roleRes['SessionToken']
