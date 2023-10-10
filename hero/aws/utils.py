import boto3
import logging
from .. import config

log = logging.getLogger(__name__)

def get_session(aws_credentials=None, region_name='us-west-2'):
    """Returns a boto3 session"""
    if aws_credentials is None:
        aws_credentials = config.config.get_aws_credentials()
    if aws_credentials is not None:
        session = boto3.Session(
            region_name=region_name,
            aws_access_key_id=aws_credentials['AccessKeyId'],
            aws_secret_access_key=aws_credentials['SecretAccessKey'],
            aws_session_token=aws_credentials['SessionToken']
        )
        return session
    return None