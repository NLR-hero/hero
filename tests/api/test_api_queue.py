import pytest
import hero as hq

def test_update_queue_url(aws_credentials):
    result = hq.api.queue.update_queue_url('unit-test')
    assert result['queue_url'] == 'unit-test'

def test_get_queue_url(aws_credentials):
    result = hq.api.queue.get_queue_url()
    assert result == 'unit-test'

import pytest
import hero as hq

from testing_environment import HERO_CLIENT_ID, HERO_CLIENT_SECRET, HERO_PROJECT, HERO_QUEUE, HERO_QUEUE_VISIBILITY_TIMEOUT

@pytest.fixture
def queue_url(aws_session):
    '''
    @param aws_session Fixture provided authenticated AWS session
    '''
    queue_url = hq.queue.create_queue(aws_session, HERO_PROJECT, 'unit-test-000')
    yield queue_url
    hq.queue.delete_queue(aws_session, queue_url)

@pytest.fixture
def queue_urls(aws_session):
    """
    Create several queues with the same prefix.
    """
    queue_url_1a = hq.queue.create_queue(aws_session, HERO_PROJECT, 'unit-test-001')
    queue_url_1b = hq.queue.create_queue(aws_session, HERO_PROJECT, 'unit-test-001')
    queues = list(hq.queue.list_queues(aws_session, HERO_PROJECT, 'unit-test-001'))
    yield queues
    hq.queue.delete_queue(aws_session, queue_url_1a)
    hq.queue.delete_queue(aws_session, queue_url_1b)


def test_create_queue(queue_url):
    assert 'hero-test-project-2-unit-test-000' in queue_url

def test_list_queues(queue_urls):
    assert len(queue_urls) == 2

def test_delete_queue(aws_session):
    queue_url = hq.queue.create_queue(aws_session, HERO_PROJECT, 'unit-test-002')
    # Make sure we have a queue to delete
    assert 'hero-test-project-2-unit-test-002' in queue_url
    hq.queue.delete_queue(aws_session, queue_url)
    queues = list(hq.queue.list_queues(aws_session, HERO_PROJECT, 'unit-test-002'))
    assert len(queues) == 0

def test_delete_other_queues():
    assert True

def test_receive_messages():
    assert True

def test_delete_message():
    assert True
