import pytest
import hero as hq

from testing_environment import HERO_CLIENT_ID, HERO_CLIENT_SECRET, HERO_PROJECT, HERO_QUEUE, HERO_QUEUE_VISIBILITY_TIMEOUT

@pytest.fixture(scope="module")
def aws_session(aws_credentials):
    '''
    Login and create a new Boto3 AWS config.
    '''
    aws_session = hq.aws.utils.get_session(aws_credentials)
    return aws_session

@pytest.fixture(scope="module")
def access_token():
    client_id, client_secret = hq.config.get_client_credentials()
    scopes = ['hero-api/user', f'project/{HERO_PROJECT}']
    access_token = hq.auth.cognito.get_token(client_id=client_id, client_secret=client_secret, scopes=scopes)
    return access_token

@pytest.fixture(scope="module")
def aws_credentials(access_token):
    aws_credentials = hq.api.role.assume_role(access_token)
    hq.config.export_session_to_env(aws_credentials)
    return aws_credentials

@pytest.fixture
def project():
    return HERO_CLIENT_ID

@pytest.fixture
def project():
    return HERO_CLIENT_SECRET

@pytest.fixture
def project():
    return HERO_PROJECT

@pytest.fixture
def project():
    return HERO_QUEUE

@pytest.fixture
def project():
    return HERO_QUEUE_VISIBILITY_TIMEOUT