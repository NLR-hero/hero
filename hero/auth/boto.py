import boto3
from .. import config


def get_session(aws_credentials, region_name="us-west-2"):
    """Returns a boto3 session"""
    if aws_credentials is None:
        aws_credentials = config.get_aws_credentials()

    session = boto3.Session(
        region_name=region_name,
        aws_access_key_id=aws_credentials["AccessKeyId"],
        aws_secret_access_key=aws_credentials["SecretAccessKey"],
        aws_session_token=aws_credentials["SessionToken"],
    )
    return session


def get_table(session, table_name):
    """Gets the table opject for table_name"""
    dyn_resource = session.resource("dynamodb")
    table = dyn_resource.Table(table_name)
    table.load()
    return table
