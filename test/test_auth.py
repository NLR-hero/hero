import pytest
import hero
import os
import json
import time

def test_create_permission():
        hero_client = hero.HeroClient()
        auth = hero_client.Auth()
        hero_client.authenticate()

        appType = "data-hub"
        appId = "dev-hero-test-framework"
        principalType = "user"
        principalId = "python-app-test-user"
        resourceType = "data-repo"
        resourceId = "dev-hero-test-framework"
        permissionSet = [
            "READ_PROJECT",
            "READ_DATASET",
            "READ_FILE"
        ]

        res = auth.create_permission(appType=appType, appId=appId, principalType=principalType, principalId=principalId, resourceType=resourceType, resourceId=resourceId, permissionSet=permissionSet)
        assert type(res) is dict
        print('res here pls!!!!!!!!!!!')
        print(res)
        assert res["permissionSet"] == permissionSet

def test_read_permission():
    hero_client = hero.HeroClient()
    auth = hero_client.Auth()
    hero_client.authenticate()

    appType = "data-hub"
    appId = "dev-hero-test-framework"
    principalType = "user"
    principalId = "python-app-test-user"
    resourceType = "data-repo"
    resourceId = "dev-hero-test-framework"

    res = auth.read_permission(appType=appType, appId=appId, principalType=principalType, principalId=principalId, resourceType=resourceType, resourceId=resourceId)
    assert type(res) is dict
    assert res["appType"] == appType
    assert res["appId"] == appId
    assert res["principalType"] == principalType
    assert res["principalId"] == principalId
    assert res["resourceType"] == resourceType
    assert res["resourceId"] == resourceId
    assert res["permissionSet"] == [
        "READ_PROJECT",
        "READ_DATASET",
        "READ_FILE"
    ]

def test_read_permissions():
    hero_client = hero.HeroClient()
    auth = hero_client.Auth()
    hero_client.authenticate()

    appType = "data-hub"
    appId = "dev-hero-test-framework"

    permissions = auth.read_permissions(appType=appType, appId=appId)
    assert type(permissions) is list

def test_update_permission():
    hero_client = hero.HeroClient()
    auth = hero_client.Auth()
    hero_client.authenticate()

    appType = "data-hub"
    appId = "dev-hero-test-framework"
    principalType = "user"
    principalId = "python-app-test-user"
    resourceType = "data-repo"
    resourceId = "dev-hero-test-framework"
    permissionSet = [
        "READ_PROJECT",
        "READ_DATASET",
        "READ_FILE",
        "WRITE_PROJECT",
        "WRITE_DATASET",
        "WRITE_FILE"
    ]

    res = auth.update_permission(appType=appType, appId=appId, principalType=principalType, principalId=principalId, resourceType=resourceType, resourceId=resourceId, permissionSet=permissionSet)
    assert type(res) is dict
    assert res["permissionSet"] == permissionSet

def test_delete_permission():
    hero_client = hero.HeroClient()
    auth = hero_client.Auth()
    hero_client.authenticate()

    appType = "data-hub"
    appId = "dev-hero-test-framework"
    principalType = "user"
    principalId = "python-app-test-user"
    resourceType = "data-repo"
    resourceId = "dev-hero-test-framework"

    res = auth.delete_permission(appType=appType, appId=appId, principalType=principalType, principalId=principalId, resourceType=resourceType, resourceId=resourceId)
    assert type(res) is dict
    assert res["appType"] == appType
    assert res["appId"] == appId
    assert res["principalType"] == principalType
    assert res["principalId"] == principalId
    assert res["resourceType"] == resourceType
    assert res["resourceId"] == resourceId
