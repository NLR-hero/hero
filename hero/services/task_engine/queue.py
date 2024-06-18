class Queue:

    def __init__(self, queue):
        self._id = queue["id"]
        self._queue = queue

    @property
    def queue_id(self):
        return self._id
