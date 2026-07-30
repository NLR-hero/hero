import pytest
import hero
import os


def test_create_permission():
    hero_client = hero.HeroClient()
    auth = hero_client.Auth()

    app_type = "data-repo"
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

    app_type = "data-repo"
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
    assert set(res["permissionSet"]) == {"READ_PROJECT", "READ_DATASET", "READ_FILE"}


def test_read_permissions():
    hero_client = hero.HeroClient()
    auth = hero_client.Auth()

    app_type = "data-repo"
    app_id = "dev-hero-test-framework"

    permissions = auth.read_permissions(app_type=app_type, app_id=app_id)
    assert type(permissions) is list


def test_update_permission():
    hero_client = hero.HeroClient()
    auth = hero_client.Auth()

    app_type = "data-repo"
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

    app_type = "data-repo"
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

    res = auth.create_user(
        username=username, name=name, email=email, roles=roles, pool="legacy"
    )

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

    res = auth.read_user(username=username, pool="legacy")
    assert type(res) is dict
    assert res["username"] == username


def test_update_user():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    username = "test-auth-user"
    roles = ["data-repo/user", "task-engine/user"]

    res = auth.update_user(username=username, roles=roles, pool="legacy")
    assert type(res) is dict
    assert res["username"] == username
    assert set(res["roles"]) == set(roles)


def test_delete_user():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    username = "test-auth-user"

    res = auth.delete_user(username=username, pool="legacy")
    assert type(res) is dict
    assert res["username"] == username


def test_list_users():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    res = auth.list_users(pool="legacy")
    assert type(res) is dict
    assert type(res["users"]) is list


def test_list_users_no_pool():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    res = auth.list_users()
    assert type(res) is dict


def test_machine_crud():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    machine_name = "test-auth-machine"
    roles = ["data-repo/user"]

    res = auth.create_machine(name=machine_name, roles=roles, pool="legacy")
    id = res["id"]

    assert type(res) is dict
    assert res["name"] == machine_name
    assert res["roles"] == roles

    res = auth.read_machine(id=id, pool="legacy")
    assert type(res) is dict
    assert res["name"] == machine_name

    roles = ["data-repo/user", "task-engine/user"]

    res = auth.update_machine(id=id, roles=roles, pool="legacy")
    assert type(res) is dict
    assert res["name"] == machine_name
    assert "data-repo/user" in res["roles"]
    assert "task-engine/user" in res["roles"]

    res = auth.delete_machine(id=id, pool="legacy")
    assert type(res) is dict
    assert res["name"] == machine_name


def test_list_machines():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    res = auth.list_machines(pool="legacy")
    assert type(res) is dict
    assert type(res["machines"]) is list


def test_list_machines_no_pool():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    res = auth.list_machines()
    assert type(res) is dict


def test_create_role():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    resource = "test-auth-resource"
    scope = "test-auth-scope"
    description = "Test Auth Role"

    res = auth.create_role(
        resource=resource, scope=scope, description=description, pool="legacy"
    )
    assert type(res) is dict
    assert res["name"] == f"{resource}/{scope}"
    assert res["description"] == description


def test_list_roles():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    res = auth.list_roles(pool="legacy")
    assert type(res) is dict
    assert type(res["roles"]) is list


def test_list_roles_no_pool():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    res = auth.list_roles()
    assert type(res) is dict


def test_read_role():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    resource = "test-auth-resource"
    scope = "test-auth-scope"

    res = auth.read_role(resource=resource, scope=scope, pool="legacy")
    assert type(res) is dict
    assert res["name"] == f"{resource}/{scope}"


def test_update_role():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    resource = "test-auth-resource"
    scope = "test-auth-scope"
    description = "Test Auth Role, but modified"

    res = auth.update_role(
        resource=resource, scope=scope, description=description, pool="legacy"
    )
    assert type(res) is dict
    assert res["name"] == f"{resource}/{scope}"
    assert res["description"] == description


def test_delete_role():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    resource = "test-auth-resource"
    scope = "test-auth-scope"
    res = auth.delete_role(resource=resource, scope=scope, pool="legacy")
    assert type(res) is dict


# ─── Pool routing ─────────────────────────────────────────────────────────────


def test_user_pool_routing():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    username = "pool-routing-user"

    auth.create_user(
        username=username,
        name="Pool Routing User",
        email="pool-routing@nrel.gov",
        roles=["data-repo/user"],
        pool="legacy",
    )

    try:
        res = auth.read_user(username=username, pool="legacy")
        assert res["username"] == username

        import requests

        with pytest.raises(requests.exceptions.HTTPError) as exc_info:
            auth.read_user(username=username, pool="primary")
        assert exc_info.value.response.status_code == 404
    finally:
        auth.delete_user(username=username, pool="legacy")


def test_machine_pool_routing():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    res = auth.create_machine(
        name="pool-routing-machine",
        roles=["data-repo/user"],
        pool="legacy",
    )
    machine_id = res["id"]

    try:
        from_legacy = auth.read_machine(id=machine_id, pool="legacy")
        assert from_legacy["name"] == "pool-routing-machine"

        import requests

        with pytest.raises(requests.exceptions.HTTPError) as exc_info:
            auth.read_machine(id=machine_id, pool="primary")
        assert exc_info.value.response.status_code == 404
    finally:
        auth.delete_machine(id=machine_id, pool="legacy")


def test_role_pool_routing():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    resource = "pool-routing-resource"
    scope = "pool-routing-scope"

    auth.create_role(
        resource=resource, scope=scope, description="Pool Routing Role", pool="legacy"
    )

    try:
        from_legacy = auth.read_role(resource=resource, scope=scope, pool="legacy")
        assert from_legacy["name"] == f"{resource}/{scope}"

        from_primary = auth.read_role(resource=resource, scope=scope, pool="primary")
        assert from_primary["name"] == f"{resource}/{scope}"
        
    finally:
        auth.delete_role(resource=resource, scope=scope, pool="legacy")


# ─── Access Requests ──────────────────────────────────────────────────────────


def test_access_request_crud():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    app_type = "data-repo"
    app_id = "dev-hero-test-framework"

    created = auth.create_access_request(
        app_type=app_type,
        app_id=app_id,
        permission_set=["READ_PROJECT", "READ_DATASET"],
        subject="Requesting access for test suite validation",
    )
    assert type(created) is dict
    assert created["appType"] == app_type
    assert created["appId"] == app_id
    request_id = created["requestId"]

    fetched = auth.read_access_request(
        app_type=app_type, app_id=app_id, request_id=request_id
    )
    assert type(fetched) is dict
    assert fetched["requestId"] == request_id

    approved = auth.update_access_request(
        app_type=app_type, app_id=app_id, request_id=request_id, status="approved"
    )
    assert type(approved) is dict
    assert approved["status"] == "approved"

    revoked = auth.update_access_request(
        app_type=app_type, app_id=app_id, request_id=request_id, status="revoked"
    )
    assert type(revoked) is dict
    assert revoked["status"] == "revoked"

    deleted = auth.delete_access_request(
        app_type=app_type, app_id=app_id, request_id=request_id
    )
    assert type(deleted) is dict


def test_list_access_requests():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    res = auth.list_access_requests(
        app_type="data-repo", app_id="dev-hero-test-framework"
    )
    assert type(res) is list


def test_list_access_requests_with_status_filter():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    res = auth.list_access_requests(
        app_type="data-repo", app_id="dev-hero-test-framework", status="pending"
    )
    assert type(res) is list
    for r in res:
        assert r["status"] == "pending"


def test_list_my_access_requests():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/user")
    auth = hero_client.Auth()

    res = auth.list_my_access_requests()
    assert type(res) is list


def test_list_my_access_requests_with_status_filter():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/user")
    auth = hero_client.Auth()

    res = auth.list_my_access_requests(status="approved")
    assert type(res) is list
    for r in res:
        assert r["status"] == "approved"


# ─── Access Request Config ────────────────────────────────────────────────────


def test_access_request_config_crud():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    app_type = "data-repo"
    app_id = "dev-hero-test-framework"

    created = auth.create_access_request_config(
        app_type=app_type,
        app_id=app_id,
        allowed_domains=["nrel.gov"],
        requestable_roles=["viewer", "admin"],
        schema_version=1,
    )
    assert type(created) is dict
    assert created["appType"] == app_type
    assert created["appId"] == app_id
    assert "nrel.gov" in created["allowedDomains"]
    assert created["requestableRoles"] == ["viewer", "admin"]
    assert created["schemaVersion"] == 1

    fetched = auth.read_access_request_config(app_type=app_type, app_id=app_id)
    assert type(fetched) is dict
    assert fetched["appId"] == app_id

    updated = auth.update_access_request_config(
        app_type=app_type,
        app_id=app_id,
        allowed_domains=["nrel.gov", "nrelgov.onmicrosoft.com"],
        requestable_roles=["viewer", "admin"],
        schema_version=2,
    )
    assert type(updated) is dict
    assert "nrelgov.onmicrosoft.com" in updated["allowedDomains"]
    assert "admin" in updated["requestableRoles"]
    assert updated["schemaVersion"] == 2


def test_access_request_config_resource_scoped_crud():
    # Resource-scoped variant of the CRUD test above. When resource_type/resource_id
    # are provided explicitly (differing from app_type/app_id), the SDK hits the
    # resource-scoped route and the API persists a distinct config row per resource tuple.
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    app_type = "data-repo"
    app_id = "dev-hero-test-framework"
    resource_type = "project"
    resource_id = "sdk-test-proj-1"

    created = auth.create_access_request_config(
        app_type=app_type,
        app_id=app_id,
        resource_type=resource_type,
        resource_id=resource_id,
        allowed_domains=["nrel.gov"],
        requestable_roles=["viewer"],
        schema_version=1,
    )
    assert type(created) is dict
    assert created["resourceType"] == resource_type
    assert created["resourceId"] == resource_id

    fetched = auth.read_access_request_config(
        app_type=app_type,
        app_id=app_id,
        resource_type=resource_type,
        resource_id=resource_id,
    )
    assert type(fetched) is dict
    assert fetched["resourceType"] == resource_type
    assert fetched["resourceId"] == resource_id

    updated = auth.update_access_request_config(
        app_type=app_type,
        app_id=app_id,
        resource_type=resource_type,
        resource_id=resource_id,
        allowed_domains=["nrel.gov", "example.com"],
        requestable_roles=["viewer"],
        schema_version=1,
    )
    assert type(updated) is dict
    assert "example.com" in updated["allowedDomains"]


def test_list_access_request_configs():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    res = auth.list_access_request_configs()
    assert type(res) is list


# ─── Service Schema ───────────────────────────────────────────────────────────


def test_service_schema_crud():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    app_type = "hero-sdk-test-service"

    registered = auth.register_service_schema(
        app_type=app_type,
        version=1,
        permissions=["READ_RESOURCE", "WRITE_RESOURCE", "DELETE_RESOURCE"],
        roles={
            "viewer": ["READ_RESOURCE"],
            "editor": ["READ_RESOURCE", "WRITE_RESOURCE"],
            "admin": ["READ_RESOURCE", "WRITE_RESOURCE", "DELETE_RESOURCE"],
        },
    )
    assert type(registered) is dict
    assert registered["appType"] == app_type
    assert registered["version"] == 1
    assert "READ_RESOURCE" in registered["permissions"]
    assert "viewer" in registered["roles"]
    assert "admin" in registered["roles"]

    fetched = auth.read_service_schema(app_type=app_type, version=1)
    assert type(fetched) is dict
    assert fetched["appType"] == app_type
    assert fetched["version"] == 1

    auth.register_service_schema(
        app_type=app_type,
        version=2,
        permissions=[
            "READ_RESOURCE",
            "WRITE_RESOURCE",
            "DELETE_RESOURCE",
            "ADMIN_RESOURCE",
        ],
        roles={
            "viewer": ["READ_RESOURCE"],
            "editor": ["READ_RESOURCE", "WRITE_RESOURCE"],
            "admin": [
                "READ_RESOURCE",
                "WRITE_RESOURCE",
                "DELETE_RESOURCE",
                "ADMIN_RESOURCE",
            ],
        },
    )

    versions = auth.list_service_schema_versions(app_type=app_type)
    assert type(versions) is list
    assert len(versions) >= 2
    version_numbers = [v["version"] for v in versions]
    assert 1 in version_numbers
    assert 2 in version_numbers

    auth.delete_service_schema(app_type=app_type, version=1)
    auth.delete_service_schema(app_type=app_type, version=2)


def test_list_service_schemas():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    res = auth.list_service_schemas()
    assert type(res) is list


def test_service_schema_resource_types():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    app_type = "hero-sdk-test-service-v2"

    registered = auth.register_service_schema(
        app_type=app_type,
        version=1,
        permissions=[
            "READ_RESOURCE",
            "UPDATE_RESOURCE",
            "CREATE_RESOURCE",
            "DELETE_RESOURCE",
        ],
        roles={},
        resource_types={
            "app": {
                "roles": {
                    "viewer": ["READ_RESOURCE"],
                    "approver": ["READ_RESOURCE", "UPDATE_RESOURCE"],
                    "admin": [
                        "READ_RESOURCE",
                        "UPDATE_RESOURCE",
                        "CREATE_RESOURCE",
                        "DELETE_RESOURCE",
                    ],
                }
            },
            "project": {
                "roles": {
                    "viewer": ["READ_RESOURCE"],
                    "approver": ["READ_RESOURCE", "UPDATE_RESOURCE"],
                    "admin": [
                        "READ_RESOURCE",
                        "UPDATE_RESOURCE",
                        "CREATE_RESOURCE",
                        "DELETE_RESOURCE",
                    ],
                }
            },
        },
    )
    assert type(registered) is dict
    assert registered["appType"] == app_type
    assert "resourceTypes" in registered
    assert "viewer" in registered["resourceTypes"]["app"]["roles"]
    assert "approver" in registered["resourceTypes"]["app"]["roles"]
    assert "admin" in registered["resourceTypes"]["project"]["roles"]

    fetched = auth.read_service_schema(app_type=app_type, version=1)
    assert "resourceTypes" in fetched
    assert "UPDATE_RESOURCE" in fetched["resourceTypes"]["app"]["roles"]["approver"]

    auth.delete_service_schema(app_type=app_type, version=1)


def test_service_schema_overwrite():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/admin")
    auth = hero_client.Auth()

    app_type = "hero-sdk-test-service"

    first = auth.register_service_schema(
        app_type=app_type,
        version=1,
        permissions=["READ_RESOURCE"],
        roles={"viewer": ["READ_RESOURCE"]},
    )
    assert first["permissions"] == ["READ_RESOURCE"]

    overwritten = auth.register_service_schema(
        app_type=app_type,
        version=1,
        permissions=["READ_RESOURCE", "WRITE_RESOURCE"],
        roles={
            "viewer": ["READ_RESOURCE"],
            "editor": ["READ_RESOURCE", "WRITE_RESOURCE"],
        },
    )
    assert "WRITE_RESOURCE" in overwritten["permissions"]
    assert "editor" in overwritten["roles"]

    auth.delete_service_schema(app_type=app_type, version=1)


def test_get_client_credentials():
    hero_client = hero.HeroClient()
    hero_client.add_scope("hero-auth/user")
    auth = hero_client.Auth()

    # First, let's create a permission for the TVM functionality
    app_type = "auth"  # Using auth app type for TVM
    app_id = "dev-hero-test-framework"
    principal_type = "machine"

    # Get the actual user ID from environment variable
    principal_id = os.getenv("HERO_CLIENT_ID")
    if not principal_id:
        pytest.skip("HERO_CLIENT_ID environment variable not set")

    # Try with the hero-auth/admin scope to create permissions
    admin_client = hero.HeroClient()
    admin_client.add_scope("hero-auth/admin")
    admin_auth = admin_client.Auth()

    resource_type = "token"
    resource_id = "hero-service-role-ops-dev-hero-test-framework"
    permission_set = ["GET_TOKEN"]

    # Create permission for TVM access using admin client
    try:
        admin_auth.create_permission(
            app_type=app_type,
            app_id=app_id,
            principal_type=principal_type,
            principal_id=principal_id,
            resource_type=resource_type,
            resource_id=resource_id,
            permission_set=permission_set,
        )
        print(f"Permission created successfully for {principal_id}")
    except Exception as e:
        print(f"Permission creation failed (might already exist): {e}")

    # Now test the TVM functionality with regular user
    res = auth.get_client_credentials(
        application_id=app_id,
        role_id=resource_id,  # Use the same role we gave permission for
    )

    print("tvm response", res)
    assert type(res) is dict

    # Clean up the permission using admin client
    try:
        admin_auth.delete_permission(
            app_type=app_type,
            app_id=app_id,
            principal_type=principal_type,
            principal_id=principal_id,
            resource_type=resource_type,
            resource_id=resource_id,
        )
        print("Permission cleaned up successfully")
    except Exception as e:
        print(f"Permission cleanup failed: {e}")
