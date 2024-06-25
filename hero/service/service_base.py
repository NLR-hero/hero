from .. import config
from .. import auth

class ServiceBase:
    def __init__(self, clientInstance):
        self.client = clientInstance
        self._configure()
        self._login()
        self._after_init()

    def _configure(self):
        return None

    def _login(self):
        """This method should not have a @retry_method decorator"""
        client_id, client_secret = config.get_client_credentials()
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token = auth.cognito.get_token(
            self.api,
            client_id=self._client_id,
            client_secret=self._client_secret,
            scopes=self._scopes,
        )

    def _after_init(self):
        return None
