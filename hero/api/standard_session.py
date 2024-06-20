import logging
from requests import Session
from ..errors import ApiUnauthorized, ApiQueueDoesNotExist

log = logging.getLogger("hero:auth:cognito")

COGNITO_AUTH_URL = (
    "https://dev-nrel-research.auth.us-west-2.amazoncognito.com/oauth2/token"
)

import urllib3

urllib3.disable_warnings()

class StandardSession(Session):
    """
    An extension of the requests.Session object that adds error handling
    """

    def request(self, method, url, **kwargs):

        r = super(StandardSession, self).request(method, url, **kwargs)

        # if r.status_code in [429, 456, 500, 502, 503, 504, 569, 563]:
        #     # TODO: implement error handling
        #     pass

        # Raise to the client
        if r.status_code == 401:
            if r.json().get("message") == "Unauthorized":
                raise ApiUnauthorized("Unauthorized for this resource")
            raise r.raise_for_status()
        # if r.status_code == 400:
        #     if r.json().get("error") == "Bad Request":
        #         raise ApiQueueDoesNotExist("Queue does not exists")
        #     raise r.raise_for_status()
        # if r.status_code == 404:
            # print(r.json())
            # if r.json().get("error", {}).get("message") == "Item not found.":
            #     raise ApiItemNotFound("Queue not found in Dynamo")
            # raise r.raise_for_status()
        return r
