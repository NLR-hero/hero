import os
import pathlib
import json
import logging

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


def set_hero_env_from_credentials():
    """
    This function will set the HERO environment variables from a file stored in ~/.hero/.credentials.json

    Ensure you have your hero credentials saved in `~/.hero/credentials.json` format.

        {
            "aeroportal-app": {
                "dev": {
                    "HERO_CLIENT_ID": "1c5ngb6o6lvtdfkus0sflstdq4",
                    "HERO_CLIENT_SECRET": "******".
                    "[ANOTHER_KEY]": "***",
                }
            }
        }


    Parameters
    ----------
    None

    Returns
    --------
    response : dict
        The response json object with an event_id
        {
            'metadata': {
                'events': []
            },
            'updatedOn': '2025-01-02T23:25:48.950Z'
        }

    """

    filepath = pathlib.Path(os.environ["HOME"]) / ".hero/credentials.json"
    os.environ["HERO_ENV"] = os.environ.get("HERO_ENV", "dev")
    hero_env = os.environ.get("HERO_ENV")
    hero_project = os.environ.get("HERO_PROJECT", "")

    try:
        credentials = json.loads(open(filepath, "r").read())
        these_credentials = credentials[hero_project][hero_env]
        for key, value in these_credentials.items():
            os.environ[key] = value
    except FileNotFoundError as e:
        log.error(f"Unable to load {filepath}")
    except KeyError as e:
        log.error(f"Unable to read key {e}")
    except Exception:
        log.error(f"Unable to set credentials from {filepath}")
