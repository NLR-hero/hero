from . import api
from . import aws
from . import auth
from . import config
from .timer import timer
from .hero import Hero

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

import logging
logging.basicConfig(level=logging.INFO)
