import pytest
import uuid
import hero as hq
from botocore.exceptions import ClientError

def test__():
    pass

@pytest.fixture
def queue_name(project, queue):
    return f'hero-{project}-{queue}-{uuid.uuid4()}'

@pytest.fixture
def queue_url(aws_session, queue_name, visibility_timeout):
    result = hq.aws.sqs.create_queue(aws_session, queue_name, visibility_timeout)
    yield result['QueueUrl']
    hq.aws.sqs.delete_queue(aws_session, result['QueueUrl'])

def test_sqs(aws_session, queue_name, visibility_timeout):
    result = hq.aws.sqs.create_queue(aws_session, queue_name, visibility_timeout)
    assert 'QueueUrl' in result

    queue_url = hq.aws.sqs.get_queue_url(aws_session, queue_name)
    assert queue_name in queue_url

    hq.aws.sqs.delete_queue(aws_session, result['QueueUrl'])

    queue_url = hq.aws.sqs.get_queue_url(aws_session, queue_url)
    assert queue_url is None

    try:
        message = hq.aws.sqs.receive_messages(aws_session, result['QueueUrl'])
        assert len(message) == 0
    except ClientError as e:
        assert e.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue"

def test_receive_messages(aws_session, queue_url):
    message = hq.aws.sqs.receive_messages(aws_session, queue_url)
    assert len(message) == 0