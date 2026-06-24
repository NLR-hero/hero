# urls.py
from types import MappingProxyType
from typing import Dict, Mapping, Literal

Env = Literal["dev", "stage", "production"]

_URL_MAP_COMPONENTS = {
    "dev": {
        "HERO_BASE_URL": "https://dev-hero.nlr.gov",
        "USER_POOL_ID": "BXOYSVgFj",
        "HERO_COGNITO_API_URL": "https://dev-nrel-research.auth.us-west-2.amazoncognito.com/oauth2/token",
    },
    "stage": {
        "HERO_BASE_URL": "https://stage-hero.nlr.gov",
        "USER_POOL_ID": "rDmntXItO",
        "HERO_COGNITO_API_URL": "https://stage-nrel-research.auth.us-west-2.amazoncognito.com/oauth2/token",
    },
    "production": {
        "HERO_BASE_URL": "https://hero.nlr.gov",
        "USER_POOL_ID": "hnq46fXoH",
        "HERO_COGNITO_API_URL": "https://nrel-research.auth.us-west-2.amazoncognito.com/oauth2/token",
    },
    "services": {
        "HERO_AUTH_API_URL": "/auth/api/v1",
        "HERO_DATA_REPO_API_URL": "/data-repo/api/v1",
        "HERO_ML_MODEL_REGISTRY_API_URL": "/ml-model-registry/api/v1",
        "HERO_SEARCH_API_URL": "/search/api/v1",
        "HERO_TASK_ENGINE_API_URL": "/task-engine/api/v1",
    },
}

_composed = {}
for env, comps in _URL_MAP_COMPONENTS.items():
    if env == "services":
        continue
    base = comps["HERO_BASE_URL"].rstrip("/")
    entry = {
        **comps,
        **{
            svc: f"{base}{path}"
            for svc, path in _URL_MAP_COMPONENTS["services"].items()
        },
    }
    _composed[env] = entry

URL_MAP: Mapping[Env, Mapping[str, str]] = MappingProxyType(
    {env: MappingProxyType(d) for env, d in _composed.items()}
)
