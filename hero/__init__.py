import os

from .lib import errors

from .client import HeroClient

def get_env_variable(var_name, default_value=None):
    '''
    Simple method to get an environment variable and tells you if it didn't load with a simple error message.
    '''
    value = os.getenv(var_name, default_value)
    if value is None:
        raise EnvironmentError(f'Required environment variable "{var_name}" is not set.')
    print('environment_variable', var_name, value)
    return value