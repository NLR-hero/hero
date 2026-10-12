import os
import json

from .errors import HeroConfigurationError, InvalidEnvironmentError


def get_env_variable(var_name, default_value=None):
    """
    Simple method to get an environment variable and tells you if it didn't load with a simple error message.
    """
    value = os.getenv(var_name, default_value)
    if value is None:
        raise EnvironmentError(
            f'Required environment variable "{var_name}" is not set.'
        )
    return value


def load_runtime_config():
    """
    Loads the JSON secret named by SECRET_NAME from AWS Secrets Manager in us-west-2.
    """
    try:
        import boto3
    except ImportError as e:
        raise ImportError(
            "AssistantService requires the optional dependency 'boto3'.\n"
            "Install with: uv add boto3"
        ) from e

    client = boto3.client("secretsmanager", region_name="us-west-2")
    secret_name = os.environ["SECRET_NAME"]
    response = client.get_secret_value(SecretId=secret_name)
    secret_string = response["SecretString"]
    secrets = json.loads(secret_string)

    from ..url_map import ENVIRONMENTS

    if not isinstance(secrets, dict):
        raise HeroConfigurationError(
            f"Secret {secret_name!r} must contain a JSON object."
        )

    hero_env = secrets.get("HERO_ENV")
    if hero_env not in ENVIRONMENTS:
        raise InvalidEnvironmentError(
            hero_env, ENVIRONMENTS, source=f"HERO_ENV in secret {secret_name!r}"
        )

    for key in ("HERO_CLIENT_ID", "HERO_CLIENT_SECRET"):
        value = secrets.get(key)
        if not isinstance(value, str) or not value.strip() or "\0" in value:
            raise HeroConfigurationError(
                f"{key} in secret {secret_name!r} must be a non-empty string "
                "with no null characters."
            )

    os.environ["HERO_CLIENT_ID"] = secrets["HERO_CLIENT_ID"]
    os.environ["HERO_CLIENT_SECRET"] = secrets["HERO_CLIENT_SECRET"]
    os.environ["HERO_ENV"] = hero_env

    return secrets


def load_environment(runtime_config={}):
    """
    Loads the environment used to configure the Hero Client. Use the application_id to setup Hero services.

    Will use runtime_config if provided AND environment variables are not defined. Otherwise environment variables are used first.
    """
    try:
        HERO_ENV = get_env_variable("HERO_ENV", runtime_config.get("HERO_ENV"))
        HERO_PROJECT = get_env_variable(
            "HERO_PROJECT", runtime_config.get("HERO_PROJECT")
        )
        HERO_CLIENT_ID = get_env_variable(
            "HERO_CLIENT_ID", runtime_config.get("HERO_CLIENT_ID")
        )
        HERO_CLIENT_SECRET = get_env_variable(
            "HERO_CLIENT_SECRET", runtime_config.get("HERO_CLIENT_SECRET")
        )

        application_id = f"{HERO_ENV}-{HERO_PROJECT}"
        return application_id
    except EnvironmentError as e:
        print(e)
        exit(1)
