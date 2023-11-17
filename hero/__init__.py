"""
.. include:: ./documentation.md
"""
__version__ = "0.1.4"

import logging
logging.basicConfig(level=logging.INFO)

from . import api
from .auth import cognito
from .client import Hero