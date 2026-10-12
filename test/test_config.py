import json
import os
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from hero.lib.config import get_conf_from_collection, get_env
from hero.lib.errors import (
    HeroConfigurationError,
    InvalidEnvironmentError,
    InvalidPoolError,
    MissingConfigurationError,
)
from hero.lib.loaders import load_runtime_config
from hero.url_map import ENVIRONMENTS, POOLS, URL_MAP, get_pool_config


@pytest.fixture(autouse=True)
def config_environment(monkeypatch):
    monkeypatch.setenv("HERO_ENV", "dev")
    monkeypatch.delenv("TEST_CONFIG_VALUE", raising=False)


def test_default_environment(monkeypatch):
    monkeypatch.delenv("HERO_ENV")
    assert get_env() == "dev"


@pytest.mark.parametrize("env", ENVIRONMENTS)
def test_supported_environment(monkeypatch, env):
    monkeypatch.setenv("HERO_ENV", env)
    assert get_env() == env
    assert (
        get_conf_from_collection(
            {env: {"TEST_CONFIG_VALUE": "value"}}, "TEST_CONFIG_VALUE"
        )
        == "value"
    )


@pytest.mark.parametrize("env", ["", "stag", "services"])
def test_invalid_environment(monkeypatch, env):
    monkeypatch.setenv("HERO_ENV", env)
    with pytest.raises(InvalidEnvironmentError) as caught:
        get_env()
    assert isinstance(caught.value, HeroConfigurationError)
    assert caught.value.env == env
    assert caught.value.valid_environments == ENVIRONMENTS
    assert "HERO_ENV environment variable" in str(caught.value)
    if env == "stag":
        assert "Did you mean 'stage'?" in str(caught.value)


@pytest.mark.parametrize("override", ["override", ""])
@pytest.mark.parametrize(
    "collection", [{}, {"dev": {}}, {"dev": {"TEST_CONFIG_VALUE": "fallback"}}]
)
def test_config_override(monkeypatch, override, collection):
    monkeypatch.setenv("TEST_CONFIG_VALUE", override)
    assert get_conf_from_collection(collection, "TEST_CONFIG_VALUE") == override


def test_missing_collection_environment():
    with pytest.raises(InvalidEnvironmentError) as caught:
        get_conf_from_collection({"stage": {}}, "TEST_CONFIG_VALUE")
    assert caught.value.env == "dev"
    assert caught.value.valid_environments == ("stage",)


def test_missing_configuration():
    with pytest.raises(MissingConfigurationError) as caught:
        get_conf_from_collection(
            {"dev": {"AVAILABLE_KEY": "value"}}, "TEST_CONFIG_VALUE"
        )
    assert isinstance(caught.value, HeroConfigurationError)
    assert caught.value.key == "TEST_CONFIG_VALUE"
    assert caught.value.env == "dev"
    assert "AVAILABLE_KEY" in str(caught.value)


def test_environment_and_pool_configuration_match_types():
    assert set(ENVIRONMENTS) == set(URL_MAP)
    for env in ENVIRONMENTS:
        for pool in POOLS:
            assert get_pool_config(env, pool) == URL_MAP[env][pool]


def test_invalid_pool_config_environment_source():
    with pytest.raises(InvalidEnvironmentError) as caught:
        get_pool_config("stag", "PRIMARY")
    assert "get_pool_config() env argument" in str(caught.value)
    assert "HERO_ENV environment variable" not in str(caught.value)


@pytest.mark.parametrize("pool", ["", "primary", "OTHER"])
def test_invalid_pool(pool):
    with pytest.raises(InvalidPoolError) as caught:
        get_pool_config("dev", pool)
    assert isinstance(caught.value, HeroConfigurationError)
    assert caught.value.pool == pool
    assert caught.value.valid_pools == POOLS


@pytest.fixture
def runtime_secret():
    return {
        "HERO_ENV": "stage",
        "HERO_CLIENT_ID": "synthetic-client-id",
        "HERO_CLIENT_SECRET": "synthetic-client-secret",
        "HERO_PROJECT": "synthetic-project",
    }


@pytest.fixture
def secrets_client(monkeypatch, runtime_secret):
    client = Mock()
    client.get_secret_value.side_effect = lambda **kwargs: {
        "SecretString": json.dumps(runtime_secret)
    }
    monkeypatch.setitem(
        sys.modules, "boto3", SimpleNamespace(client=Mock(return_value=client))
    )
    monkeypatch.setenv("SECRET_NAME", "synthetic-secret-name")
    monkeypatch.setenv("HERO_CLIENT_ID", "previous-id")
    monkeypatch.setenv("HERO_CLIENT_SECRET", "previous-secret")
    return client


def test_load_runtime_config(secrets_client, runtime_secret):
    assert load_runtime_config() == runtime_secret
    for key in ("HERO_ENV", "HERO_CLIENT_ID", "HERO_CLIENT_SECRET"):
        assert os.environ[key] == runtime_secret[key]
    secrets_client.get_secret_value.assert_called_once_with(
        SecretId="synthetic-secret-name"
    )


@pytest.mark.parametrize("key", ["HERO_ENV", "HERO_CLIENT_ID", "HERO_CLIENT_SECRET"])
def test_missing_runtime_field_preserves_environment(
    secrets_client, runtime_secret, key
):
    del runtime_secret[key]
    before = dict(os.environ)
    with pytest.raises(HeroConfigurationError, match=key):
        load_runtime_config()
    assert dict(os.environ) == before


@pytest.mark.parametrize("env", [None, "", "stag", 123, []])
def test_invalid_runtime_environment(secrets_client, runtime_secret, env):
    runtime_secret["HERO_ENV"] = env
    before = dict(os.environ)
    with pytest.raises(
        InvalidEnvironmentError, match="HERO_ENV in secret 'synthetic-secret-name'"
    ):
        load_runtime_config()
    assert dict(os.environ) == before


@pytest.mark.parametrize("key", ["HERO_CLIENT_ID", "HERO_CLIENT_SECRET"])
@pytest.mark.parametrize(
    "value", [None, "", "  ", 123, [], {}, True, "synthetic\0secret"]
)
def test_invalid_runtime_credentials(secrets_client, runtime_secret, key, value):
    runtime_secret[key] = value
    before = dict(os.environ)
    with pytest.raises(HeroConfigurationError, match=key) as caught:
        load_runtime_config()
    assert "synthetic-secret-name" in str(caught.value)
    assert "synthetic-client-secret" not in str(caught.value)
    assert "synthetic\\x00secret" not in str(caught.value)
    assert dict(os.environ) == before


@pytest.mark.parametrize("payload", [None, [], "text", 123])
def test_runtime_secret_must_be_object(secrets_client, payload):
    secrets_client.get_secret_value.side_effect = None
    secrets_client.get_secret_value.return_value = {"SecretString": json.dumps(payload)}
    before = dict(os.environ)
    with pytest.raises(HeroConfigurationError, match="JSON object"):
        load_runtime_config()
    assert dict(os.environ) == before
