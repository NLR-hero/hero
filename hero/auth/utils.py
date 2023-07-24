import json
import base64
import logging

log = logging.getLogger('hero:auth:utils')

def parse_token(token):
    """
    A utility function to parse a JWT into JSON.
    """
    token_part = token.split('.')[1]
    padded = token_part + "="*divmod(len(token_part),4)[1]
    return json.loads(base64.urlsafe_b64decode(padded))
