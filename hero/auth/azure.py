TENANT = 'a0f29d7e-28cd-4f54-8442-7885aee7c080'
AZURE_AUTH_URL = f'https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token'

def _get_token_from_azure(client_id, client_secret, scopes, auth_url=AZURE_AUTH_URL):
    '''
    scopes = 'https://graph.microsoft.com/.default'
    '''
    # Request access_token following client credentials grant flow
    response = requests.post(auth_url,
                                data=f'client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials&scope={scopes}',
                                headers={
                                    'Content-Type': 'application/x-www-form-urlencoded'
                                })
    response.raise_for_status()
                
    return response.json()['access_token']