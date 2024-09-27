from requests import HTTPError
import logging

logger = logging.getLogger("hero:api")


def log_request(resp, *args, **kwargs):
    """
    Log the request object

    Note: This function should be used as a hook in a request session
    """
    logger.debug("Request %s", resp.request.url)
    logger.debug("Request headers %s", resp.request.headers)
    logger.debug("Request body %s", resp.request.body)


def check_for_errors(resp, *args, **kwargs):
    """
    Check for errors in the response.
    This implementation is fairly naive and only checks for HTTP errors..

    Note: This function should be used as a hook in a request session
    """
    try:
        resp.raise_for_status()
    except HTTPError:
        logger.debug("Received error %s", resp.text)
        raise
    else:
        logger.debug("Received response %s", resp.text)
