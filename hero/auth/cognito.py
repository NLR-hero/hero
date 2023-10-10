import requests
import base64
import logging

from requests import Session
from requests.adapters import HTTPAdapter, Retry

import numpy as np
import math
import time


log = logging.getLogger('hero:auth:cognito')

COGNITO_AUTH_URL = 'https://dev-nrel-research.auth.us-west-2.amazoncognito.com/oauth2/token'

class ResilientSession(Session):
    """
    This class is supposed to retry requests that return temporary errors.
    At this moment it supports: 401, 429, 502, 503, 504
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
                delay0 = 5*math.pow(2, counter)

                # add some randomness

                # effective delay
                delay = 0.5*(delay0 + delay1)

                logging.warn("Got recoverable error [%s]: retry #%s in %ss from %s %s, " % (r.status_code, counter, delay, method, url ))
                time.sleep(delay)
                continue

            return r


def get_token(client_id, client_secret, scopes, auth_url=COGNITO_AUTH_URL):
    """
    Login to the Cognito user pool. Requires a client with a client secret and authorization to assign requested scopes.

    Returns a JWT access token.
    """
    app_client_id_secret = f'{client_id}:{client_secret}'.encode('utf-8')
    # Request access_token following client credentials grant flow
    basic_auth = f'Basic {base64.urlsafe_b64encode(app_client_id_secret).decode()}'

    s = ResilientSession()
    response = s.post(auth_url,
                                data=f'grant_type=client_credentials&scope={" ".join(scopes)}&client_id={client_id}',
                                headers={
                                    'Authorization': basic_auth,
                                    'Content-Type': 'application/x-www-form-urlencoded'
                                }, verify=False)
    response.raise_for_status()
                
    return response.json()['access_token']

