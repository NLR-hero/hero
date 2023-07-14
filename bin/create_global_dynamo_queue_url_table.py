import boto3
import logging
import hero as hq

hq.session.get_session()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    logger.info("Creating DynamoDB table")
    client = boto3.client('dynamodb')
    response = client.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'project_name',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'queue_prefix',
                'AttributeType': 'S'
            },
        ],
        TableName='hero-dynamodb-project-queue-names',
        KeySchema=[
            {
                'AttributeName': 'project_name',
                'KeyType': 'HASH'
            },
        {
                'AttributeName': 'queue_prefix',
                'KeyType': 'RANGE'
            },
        ],
        BillingMode='PAY_PER_REQUEST',
        StreamSpecification={
            'StreamEnabled': False,
        },
        SSESpecification={
            'Enabled': False,
        },
        Tags=[
            {
                'Key': 'string',
                'Value': 'string'
            },
        ],
        TableClass='STANDARD',
        DeletionProtectionEnabled=False
    )

    logger.info("Waiting for table to be created")
    logger.info("Table created")
    logger.info(response)
