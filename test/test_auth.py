import pytest
import hero
import os
import json
import time

def test_read_permissions():

    hero_client = hero.HeroClient()
    auth = hero_client.Auth()
    hero_client.authenticate()

    appType = "data-hub"
    appId = "dev-hero-test-framework"

    permissions = auth.read_permissions(appType=appType, appId=appId)
    assert type(permissions) is list