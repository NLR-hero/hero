import os


from collections import OrderedDict


def get_environment():
    tmp = OrderedDict()
    tmp["HERO_ENV"] = os.environ.get("HERO_ENV", "dev")
    tmp["HERO_PROJECT"] = os.environ.get("HERO_PROJECT")
    tmp["HERO_CLIENT_ID"] = os.environ.get("HERO_CLIENT_ID")
    tmp["HERO_CLIENT_SECRET"] = os.environ.get("HERO_CLIENT_SECRET")
    tmp["HERO_TASK_ENGINE_API_URL"] = os.environ.get("HERO_TASK_ENGINE_API_URL")
    tmp["HERO_DATA_REPO_API"] = os.environ.get("HERO_DATA_REPO_API")
    tmp["AWS_ACCESS_KEY_ID"] = os.environ.get("AWS_ACCESS_KEY_ID")
    tmp["AWS_SECRET_ACCESS_KEY"] = os.environ.get("AWS_SECRET_ACCESS_KEY")
    tmp["AWS_SESSION_TOKEN"] = os.environ.get("AWS_SESSION_TOKEN")
    return tmp


def get_client_credentials():
    """Returns the client credentials tuple (client_id, client_secret) from the environment variables HERO_CLIENT_ID and HERO_CLIENT_SECRET"""
    client_credentials = (
        os.environ["HERO_CLIENT_ID"],
        os.environ["HERO_CLIENT_SECRET"],
    )
    return client_credentials


def get_project():
    """Get the project from the environment"""
    return os.environ["HERO_PROJECT"]


def get_task_engine_id():
    env = os.environ.get("HERO_ENV", "dev")
    return f"{env}-{os.environ['HERO_PROJECT']}"


def get_task_engine_scopes():
    return ["task-engine/user"]


def get_data_repo_id():
    env = os.environ.get("HERO_ENV", "dev")
    return f"{env}-{os.environ['HERO_PROJECT']}"


def get_data_repo_scopes():
    return ["data-repo/user"]


def get_task_engine_api():
    defined = os.environ.get("HERO_TASK_ENGINE_API_URL")
    if defined is not None:
        return defined
    env = os.environ.get("HERO_ENV", "dev")
    return f"https://{env}-HERO-TASK-ENGINE"


def get_data_repo_api():
    defined = os.environ["HERO_DATA_REPO_API_URL"]
    if defined is not None:
        return defined
    env = os.environ.get("HERO_ENV", "dev")
    return f"https://{env}-HERO-DATA-REPO"
