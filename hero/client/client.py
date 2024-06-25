from requests import Session
import base64
import jwt
from jwt.exceptions import DecodeError

from ..config import get_client_credentials, get_cognito_api, get_client_scopes
from ..services import DataRepoService, TaskEngineService, M3SService

COGNITO_AUTH_URL = get_cognito_api()

class HeroClient:
    '''
    Primary client for interfacing with the HERO API. Provides access to all services.
    '''
    def __init__(self):
        '''
        Initializes the client and logs in.
        '''
        self.session = Session()
        self._login()

    def _login(self):
        '''
        Kicks off the login process by fetching a token.
        '''
        client_id, client_secret = get_client_credentials()
        self._client_id = client_id
        self._client_secret = client_secret
        self._scopes = get_client_scopes()
        self.fetch_token(
            client_id=self._client_id,
            client_secret=self._client_secret,
            scopes=self._scopes,
        )

    def fetch_token(self, client_id, client_secret, scopes):
        '''
        Login to the Cognito user pool. Requires a client with a client secret and authorization to assign requested scopes.

        Returns a JWT access token.
        '''
        app_client_id_secret = f'{client_id}:{client_secret}'.encode('utf-8')
        # Request access_token following client credentials grant flow
        basic_auth = f'Basic {base64.urlsafe_b64encode(app_client_id_secret).decode()}'

        response = self.session.post(
            COGNITO_AUTH_URL,
            data=f'grant_type=client_credentials&scope={" ".join(scopes)}&client_id={client_id}',
            headers={
                'Authorization': basic_auth,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            verify=False,
        )

        self._access_token = response.json()['access_token']

    def decode_token(self, token):
        '''
        Decodes a JWT token and returns the payload, returns None otherwise.
        '''
        try:
            return jwt.decode(token,
                              algorithms=['RS256'],
                              options={'verify_signature': False})
        except DecodeError as e:
            print('Token is not valid')

    def get_token(self):
        '''
        Returns the access token if it is valid.

        Note: we could add re-auth capabilities here Or manage elsewhere
        (i.e. resilient sessions, etc)
        '''
        access_token_decoded = self.decode_token(self._access_token)
        if access_token_decoded:
            return self._access_token

    def DataRepo(self):
        '''
        Returns a DataRepoService instance.
        '''
        return DataRepoService(self)

    def TaskEngine(self, queue_name):
        '''
        Returns a TaskEngineService instance.
        '''
        return TaskEngineService(self, queue_name)

    def M3S(self, m3s_name):
        '''
        Returns a M3SService instance.
        '''
        return M3SService(self, m3s_name)
