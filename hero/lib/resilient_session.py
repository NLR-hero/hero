import logging
from requests import Session
import math
import time
import urllib3

log = logging.getLogger("hero:auth:cognito")

urllib3.disable_warnings()


class ResilientSession(Session):
    """
    An extension of the requests.Session object that will retry requests that return temporary/resolvable errors.

    Currently supports the following error codes: [429, 456, 500, 502, 503, 504, 569, 563]
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
