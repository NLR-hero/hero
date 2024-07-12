
import jwt
import base64
from requests import Session
from jwt.exceptions import DecodeError

from .url_map import URL_MAP
from .lib import get_conf_from_collection, get_env, get_client_credentials
from .services import DataRepoService, TaskEngineService, MLModelRegistry

COGNITO_AUTH_URL = get_conf_from_collection(URL_MAP, 'HERO_COGNITO_API_URL')

class HeroClient:
    '''
    Primary client for interfacing with the HERO API. Provides access to all services.
    '''
    def __init__(self):
        '''
        Creates the Hero client.
        '''
        self._scopes = []
        self.env = get_env()
        self.api = Session()
        client_id, client_secret = get_client_credentials()
        self._client_id = client_id
        self._client_secret = client_secret

    def _fetch_token(self):
        '''
        Login to the Cognito user pool. Requires a client with a client secret and authorization to assign requested scopes.

        Returns a JWT access token.
        '''
        app_client_id_secret = f'{self._client_id}:{self._client_secret}'.encode('utf-8')
        # Request access_token following client credentials grant flow
        basic_auth = f'Basic {base64.urlsafe_b64encode(app_client_id_secret).decode()}'

        response = self.api.post(
            COGNITO_AUTH_URL,
            data=f'grant_type=client_credentials&scope={" ".join(self._scopes)}&client_id={self._client_id}',
            headers={
                'Authorization': basic_auth,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            verify=False,
        )

        self._access_token = response.json()['access_token']

    def _decode_token(self, token):
        '''
        Decodes a JWT token and returns the payload, returns None otherwise.
        '''
        try:
            return jwt.decode(token,
                              algorithms=['RS256'],
                              options={'verify_signature': False})
        except DecodeError as e:
            print('Token is not valid')

    def add_scope(self, scope):
        '''
        Adds a scope to the client.
        '''
        self._scopes.append(scope)

    def authenticate(self):
        '''
        Authenticates the client with the Cognito user pool.
        '''
        self._fetch_token()

    def get_token(self):
        '''
        Returns the access token if it is valid.

        Note: we could add re-auth capabilities here Or manage elsewhere
        (i.e. resilient sessions, etc)
        '''
        access_token_decoded = self._decode_token(self._access_token)
        if access_token_decoded:
            return self._access_token

    def DataRepo(self):
        '''
        Returns a DataRepoService instance.
        '''
        return DataRepoService(self)

    def TaskEngine(self):
        '''
        Returns a TaskEngineService instance.
        '''
        return TaskEngineService(self)

    def MLModelRegistry(self, m3s_name):
        '''
        Returns a MLModelRegistry instance.
        '''
        return MLModelRegistry(self, m3s_name)
