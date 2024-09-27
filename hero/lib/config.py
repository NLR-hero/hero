import os


def get_env():
    return os.environ.get("HERO_ENV", "dev")


def get_service_id(key):
    env = get_env()
    return f"{env}-{os.environ[key]}"


def get_conf_from_collection(collection, key):
    return os.environ.get(key, collection[get_env()][key])


def get_resilient_session():
    return os.environ.get("HERO_RESILIENT_SESSION", "False").lower() in ("true")


def get_client_credentials():
    """Returns the client credentials tuple (client_id, client_secret) from the environment variables HERO_CLIENT_ID and HERO_CLIENT_SECRET"""
    client_credentials = (
        os.environ["HERO_CLIENT_ID"],
        os.environ["HERO_CLIENT_SECRET"],
    )
    return client_credentials
