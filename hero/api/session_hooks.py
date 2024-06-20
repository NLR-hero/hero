from requests import HTTPError
import logging

logger = logging.getLogger('hero:api:session')


def log_request(resp, *args, **kwargs):
    logger.debug('Request %s', resp.request.url)
    logger.debug('Request headers %s', resp.request.headers)
    logger.debug('Request body %s', resp.request.body)


def check_for_errors(resp, *args, **kwargs):
    try:
        resp.raise_for_status()
    except HTTPError:
        logger.error('Received error %s', resp.text)
        raise
    else:
        logger.debug('Received response %s', resp.text)