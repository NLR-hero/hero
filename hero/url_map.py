# urls.py
from types import MappingProxyType
from typing import Dict, Mapping, Literal
import jwt

Env = Literal["dev", "stage", "production"]
Pool = Literal["PRIMARY", "LEGACY"]

_URL_MAP_COMPONENTS = {
    "dev": {
        "HERO_BASE_URL": "https://dev-hero.nlr.gov",
        "LEGACY": {
            "USER_POOL_ID": "BXOYSVgFj",
            "HERO_COGNITO_API_URL": "https://dev-nrel-research.auth.us-west-2.amazoncognito.com/oauth2/token"
        },
        "PRIMARY": {
            "USER_POOL_ID": "zBKhkMi3I",
            "HERO_COGNITO_API_URL": "https://dev-hero.auth.us-west-2.amazoncognito.com/oauth2/token"
        }
    },
    "stage": {
        "HERO_BASE_URL": "https://stage-hero.nlr.gov",
        "LEGACY": {
            "USER_POOL_ID": "rDmntXItO",
            "HERO_COGNITO_API_URL": "https://stage-nrel-research.auth.us-west-2.amazoncognito.com/oauth2/token"
        },
        "PRIMARY": {
            "USER_POOL_ID": "cCY62Xb2M",
            "HERO_COGNITO_API_URL": "https://stage-hero.auth.us-west-2.amazoncognito.com/oauth2/token"
        }
    },
    "production": {
        "HERO_BASE_URL": "https://hero.nlr.gov",
        "LEGACY": {
            "USER_POOL_ID": "hnq46fXoH",
            "HERO_COGNITO_API_URL": "https://nrel-research.auth.us-west-2.amazoncognito.com/oauth2/token",
        },
        "PRIMARY": {
            "USER_POOL_ID": "he2tr0gJz",
            "HERO_COGNITO_API_URL": "https://aura.auth.us-west-2.amazoncognito.com/oauth2/token",
        }
    },
    "services": {
        "HERO_AUTH_API_URL": "/auth/api/v1",
        "HERO_DATA_REPO_API_URL": "/data-repo/api/v1",
        "HERO_ML_MODEL_REGISTRY_API_URL": "/ml-model-registry/api/v1",
        "HERO_SEARCH_API_URL": "/search/api/v1",
        "HERO_TASK_ENGINE_API_URL": "/task-engine/api/v1",
    },
}

_POOL_ID_TO_POOL: dict[str, dict[str, Pool]] = {}
for _env, _comps in _URL_MAP_COMPONENTS.items():
    if _env == "services":
        continue
    for _pool in ("LEGACY", "PRIMARY"):
        pool_id = _comps[_pool]["USER_POOL_ID"]
        if _env not in _POOL_ID_TO_POOL:
            _POOL_ID_TO_POOL[_env] = {}
        _POOL_ID_TO_POOL[_env][pool_id] = _pool

_DEFAULT_POOL: Pool = "PRIMARY" 

_composed = {}
for env, comps in _URL_MAP_COMPONENTS.items():
    if env == "services":
        continue
    base = comps["HERO_BASE_URL"].rstrip("/")
    entry = {
        "HERO_BASE_URL": base,
        **comps[_DEFAULT_POOL],
        "LEGACY": comps["LEGACY"],
        "PRIMARY": comps["PRIMARY"],
        **{
            svc: f"{base}{path}"
            for svc, path in _URL_MAP_COMPONENTS["services"].items()
        },
    }
    _composed[env] = entry

URL_MAP: Mapping[Env, Mapping[str, str]] = MappingProxyType(
    {env: MappingProxyType(d) for env, d in _composed.items()}
)

def get_pool_config(env: Env, pool: Pool) -> Mapping[str, str]:
    """Get the USER_POOL_ID and HERO_COGNITO_API_URL for a specific pool."""
    return _URL_MAP_COMPONENTS[env][pool]

def detect_pool_from_token(env: Env, token: str) -> Pool:
    """Detect which pool a JWT was issued from by inspecting its 'iss' claim."""
    unverified = jwt.decode(token, algorithms=["RS256"], options={"verify_signature": False})
    iss = unverified.get("iss", "")
    pool_id = iss.rsplit("_", 1)[-1] if "_" in iss else ""
    return _POOL_ID_TO_POOL.get(env, {}).get(pool_id, _DEFAULT_POOL)
