import requests
import logging

from ..auth.cognito import ResilientSession

log = logging.getLogger('hero:api:role')

API_URL = 'https://dev-hero-api.stratus.nrel.gov'

def assume_role(token):
    """
    Returns AWS credentials from the Hero API. Use this to assume an IAM role.
    """
    endpoint = f'{API_URL}/hero/api/v2/role'
    s = ResilientSession()
    response = s.get(endpoint,
        headers={
            'Authorization': f'Bearer {token}'
        },
        verify=False)
    return response.json()