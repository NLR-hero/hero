class UnauthorizedException(Exception):
    pass


class QueueNotActiveException(Exception):
    pass


class QueueDoesNotExistException(Exception):
    pass


class QueueEmptyException(Exception):
    pass


class ItemNotFoundException(Exception):
    pass
