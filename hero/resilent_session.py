import base64
import logging
from requests import Session
import math
import time
from . import errors

log = logging.getLogger("hero:auth:cognito")

COGNITO_AUTH_URL = (
    "https://dev-nrel-research.auth.us-west-2.amazoncognito.com/oauth2/token"
)

import urllib3

urllib3.disable_warnings()


class ResilientSession(Session):
    """
    This class is supposed to retry requests that return temporary errors.
    At this moment it supports: [429, 456, 500, 502, 503, 504, 569, 563]
    """

    def request(self, method, url, **kwargs):

        counter = 0
        max_retries = 10

        # # add random delay, so that not all requests come at once
        # delay_start = np.random.uniform(low=0.0, high=20.0)
        # time.sleep(delay_start)

        while counter < max_retries:
            counter += 1

            r = super(ResilientSession, self).request(method, url, **kwargs)

            if r.status_code in [429, 456, 500, 502, 503, 504, 569, 563]:

                # calculate delay
                delay = (5 * math.pow(2, counter)) * 0.5

                logging.warning(
                    "Got recoverable error [%s]: retry #%s in %ss from %s %s, "
                    % (r.status_code, counter, delay, method, url)
                )
                time.sleep(delay)
                continue

            if r.status_code == 401:
                raise errors.UnauthorizedException(
                    "Hero 401: Unauthorized for this resource"
                )
            if r.status_code == 400:
                raise errors.QueueDoesNotExistException(
                    "Hero 400: Queue does not exists"
                )
            if r.status_code == 404:
                raise errors.ItemNotFoundException(
                    "Hero 404: Queue not found in Dynamo"
                )
            return r
