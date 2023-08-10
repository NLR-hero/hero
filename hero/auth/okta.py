
import logging

log = logging.getLogger('hero:auth:okta')


OKTA_AUTH_URL = 'https://dev-79259981.okta.com/oauth2/default/v1/token'

def _get_token_from_okta(client_id, client_secret, scopes, auth_url=OKTA_AUTH_URL):
    '''
    scopes = 'hero-api/user data-api/user authz-api/user'
    auth_url = 
    '''
    app_client_id_secret = f'{client_id}:{client_secret}'.encode('utf-8')

    # Request access_token following client credentials grant flow
    basic_auth = f'Basic {base64.urlsafe_b64encode(app_client_id_secret).decode()}'
    response = requests.post(auth_url,
                                data=f'grant_type=client_credentials&scope={scopes}',
                                headers={
                                    'Authorization': basic_auth,
                                    'Content-Type': 'application/x-www-form-urlencoded'
                                }, verify=False)
    response.raise_for_status()
                
    return response.json()['access_token']