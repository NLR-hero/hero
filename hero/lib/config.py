import os
import pathlib
import json
import logging
import pathlib

log = logging.getLogger("hero:config")


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


def set_environment(application_id, path=None):
    """
    This function will set the HERO environment variables from a file stored in ~/.hero/.credentials.json

    Ensure you have your hero credentials saved in `~/.hero/credentials.json` format.

        {
            "dev-aeroportal": {
                "HERO_CLIENT_ID": "1c5ngb6o6lvtdfkus0sflstdq4",
                "HERO_CLIENT_SECRET": "******",
                "[ANOTHER_KEY]": "***"
            }
        }


    Parameters
    ----------
    application_id: name in the credentials.json file (e.g. dev-aeroportal)

    """
    if path is None:
        path = pathlib.Path(os.environ.get("HOME") / ".hero" / "credentials.json")

    try:
        credentials = json.loads(open(path, "r").read())
        these_credentials = credentials[application_id]
        for key, value in these_credentials.items():
            os.environ[key] = value

    except FileNotFoundError as e:
        log.error(f"Unable to load {path}")
    except KeyError as e:
        log.error(f"Unable to read key {e}")
    except Exception as e:
        log.error(str(e))
        log.error(f"Unable to set credentials from {path}")
