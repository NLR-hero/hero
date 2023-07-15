import requests
import boto3
import base64
import json
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

API_URL = 'https://dev-hero-api.stratus.nrel.gov'
COGNITO_AUTH_URL = 'https://dev-nrel-research.auth.us-west-2.amazoncognito.com/oauth2/token'
TENANT = 'a0f29d7e-28cd-4f54-8442-7885aee7c080'
AZURE_AUTH_URL = f'https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token'
OKTA_AUTH_URL = 'https://dev-79259981.okta.com/oauth2/default/v1/token'

def get_token_from_cognito(client_id, client_secret, scopes, auth_url=COGNITO_AUTH_URL):
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

def get_token_from_azure(client_id, client_secret, scopes, auth_url=AZURE_AUTH_URL):
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

def get_token_from_okta(client_id, client_secret, scopes, auth_url=OKTA_AUTH_URL):
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

def parse_token(token):
    token_part = token.split('.')[1]
    padded = token_part + "="*divmod(len(token_part),4)[1]
    return json.loads(base64.urlsafe_b64decode(padded))



def assume_role(token):
    endpoint = f'{API_URL}/hero/api/v2/role'
    response = requests.get(endpoint,
        headers={
            'Authorization': f'Bearer {token}'
        },
        verify=False)
    return response.json()