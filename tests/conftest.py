import pytest
import hero as hq

from testing_environment import HERO_CLIENT_ID, HERO_CLIENT_SECRET, HERO_PROJECT, HERO_QUEUE, HERO_QUEUE_VISIBILITY_TIMEOUT

@pytest.fixture(scope="module")
def aws_session(aws_credentials):
    '''
    Login and create a new Boto3 AWS session.
    '''
    aws_session = hq.session.get_session(aws_credentials)
    return aws_session

@pytest.fixture(scope="module")
def access_token():
    client_id, client_secret = hq.session.get_client_credentials()
    scopes = ['hero-api/user', f'project/{HERO_PROJECT}']
    access_token = hq.auth.get_token_from_cognito(client_id=client_id, client_secret=client_secret, scopes=scopes)
    return access_token

@pytest.fixture(scope="module")
def aws_credentials(access_token):
    aws_credentials = hq.auth.assume_role(access_token)
    return aws_credentials