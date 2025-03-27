import pytest
import hero


def test_create_permission():
    hero_client = hero.HeroClient()
    auth = hero_client.Auth()

    app_type = "data-hub"
    app_id = "dev-hero-test-framework"
    principal_type = "user"
    principal_id = "python-app-test-user"
    resource_type = "data-repo"
    resource_id = "dev-hero-test-framework"
    permission_set = ["READ_PROJECT", "READ_DATASET", "READ_FILE"]

    res = auth.create_permission(
        app_type=app_type,
        app_id=app_id,
        principal_type=principal_type,
        principal_id=principal_id,
        resource_type=resource_type,
        resource_id=resource_id,
        permission_set=permission_set,
    )
    assert type(res) is dict
    assert res["permissionSet"] == permission_set


def test_read_permission():
    hero_client = hero.HeroClient()
    auth = hero_client.Auth()

    app_type = "data-hub"
    app_id = "dev-hero-test-framework"
    principal_type = "user"
    principal_id = "python-app-test-user"
    resource_type = "data-repo"
    resource_id = "dev-hero-test-framework"

    res = auth.read_permission(
        app_type=app_type,
        app_id=app_id,
        principal_type=principal_type,
        principal_id=principal_id,
        resource_type=resource_type,
        resource_id=resource_id,
    )
    assert type(res) is dict
    assert res["appType"] == app_type
    assert res["appId"] == app_id
    assert res["principalType"] == principal_type
    assert res["principalId"] == principal_id
    assert res["resourceType"] == resource_type
    assert res["resourceId"] == resource_id
    assert res["permissionSet"] == ["READ_PROJECT", "READ_DATASET", "READ_FILE"]


def test_read_permissions():
    hero_client = hero.HeroClient()
    auth = hero_client.Auth()

    app_type = "data-hub"
    app_id = "dev-hero-test-framework"

    permissions = auth.read_permissions(app_type=app_type, app_id=app_id)
    assert type(permissions) is list


def test_update_permission():
    hero_client = hero.HeroClient()
    auth = hero_client.Auth()

    app_type = "data-hub"
    app_id = "dev-hero-test-framework"
    principal_type = "user"
    principal_id = "python-app-test-user"
    resource_type = "data-repo"
    resource_id = "dev-hero-test-framework"
    permission_set = [
        "READ_PROJECT",
        "READ_DATASET",
        "READ_FILE",
        "WRITE_PROJECT",
        "WRITE_DATASET",
        "WRITE_FILE",
    ]

    res = auth.update_permission(
        app_type=app_type,
        app_id=app_id,
        principal_type=principal_type,
        principal_id=principal_id,
        resource_type=resource_type,
        resource_id=resource_id,
        permission_set=permission_set,
    )
    assert type(res) is dict
    assert res["permissionSet"] == permission_set


def test_delete_permission():
    hero_client = hero.HeroClient()
    auth = hero_client.Auth()

    app_type = "data-hub"
    app_id = "dev-hero-test-framework"
    principal_type = "user"
    principal_id = "python-app-test-user"
    resource_type = "data-repo"
    resource_id = "dev-hero-test-framework"

    res = auth.delete_permission(
        app_type=app_type,
        app_id=app_id,
        principal_type=principal_type,
        principal_id=principal_id,
        resource_type=resource_type,
        resource_id=resource_id,
    )
    assert type(res) is dict
    assert res["appType"] == app_type
    assert res["appId"] == app_id
    assert res["principalType"] == principal_type
    assert res["principalId"] == principal_id
    assert res["resourceType"] == resource_type
    assert res["resourceId"] == resource_id


def test_user_create():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    username = "test-auth-user"
    name = "Test Auth User"
    email = "test@nrel.gov"
    roles = ["data-repo/user"]

    res = auth.create_user(username=username, name=name, email=email, roles=roles)

    assert type(res) is dict
    assert res["username"] == username
    assert res["name"] == name
    assert res["email"] == email
    assert res["roles"] == roles


def test_read_user():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    username = "test-auth-user"

    res = auth.read_user(username=username)
    assert type(res) is dict
    assert res["username"] == username


def test_update_user():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    username = "test-auth-user"
    roles = ["data-repo/user", "task-engine/user"]

    res = auth.update_user(username=username, roles=roles)
    assert type(res) is dict
    assert res["username"] == username
    assert res["roles"] == roles


def test_delete_user():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    username = "test-auth-user"

    res = auth.delete_user(username=username)
    assert type(res) is dict
    assert res["username"] == username


def test_list_users():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    res = auth.list_users()
    assert type(res) is dict
    assert type(res["users"]) is list


def test_machine_crud():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    machine_name = "test-auth-machine"
    roles = ["data-repo/user"]

    res = auth.create_machine(name=machine_name, roles=roles)
    id = res["id"]

    assert type(res) is dict
    assert res["name"] == machine_name
    assert res["roles"] == roles

    res = auth.read_machine(id=id)
    assert type(res) is dict
    assert res["name"] == machine_name

    roles = ["data-repo/user", "task-engine/user"]

    res = auth.update_machine(id=id, roles=roles)
    assert type(res) is dict
    assert res["name"] == machine_name
    assert "data-repo/user" in res["roles"]
    assert "task-engine/user" in res["roles"]

    res = auth.delete_machine(id=id)
    assert type(res) is dict
    assert res["name"] == machine_name


def test_list_machines():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    res = auth.list_machines()
    assert type(res) is dict
    assert type(res["machines"]) is list


def test_create_role():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    resource = "test-auth-resource"
    scope = "test-auth-scope"
    description = "Test Auth Role"

    res = auth.create_role(resource=resource, scope=scope, description=description)
    assert type(res) is dict
    assert res["name"] == f"{resource}/{scope}"
    assert res["description"] == description


def test_read_role():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    resource = "test-auth-resource"
    scope = "test-auth-scope"

    res = auth.read_role(resource=resource, scope=scope)
    assert type(res) is dict
    assert res["name"] == f"{resource}/{scope}"


def test_update_role():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    resource = "test-auth-resource"
    scope = "test-auth-scope"
    description = "Test Auth Role, but modified"

    res = auth.update_role(resource=resource, scope=scope, description=description)
    assert type(res) is dict
    assert res["name"] == f"{resource}/{scope}"
    assert res["description"] == description


def test_delete_role():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    resource = "test-auth-resource"
    scope = "test-auth-scope"
    res = auth.delete_role(resource=resource, scope=scope)
    assert type(res) is dict
