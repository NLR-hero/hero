from requests import Session
import base64

from ..config import get_client_credentials, get_cognito_api

from ..services import DataRepoService, TaskEngineService, M3SService

COGNITO_AUTH_URL = get_cognito_api()

class HeroClient:
    def __init__(self):
        self.session = Session()
        self._login()

    def _login(self):
        client_id, client_secret = get_client_credentials()
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token = self.get_token(
            self.api,
            client_id=self._client_id,
            client_secret=self._client_secret,
            scopes=self._scopes,
        )

    def get_token(self, client_id, client_secret, scopes):
        """
        Login to the Cognito user pool. Requires a client with a client secret and authorization to assign requested scopes.

        Returns a JWT access token.
        """
        app_client_id_secret = f"{client_id}:{client_secret}".encode("utf-8")
        # Request access_token following client credentials grant flow
        basic_auth = f"Basic {base64.urlsafe_b64encode(app_client_id_secret).decode()}"

        response = self.session.post(
            COGNITO_AUTH_URL,
            data=f'grant_type=client_credentials&scope={" ".join(scopes)}&client_id={client_id}',
            headers={
                "Authorization": basic_auth,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            verify=False,
        )

        return response.json()["access_token"]

    def DataRepo(self):
        return DataRepoService(self)

    def TaskEngine(self, queue_name):
        return TaskEngineService(self, queue_name)

    def M3S(self):
        return M3SService(self)
