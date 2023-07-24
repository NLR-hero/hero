import pytest
import hero as hq

def test_update_queue_url(aws_credentials):
    result = hq.api.queue.update_queue_url('unit-test')
    assert result['queue_url'] == 'unit-test'

def test_get_queue_url(aws_credentials):
    result = hq.api.queue.get_queue_url()
    assert result == 'unit-test'