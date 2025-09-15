import jwt
import base64
from requests import Session
from jwt import (
    PyJWKClient,
    ExpiredSignatureError,
    InvalidTokenError,
    InvalidSignatureError,
    DecodeError,
)

from .url_map import URL_MAP
from .lib import (
    get_conf_from_collection,
    get_env,
    get_client_credentials,
)
from .services import AuthService, DataRepoService, TaskEngineService, MLModelRegistry
from .services import SearchService

from .lib.errors import (
    TokenDecodeError,
    TokenInvalidSignatureError,
    TokenInvalidError,
    TokenGeneralError,
)


class HeroClient:
    """
    Primary client for interfacing with the HERO API. Provides access to all services.
    """

    def __init__(self):
        """
        Creates the Hero client.
        """
        self._scopes = []

        self.env = get_env()
        self.api = Session()
        region = "us-west-2"
        client_id, client_secret = get_client_credentials()

        self._client_id = client_id
        self._client_secret = client_secret
        self._cognito_api_url = get_conf_from_collection(
            URL_MAP, "HERO_COGNITO_API_URL"
        )
        self._cognito_user_pool_id = get_conf_from_collection(URL_MAP, "USER_POOL_ID")
        self._cognito_auth_url = f"https://cognito-idp.{region}.amazonaws.com/{region}_{self._cognito_user_pool_id}"
        self._jwks_url = f"{self._cognito_auth_url}/.well-known/jwks.json"
        self._jwk_client = PyJWKClient(self._jwks_url)
        self._access_token = None

    def _fetch_token(self):
        """
        Login to the Cognito user pool. Requires a client with a client secret and authorization to assign requested scopes.

        Returns a JWT access token.
        """
        app_client_id_secret = f"{self._client_id}:{self._client_secret}".encode(
            "utf-8"
        )
        # Request access_token following client credentials grant flow
        basic_auth = f"Basic {base64.urlsafe_b64encode(app_client_id_secret).decode()}"

        response = self.api.post(
            self._cognito_api_url,
            data=f'grant_type=client_credentials&scope={" ".join(self._scopes)}&client_id={self._client_id}',
            headers={
                "Authorization": basic_auth,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            verify=False,
        )

        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch access token: {response.status_code} - {response.text}, {self._scopes}"
            )

        self._access_token = response.json()["access_token"]

    def _decode_token(self, token):
        """
        Decodes a JWT token and returns the payload, verifying its signature and expiration.

        Raises TokenInvalidSignatureError if the signature is invalid.
        Raises TokenDecodeError if the token is malformed.
        Raises TokenInvalidError if the token is invalid.
        Raises TokenGeneralError for any other unexpected errors.
        """
        try:
            signing_key = self._jwk_client.get_signing_key_from_jwt(token).key
            # Token is valid and not expired
            return jwt.decode(
                token,
                key=signing_key,
                algorithms=["RS256"],
                options={"verify_exp": True, "verify_iat": False},
            )
        except ExpiredSignatureError:
            # token expired, we need to refresh it
            self._fetch_token()
            # try to decode again
            return jwt.decode(
                token, algorithms=["RS256"], options={"verify_signature": False}
            )
        except InvalidSignatureError:
            # The signature doesn't match — token could be tampered with
            raise TokenInvalidSignatureError("Invalid token signature")
        except DecodeError:
            # Token is malformed (e.g., bad base64, wrong structure)
            raise TokenDecodeError("Malformed token")
        except InvalidTokenError as e:
            # Other invalid token cases
            raise TokenInvalidError(f"Invalid token: {str(e)}")
        except Exception as e:
            # Any other unexpected errors
            raise TokenGeneralError("Unexpected error")

    def add_scope(self, scope):
        """
        Adds a scope to the client.
        """
        if scope in self._scopes:
            return
        self._scopes.append(scope)

    def authenticate(self):
        """
        Authenticates the client with the Cognito user pool.
        """
        self._fetch_token()

    def get_token(self):
        """
        Returns the access token if it is valid.

        Note: we could add re-auth capabilities here Or manage elsewhere
        (i.e. resilient sessions, etc)
        """
        access_token_decoded = self._decode_token(self._access_token)
        if access_token_decoded:
            return self._access_token
        else:
            self._fetch_token()
            return self._access_token

    def Auth(self):
        """
        Returns a AuthService instance.
        """
        return AuthService(self)

    def DataRepo(self, application_id=None):
        """
        Returns a DataRepoService instance.
        """
        return DataRepoService(self, application_id)

    def TaskEngine(self, application_id=None):
        """
        Returns a TaskEngineService instance.
        """
        return TaskEngineService(self, application_id)

    def MLModelRegistry(self, application_id=None):
        """
        Returns a MLModelRegistry instance.
        """
        self.authInstance = self.Auth()
        return MLModelRegistry(self, application_id)

    def Search(self):
        """
        Returns a SearchService instance.
        """
        return SearchService(self)
