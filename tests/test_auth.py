import pytest
import hero as hq
import os

from testing_environment import HERO_CLIENT_ID, HERO_CLIENT_SECRET, HERO_PROJECT, HERO_QUEUE, HERO_QUEUE_VISIBILITY_TIMEOUT

@pytest.fixture(scope="session", autouse=True)
def setup_login(request):
    client_id, client_secret = hq.session.get_client_credentials()
    scopes = ['hero-api/user']
    access_token = hq.auth.get_token_from_cognito(client_id=client_id, client_secret=client_secret, scopes=scopes)
    aws_credentials = hq.auth.assume_role(access_token)

    #HACK: there is a better way to do this, like set the creds in the boto session,
    # but the session isn't expsed to the libraries that interact with aws

    request.session.access_token = access_token
    request.session.aws_credentials = aws_credentials

def test_get_token_from_cognito(request):
    access_token = request.session.access_token

    claims = hq.auth.parse_token(access_token)

    assert 'sub' in claims
    assert claims['scope'] == "hero-api/user"

def test_assume_role(request):
    aws_credentials = request.session.aws_credentials

    assert 'AccessKeyId' in aws_credentials
    assert 'SecretAccessKey' in aws_credentials
    assert 'SessionToken' in aws_credentials
    assert 'Expiration' in aws_credentials

def test_set_aws_credentials_in_environment():
    assert os.environ['AWS_ACCESS_KEY_ID'] is not None
