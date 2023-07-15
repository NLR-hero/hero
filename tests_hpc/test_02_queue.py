import time
import hero as hq

hq.session.get_session()


def test_create_queue():
    """Create virutal queue"""
    project = hq.session.get_project()
    queue = hq.session.get_queue()
    queue_url = hq.queue.create_queue(project, queue)
    hq.dynamo.update_queue_url(project, queue, queue_url)
    hq.queue.delete_other_queues(queue_url, project, queue)

    dynamo_queue_url = hq.dynamo.get_queue_url(project, queue)
    assert dynamo_queue_url == queue_url
