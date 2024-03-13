import base64
import logging
import os

from ..resilient_session import ResilientSession
from ..config import get_cognito_api

COGNITO_AUTH_URL = get_cognito_api()


def get_token(client_id, client_secret, scopes):
    """
    Login to the Cognito user pool. Requires a client with a client secret and authorization to assign requested scopes.

    Returns a JWT access token.
    """
    app_client_id_secret = f"{client_id}:{client_secret}".encode("utf-8")
    # Request access_token following client credentials grant flow
    basic_auth = f"Basic {base64.urlsafe_b64encode(app_client_id_secret).decode()}"

    s = ResilientSession()
    response = s.post(
        COGNITO_AUTH_URL,
        data=f'grant_type=client_credentials&scope={" ".join(scopes)}&client_id={client_id}',
        headers={
            "Authorization": basic_auth,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        verify=False,
    )
    response.raise_for_status()

    return response.json()["access_token"]
