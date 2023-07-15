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
    boto3 = hq.session.get_session(aws_credentials)

    request.session.access_token = access_token
    request.session.aws_credentials = aws_credentials
    request.session.boto3 = boto3

def test_get_table(request):
    dynamo = hq.dynamo.Dynamo(request.session.boto3)
    dynamo.get_table('hero-table')

def test_get_queue_url(request):
    dynamo = hq.dynamo.Dynamo(request.session.boto3)
    dynamo.get_queue_url('hero-test-project', 'hero-test-queue')