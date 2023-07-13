from time import time
import os
import logging

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger("hero:timer")


def timer(func):
    """Prints the runtime of the decorated function"""

    def wrap_func(*args, **kwargs):
        tic = time()
        result = func(*args, **kwargs)
        log.into(f"Function {func.__name__!r} executed in {(time()-tic):.4f}s")
        return result

    return wrap_func
