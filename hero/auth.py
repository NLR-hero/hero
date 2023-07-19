"""
Authentication is centrally managed by Amazon Cognito. Authorization depends on what you access and how you get to it. For direct access to AWS via boto3, AWS credentials are required. For access to the Hero API you will need the correct groups and scopes set in the Cognito User Pool.

Either way you access Hero, you will first need to sign into the user pool. For machine-to-machine auth, we follow the client creentials grant flow. You will need a CLIENT_ID, CLIENT_SECRET, and list of scopes.

To request a new app client with client id and client secret, contact us.

Scopes are used to grant access to specific API resources. Each scope follows a similar structure `<RESOURCE>/<THING>`, e.g. `hero-api/user` or `project/example`. These roles are request when you authenticate. For example:

```python
client_id = "MY_CLIENT_ID"
client_secret = "MY_CLIENT_SECRET"
scopes = ['hero-api/user', f'project/example']
access_token = hq.auth.get_token_from_cognito(client_id=client_id, client_secret=client_secret, scopes=scopes)
```

This generates a JWT access token which can be used to access Hero APIs or exchanged for to assume a specific IAM role. To assume an IAM role and use boto3 run:

```python
aws_credentials = hq.auth.assume_role(access_token)
```

Here, `aws_credentials` are your access keys to AWS. Use them as you would typically use AWS access keys.

"""

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

def parse_token(token):
    """
    A utility function to parse a JWT into JSON.
    """
    token_part = token.split('.')[1]
    padded = token_part + "="*divmod(len(token_part),4)[1]
    return json.loads(base64.urlsafe_b64decode(padded))



def assume_role(token):
    """
    Returns AWS credentials from the Hero API. Use this to assume an IAM role.
    """
    endpoint = f'{API_URL}/hero/api/v2/role'
    response = requests.get(endpoint,
        headers={
            'Authorization': f'Bearer {token}'
        },
        verify=False)
    return response.json()