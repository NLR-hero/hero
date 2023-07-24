import pytest
import hero as hq

def test_get_aws_credentials_is_empty():
    aws_credentials = hq.config.get_aws_credentials()
    assert aws_credentials is None

def test_get_aws_credentials(aws_credentials):
    hq.config.export_session_to_env(aws_credentials)
    aws_credentials = hq.config.get_aws_credentials()
    assert 'AccessKeyId' in aws_credentials
    assert 'SecretAccessKey' in aws_credentials
    assert 'SessionToken' in aws_credentials
