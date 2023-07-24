import pytest
import hero as hq

from testing_environment import HERO_CLIENT_ID, HERO_CLIENT_SECRET, HERO_PROJECT, HERO_QUEUE, HERO_QUEUE_VISIBILITY_TIMEOUT

def test_get_token_from_cognito(access_token):
    claims = hq.auth.utils.parse_token(access_token)

    assert 'sub' in claims
    scopes = claims['scope'].split(' ')
    assert 'hero-api/user' in scopes
    assert f'project/{HERO_PROJECT}' in scopes

def test_assume_role(aws_credentials):
    assert 'AccessKeyId' in aws_credentials
    assert 'SecretAccessKey' in aws_credentials
    assert 'SessionToken' in aws_credentials
    assert 'Expiration' in aws_credentials
