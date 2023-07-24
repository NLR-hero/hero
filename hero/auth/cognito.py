import requests
import base64
import logging

log = logging.getLogger('hero:auth:cognito')

COGNITO_AUTH_URL = 'https://dev-nrel-research.auth.us-west-2.amazoncognito.com/oauth2/token'

def get_token(client_id, client_secret, scopes, auth_url=COGNITO_AUTH_URL):
    """
    Login to the Cognito user pool. Requires a client with a client secret and authorization to assign requested scopes.

    Returns a JWT access token.
    """
    app_client_id_secret = f'{client_id}:{client_secret}'.encode('utf-8')
    # Request access_token following client credentials grant flow
    basic_auth = f'Basic {base64.urlsafe_b64encode(app_client_id_secret).decode()}'
    response = requests.post(auth_url,
                                data=f'grant_type=client_credentials&scope={" ".join(scopes)}&client_id={client_id}',
                                headers={
                                    'Authorization': basic_auth,
                                    'Content-Type': 'application/x-www-form-urlencoded'
                                }, verify=False)
    response.raise_for_status()
                
    return response.json()['access_token']