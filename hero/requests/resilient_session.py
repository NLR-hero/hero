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

                print(r.status_code, r.json().get("error"))
                # calculate delay
                delay = (5 * math.pow(2, counter)) * 0.5

                logging.warning(
                    "Got recoverable error [%s]: retry #%s in %ss from %s %s, "
                    % (r.status_code, counter, delay, method, url)
                )
                time.sleep(delay)
                continue

            # Raise to the client
            if r.status_code == 401:
                if r.json().get("message") == "Unauthorized":
                    raise errors.ApiUnauthorized("Unauthorized for this resource")
                raise r.raise_for_status()
            if r.status_code == 400:
                if r.json().get("error") == "Bad Request":
                    raise errors.ApiQueueDoesNotExist("Queue does not exists")
                raise r.raise_for_status()
            if r.status_code == 404:
                # print(r.json())
                # if r.json().get("error", {}).get("message") == "Item not found.":
                #     raise errors.ApiItemNotFound("Queue not found in Dynamo")
                raise r.raise_for_status()
            return r
