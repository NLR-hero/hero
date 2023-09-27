"""
.. include:: ./documentation.md
"""
__version__ = "0.0.2"

from time import time

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

import logging
logging.basicConfig(level=logging.INFO)


from . import api
from . import aws
from . import auth
from . import config
from .client import Hero

# def timer(func):
#     """Prints the runtime of the decorated function"""

#     def wrap_func(*args, **kwargs):
#         tic = time()
#         result = func(*args, **kwargs)
#         log.into(f"Function {func.__name__!r} executed in {(time()-tic):.4f}s")
#         return result

#     return wrap_func

