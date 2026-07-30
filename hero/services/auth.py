import json
import os
from ..url_map import URL_MAP
from ..lib import ServiceBase, decorate_all, log_errors, get_conf_from_collection
from requests.exceptions import HTTPError, JSONDecodeError
from ..lib.errors import MissingRequiredAttribute, HEROAPIResponseException
from ..lib.helpers import kwargs_to_json_for_request


@decorate_all(log_errors)
class AuthService(ServiceBase):

    def _configure(self):
        """
        Sets the API, adds required scope
        """
        self.client.add_scope("hero-auth/user")
        self.base_url = get_conf_from_collection(URL_MAP, "HERO_AUTH_API_URL")

    def create_permission(
        self,
        app_type=None,
        app_id=None,
        principal_type=None,
        principal_id=None,
        resource_type=None,
        resource_id=None,
        permission_set=None,
    ):
        """
        Creates a permission for the given app, principal, and resource

        Parameters
        ----------
        app_type : str, required
            The type of the app
        app_id : str, required
            The ID of the app
        principal_type : str, required
            The type of the principal
        principal_id : str, required
            The ID of the principal
        resource_type : str, required
            The type of the resource
        resource_id : str, required
            The ID of the resource
        permission_set : list, required
            The permission set

        Returns
        -------
        permission : dict
            The newly created permission entry containing the permission set

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """

        if app_type is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_type"')
        if app_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_id"')
        if principal_type is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "principal_type"'
            )
        if principal_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "principal_id"')
        if resource_type is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "resource_type"'
            )
        if resource_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "resource_id"')
        if permission_set is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "permission_set"'
            )

        attributes = {"permissionSet": permission_set}

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/permission/{app_type}/{app_id}/{principal_type}/{principal_id}/{resource_type}/{resource_id}"
        data = json.dumps(attributes)

        try:
            response = self.api.request("POST", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def read_permission(
        self,
        app_type=None,
        app_id=None,
        principal_type=None,
        principal_id=None,
        resource_type=None,
        resource_id=None,
    ):
        """
        Reads a permission for the given app, principal, and resource

        Parameters
        ----------
        app_type : str, required
            The type of the app
        app_id : str, required
            The ID of the app
        principal_type : str, required
            The type of the principal
        principal_id : str, required
            The ID of the principal
        resource_type : str, required
            The type of the resource
        resource_id : str, required
            The ID of the resource

        Returns
        -------
        permission : dict
            The permission entry containing the permission set

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """

        if app_type is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_type"')
        if app_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_id"')
        if principal_type is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "principal_type"'
            )
        if principal_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "principal_id"')
        if resource_type is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "resource_type"'
            )
        if resource_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "resource_id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/permission/{app_type}/{app_id}/{principal_type}/{principal_id}/{resource_type}/{resource_id}"

        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def read_permissions(
        self, app_type=None, app_id=None, principal_type=None, principal_id=None
    ):
        """
        Reads and returns a collection of permissions in the given app, principal, and resource

        Parameters
        ----------
        app_type : str, required
            The type of the app
        app_id : str, required
            The ID of the app
        principal_type : str, optional
            The type of the principal
        principal_id : str, optional
            The ID of the principal

        Returns
        -------
        permission : list
            A collection of permission entrys

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """

        if app_type is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_type"')
        if app_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/permissions/{app_type}/{app_id}"

        # Add principal_id and principal_type to the URL if provided to query permissions for a specific principal
        params = None
        if principal_id and principal_type:
            params = {principal_type: principal_id}

        try:
            response = self.api.request("GET", url, headers=headers, params=params)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def update_permission(
        self,
        app_type=None,
        app_id=None,
        principal_type=None,
        principal_id=None,
        resource_type=None,
        resource_id=None,
        permission_set=None,
    ):
        """
        Updates a permission for the given app, principal, and resource

        Parameters
        ----------
        app_type : str, required
            The type of the app
        app_id : str, required
            The ID of the app
        principal_type : str, required
            The type of the principal
        principal_id : str, required
            The ID of the principal
        resource_type : str, required
            The type of the resource
        resource_id : str, required
            The ID of the resource
        permission_set : list, required
            The updated permission set

        Returns
        -------
        permission : dict
            The newly updated permission entry containing the permission set

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """

        if app_type is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_type"')
        if app_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_id"')
        if principal_type is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "principal_type"'
            )
        if principal_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "principal_id"')
        if resource_type is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "resource_type"'
            )
        if resource_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "resource_id"')
        if permission_set is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "permission_set"'
            )

        attributes = {"permissionSet": permission_set}
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/permission/{app_type}/{app_id}/{principal_type}/{principal_id}/{resource_type}/{resource_id}"
        data = json.dumps(attributes)

        try:
            response = self.api.request("PUT", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def delete_permission(
        self,
        app_type=None,
        app_id=None,
        principal_type=None,
        principal_id=None,
        resource_type=None,
        resource_id=None,
    ):
        """
        Deletes a permission for the given app, principal, and resource

        Parameters
        ----------
        app_type : str, required
            The type of the app
        app_id : str, required
            The ID of the app
        principal_type : str, required
            The type of the principal
        principal_id : str, required
            The ID of the principal
        resource_type : str, required
            The type of the resource
        resource_id : str, required
            The ID of the resource

        Returns
        -------
        permission : dict
            The deleted permission entry containing the permission set

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """

        if app_type is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_type"')
        if app_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_id"')
        if principal_type is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "principal_type"'
            )
        if principal_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "principal_id"')
        if resource_type is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "resource_type"'
            )
        if resource_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "resource_id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/permission/{app_type}/{app_id}/{principal_type}/{principal_id}/{resource_type}/{resource_id}"

        try:
            response = self.api.request("DELETE", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def create_user(self, username=None, name=None, email=None, roles=None, pool=None):
        """
        Creates a user

        Parameters
        ----------
        username : str, required
            The username of the user. Note: this will function as the id of the user and must be unique.
        name : str, required
            The name of the user
        email : str, required
            The email of the user
        roles : list, required
            The roles of the user
        pool : str, optional
            The Cognito pool to target

        Returns
        -------
        user : dict
            The newly created user entry containing the username, name, email, and roles

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """
        if username is None:
            raise MissingRequiredAttribute('Missing required attribute: "username"')
        if name is None:
            raise MissingRequiredAttribute('Missing required attribute: "name"')
        if email is None:
            raise MissingRequiredAttribute('Missing required attribute: "email"')
        if roles is None:
            raise MissingRequiredAttribute('Missing required attribute: "roles"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/principals/user"
        data = json.dumps(
            {
                "username": username,
                "name": name,
                "email": email,
                "roles": roles,
                "pool": pool,
            }
        )

        try:
            response = self.api.request("POST", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def list_users(
        self, count=20, next_token=None, filter_key=None, filter_val=None, pool=None
    ):
        """
        Lists and returns a collection of users

        Parameters
        ----------
        count : int, optional
            The number of users to return
        next_token : str, optional
            The next token for pagination
        filter_key : str, optional
            An optional key to filter by. Note: this is required if filter_val is provided
        filter_val : str, optional
            An optional value to filter by. Note: this is required if filter_key is provided
        pool : str, optional
            The Cognito pool to target

        Returns
        -------
        user : list
            A collection of user entries

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/principals/users"
        params = {}

        if count:
            params["count"] = count
        if next_token:
            params["nextToken"] = next_token
        if filter_key and filter_val:
            params["filterKey"] = filter_key
            params["filterVal"] = filter_val
        if pool:
            params["pool"] = pool

        try:
            response = self.api.request("GET", url, headers=headers, params=params)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def read_user(self, username=None, pool=None):
        """
        Reads and returns a user

        Parameters
        ----------
        username : str, required
            The unique username of the user.
        pool : str, optional
            The Cognito pool to target

        Returns
        -------
        user : dict
            An entry containing the username, name, email, and roles of the user

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """
        if username is None:
            raise MissingRequiredAttribute('Missing required attribute: "username"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/principals/user/{username}"
        params = {}
        if pool:
            params["pool"] = pool

        try:
            response = self.api.request(
                "GET", url, headers=headers, params=params or None
            )
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def update_user(self, username=None, enabled=None, roles=None, pool=None):
        """
        Updates a user

        Parameters
        ----------
        username : str, required
            The unique username of the user.
        enabled : bool, optional
            The enabled status of the user
        roles : list, optional
            The roles of the user
        pool : str, optional
            The Cognito pool to target

        Returns
        -------
        user : dict
            An entry containing the username, name, email, and roles of the user

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """
        if username is None:
            raise MissingRequiredAttribute('Missing required attribute: "username"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/principals/user/{username}"

        data = {}
        if enabled is not None:
            data["enabled"] = enabled
        if roles is not None:
            data["roles"] = roles
        if pool is not None:
            data["pool"] = pool
        data = json.dumps(data)

        try:
            response = self.api.request("PUT", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def delete_user(self, username=None, pool=None):
        """
        Deletes and returns a user

        Parameters
        ----------
        username : str, required
            The unique username of the user.
        pool : str, optional
            The Cognito pool to target

        Returns
        -------
        user : dict
            An entry containing the username, name, email, and roles of the user

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """
        if username is None:
            raise MissingRequiredAttribute('Missing required attribute: "username"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/principals/user/{username}"
        params = {}
        if pool:
            params["pool"] = pool

        try:
            response = self.api.request(
                "DELETE", url, headers=headers, params=params or None
            )
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def create_machine(
        self,
        name=None,
        roles=None,
        generate_secret=None,
        callback_urls=None,
        logout_urls=None,
        pool=None,
    ):
        """
        Creates a new machine client

        Parameters
        ----------
        name : str, required
            The name of the machine
        roles : list, required
            The roles of the machine
        generate_secret : bool, optional
            Whether to generate a secret for the machine
        callback_urls : list, optional
            The callback URLs for the machine
        logout_urls : list, optional
            The logout URLs for the machine
        pool : str, optional
            The Cognito pool to target

        Returns
        -------
        machine : dict
            The newly created machine entry containing the name, roles, secret, etc

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """
        if name is None:
            raise MissingRequiredAttribute('Missing required attribute: "name"')
        if roles is None:
            raise MissingRequiredAttribute('Missing required attribute: "roles"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/principals/machine"
        data = json.dumps(
            {
                "name": name,
                "roles": roles,
                "generateSecret": generate_secret,
                "callbackUrls": callback_urls,
                "logoutUrls": logout_urls,
                "pool": pool,
            }
        )

        try:
            response = self.api.request("POST", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def list_machines(self, count=20, next_token=None, pool=None):
        """
        Returns a list of machine clients

        Parameters
        ----------
        count : int, optional
            The number of machines to return
        next_token : str, optional
            The next token for pagination
        pool : str, optional
            The Cognito pool to target

        Returns
        -------
        machine : dict
            A collection of machine entries containing the name, roles, secret, etc

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/principals/machines"
        params = {}

        if count:
            params["count"] = count
        if next_token:
            params["nextToken"] = next_token
        if pool:
            params["pool"] = pool

        try:
            response = self.api.request("GET", url, headers=headers, params=params)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def read_machine(self, id=None, pool=None):
        """
        Reads and returns a machine client

        Parameters
        ----------
        id: str, required
            The unique ID of the machine client
        pool : str, optional
            The Cognito pool to target

        Returns
        -------
        machine : dict
            A machine entry containing the name, roles, secret, etc

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """
        if id is None:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/principals/machine/{id}"
        params = {}
        if pool:
            params["pool"] = pool

        try:
            response = self.api.request(
                "GET", url, headers=headers, params=params or None
            )
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def update_machine(
        self,
        id=None,
        name=None,
        roles=None,
        generate_secret=None,
        callback_urls=None,
        logout_urls=None,
        pool=None,
    ):
        """
        Updates a machine client

        Parameters
        ----------
        id: str, required
            The unique ID of the machine client
        name : str, optional
            The name of the machine
        roles : list, optional
            The roles of the machine
        generate_secret : bool, optional
            Whether to generate a secret for the machine
        callback_urls : list, optional
            The callback URLs for the machine
        logout_urls : list, optional
            The logout URLs for the machine
        pool : str, optional
            The Cognito pool to target

        Returns
        -------
        machine : dict
            The newly updated machine entry containing the name, roles, secret, etc

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """
        if id is None:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/principals/machine/{id}"
        data = json.dumps(
            {
                "name": name,
                "roles": roles,
                "generateSecret": generate_secret,
                "callbackUrls": callback_urls,
                "logoutUrls": logout_urls,
                "pool": pool,
            }
        )

        try:
            response = self.api.request("PUT", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def delete_machine(self, id=None, pool=None):
        """
        Deletes a machine client

        Parameters
        ----------
        id: str, required
            The unique ID of the machine client
        pool : str, optional
            The Cognito pool to target

        Returns
        -------
        machine : dict
            The deleted machine entry containing the name, roles, secret, etc

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """
        if id is None:
            raise MissingRequiredAttribute('Missing required attribute: "id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/principals/machine/{id}"
        params = {}
        if pool:
            params["pool"] = pool

        try:
            response = self.api.request(
                "DELETE", url, headers=headers, params=params or None
            )
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def create_role(self, resource=None, scope=None, description=None, pool=None):
        """
        Creates a role

        Parameters
        ----------
        resource : str, required
            The resource this role is for
        scope : str, required
            The scope this role covers for the given resource
        description : str, optional
            The description of the role
        pool : str, optional
            The Cognito pool to target

        Returns
        -------
        role : dict
            The newly created role entry containing the name and description

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """
        if resource is None:
            raise MissingRequiredAttribute('Missing required attribute: "resource"')
        if scope is None:
            raise MissingRequiredAttribute('Missing required attribute: "scope"')

        name = f"{resource}/{scope}"
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/role"

        data = json.dumps({"name": name, "description": description, "pool": pool})

        try:
            response = self.api.request("POST", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def list_roles(self, count=20, next_token=None, pool=None):
        """
        Reads and returns a collection of role entries

        Parameters
        ----------
        count : int, optional
            The number of roles to return
        next_token : str, optional
            The next token for pagination
        pool : str, optional
            The Cognito pool to target

        Returns
        -------
        role : dict
            A collection of role entries

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/roles"
        params = {}

        if count:
            params["count"] = count
        if next_token:
            params["nextToken"] = next_token
        if pool:
            params["pool"] = pool

        try:
            response = self.api.request("GET", url, headers=headers, params=params)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def read_role(self, resource=None, scope=None, pool=None):
        """
        Reads and returns a role

        Parameters
        ----------
        resource : str, required
            The resource this role is for
        scope : str, required
            The scope this role covers for the given resource
        pool : str, optional
            The Cognito pool to target

        Returns
        -------
        role : dict
            A role entry containing the name and description

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """
        if resource is None:
            raise MissingRequiredAttribute('Missing required attribute: "resource"')
        if scope is None:
            raise MissingRequiredAttribute('Missing required attribute: "scope"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/role/{resource}/{scope}"
        params = {}
        if pool:
            params["pool"] = pool

        try:
            response = self.api.request(
                "GET", url, headers=headers, params=params or None
            )
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def update_role(self, resource=None, scope=None, description=None, pool=None):
        """
        Updates a role

        Parameters
        ----------
        resource : str, required
            The resource this role is for
        scope : str, required
            The scope this role covers for the given resource
        description : str, required
            The description of the role
        pool : str, optional
            The Cognito pool to target

        Returns
        -------
        role : dict
            The newly updated role entry containing the name and description

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """
        if resource is None:
            raise MissingRequiredAttribute('Missing required attribute: "resource"')
        if scope is None:
            raise MissingRequiredAttribute('Missing required attribute: "scope"')
        if description is None:
            raise MissingRequiredAttribute('Missing required attribute: "description"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/role/{resource}/{scope}"
        data = json.dumps({"description": description, "pool": pool})

        try:
            response = self.api.request("PUT", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def delete_role(self, resource=None, scope=None, pool=None):
        """
        Deletes a role

        Parameters
        ----------
        resource : str, required
            The resource this role is for
        scope : str, required
            The scope this role covers for the given resource
        pool : str, optional
            The Cognito pool to target

        Returns
        -------
        role : dict
            The newly deleted role entry containing the name and description

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON

        Notes
        -----
        New in version 0.4.0
        """
        if resource is None:
            raise MissingRequiredAttribute('Missing required attribute: "resource"')
        if scope is None:
            raise MissingRequiredAttribute('Missing required attribute: "scope"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/role/{resource}/{scope}"
        params = {}
        if pool:
            params["pool"] = pool

        try:
            response = self.api.request(
                "DELETE", url, headers=headers, params=params or None
            )
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def get_client_credentials(self, application_id, role_id):
        """
        Returns the client credentials for a given application and role.

        Parameters
        ----------
        application_id : str, required
            The ID of the application
        role_id : str, required
            The ID of the role
        Returns
        -------
        credentials : dict
            The client credentials containing the access token and other information
        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        HEROAPIResponseException
            If the API response is not parsable JSON
        Notes
        -----
        New in version 0.9.0
        """

        if application_id is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "application_id"'
            )
        if role_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "role_id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/tvm/{application_id}/token/{role_id}"

        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    # ─── Access Requests ──────────────────────────────────────────────────────

    def create_access_request(
        self,
        app_type=None,
        app_id=None,
        role=None,
        permission_set=None,
        subject=None,
        resource_type=None,
        resource_id=None,
    ):
        """
        Submits an access request for the given role on the given application.
        Auto-approves and grants permissions immediately if the user's email domain
        matches the app's allowedDomains list.

        Parameters
        ----------
        app_type : str, required
            The type of the app (e.g. 'data-repo', 'task-engine')
        app_id : str, required
            The ID of the app
        role : str, optional
            The role to request (defaults to 'viewer' if omitted)
        permission_set : list, optional
            The permission set to request
        subject : str, optional
            The subject of the access request
        resource_type : str, optional
            The type of the resource
        resource_id : str, optional
            The ID of the resource

        Returns
        -------
        access_request : dict
            The newly created access request entry

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing

        HEROAPIResponseException
            If the API response is not parsable JSON
        """
        if app_type is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_type"')
        if app_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/access-request/{app_type}/{app_id}"
        data = json.dumps(
            {
                "role": role,
                "permissionSet": permission_set,
                "subject": subject,
                "resourceType": resource_type,
                "resourceId": resource_id,
            }
        )

        try:
            response = self.api.request("POST", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def read_access_request(self, app_type=None, app_id=None, request_id=None):
        """
        Reads a single access request by ID.

        Parameters
        ----------
        app_type : str, required
            The type of the app
        app_id : str, required
            The ID of the app
        request_id : str, required
            The ID of the access request

        Returns
        -------
        access_request : dict

        Raises
        ------
        MissingRequiredAttribute
        HEROAPIResponseException
        """
        if app_type is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_type"')
        if app_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_id"')
        if request_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "request_id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/access-request/{app_type}/{app_id}/{request_id}"

        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def list_access_requests(self, app_type=None, app_id=None, status=None):
        """
        Lists all access requests for an application.

        Parameters
        ----------
        app_type : str, required
            The type of the app
        app_id : str, required
            The ID of the app
        status : str, optional
            Optional status filter (pending | approved | denied | revoked)

        Returns
        -------
        access_requests : list

        Raises
        ------
        MissingRequiredAttribute
        HEROAPIResponseException
        """
        if app_type is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_type"')
        if app_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/access-requests/{app_type}/{app_id}"
        params = {}
        if status:
            params["status"] = status

        try:
            response = self.api.request(
                "GET", url, headers=headers, params=params or None
            )
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def list_my_access_requests(self, status=None):
        """
        Lists all access requests submitted by the authenticated user.

        Parameters
        ----------
        status : str, optional
            Optional status filter (pending | approved | denied | revoked)

        Returns
        -------
        access_requests : list

        Raises
        ------
        HEROAPIResponseException
        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/access-requests/me"
        params = {}
        if status:
            params["status"] = status

        try:
            response = self.api.request(
                "GET", url, headers=headers, params=params or None
            )
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def update_access_request(
        self, app_type=None, app_id=None, request_id=None, status=None
    ):
        """
        Approves, denies, or revokes an access request.

        Parameters
        ----------
        app_type : str, required
            The type of the app
        app_id : str, required
            The ID of the app
        request_id : str, required
            The ID of the access request
        status : str, required
            New status: 'approved' | 'denied' | 'revoked'

        Returns
        -------
        access_request : dict

        Raises
        ------
        MissingRequiredAttribute
        HEROAPIResponseException
        """
        if app_type is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_type"')
        if app_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_id"')
        if request_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "request_id"')
        if status is None:
            raise MissingRequiredAttribute('Missing required attribute: "status"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/access-request/{app_type}/{app_id}/{request_id}"
        data = json.dumps({"status": status})

        try:
            response = self.api.request("PUT", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def delete_access_request(self, app_type=None, app_id=None, request_id=None):
        """
        Permanently deletes an access request record.

        Parameters
        ----------
        app_type : str, required
            The type of the app
        app_id : str, required
            The ID of the app
        request_id : str, required
            The ID of the access request

        Returns
        -------
        access_request : dict

        Raises
        ------
        MissingRequiredAttribute
        HEROAPIResponseException
        """
        if app_type is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_type"')
        if app_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_id"')
        if request_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "request_id"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/access-request/{app_type}/{app_id}/{request_id}"

        try:
            response = self.api.request("DELETE", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    # ─── Access Request Config ────────────────────────────────────────────────

    def list_access_request_configs(self):
        """
        Lists all access request configs across all applications.

        Returns
        -------
        configs : list

        Raises
        ------
        HEROAPIResponseException
        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/access-request/configs"

        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def create_access_request_config(
        self,
        app_type=None,
        app_id=None,
        resource_type=None,
        resource_id=None,
        allowed_domains=None,
        requestable_roles=None,
        schema_version=None,
    ):
        """
        Creates an access request config, scoped to the app or a specific resource within the app.

        Parameters
        ----------
        app_type : str, required
            The type of the app
        app_id : str, required
            The ID of the app
        resource_type : str, optional
            Optional resource type — defaults to app_type for an app-scoped config
        resource_id : str, optional
            Optional resource id — defaults to app_id for an app-scoped config
        allowed_domains : list, required
            List of email domains that are auto-approved (e.g. ['nrel.gov'])
        requestable_roles : list, required
            Role names users may request
        schema_version : int, optional
            Service-schema version for role resolution

        Returns
        -------
        config : dict

        Raises
        ------
        MissingRequiredAttribute
        HEROAPIResponseException
        """
        if app_type is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_type"')
        if app_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_id"')
        if allowed_domains is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "allowed_domains"'
            )
        if requestable_roles is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "requestable_roles"'
            )

        resolved_resource_type = resource_type if resource_type is not None else app_type
        resolved_resource_id = resource_id if resource_id is not None else app_id

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/access-request/{app_type}/{app_id}/{resolved_resource_type}/{resolved_resource_id}/config"
        data = json.dumps(
            {
                "allowedDomains": allowed_domains,
                "requestableRoles": requestable_roles,
                "schemaVersion": schema_version,
            }
        )

        try:
            response = self.api.request("POST", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def read_access_request_config(
        self,
        app_type=None,
        app_id=None,
        resource_type=None,
        resource_id=None,
    ):
        """
        Reads an access request config, scoped to the app or a specific resource within the app.

        Parameters
        ----------
        app_type : str, required
            The type of the app
        app_id : str, required
            The ID of the app
        resource_type : str, optional
            Optional resource type — defaults to app_type
        resource_id : str, optional
            Optional resource id — defaults to app_id

        Returns
        -------
        config : dict

        Raises
        ------
        MissingRequiredAttribute
        HEROAPIResponseException
        """
        if app_type is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_type"')
        if app_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_id"')

        resolved_resource_type = resource_type if resource_type is not None else app_type
        resolved_resource_id = resource_id if resource_id is not None else app_id

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/access-request/{app_type}/{app_id}/{resolved_resource_type}/{resolved_resource_id}/config"

        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def update_access_request_config(
        self,
        app_type=None,
        app_id=None,
        resource_type=None,
        resource_id=None,
        allowed_domains=None,
        requestable_roles=None,
        schema_version=None,
    ):
        """
        Replaces the config values for an access request config (app or resource-scoped).

        Parameters
        ----------
        app_type : str, required
            The type of the app
        app_id : str, required
            The ID of the app
        resource_type : str, optional
            Optional resource type — defaults to app_type
        resource_id : str, optional
            Optional resource id — defaults to app_id
        allowed_domains : list, required
            Updated list of email domains
        requestable_roles : list, required
            Updated list of requestable role names
        schema_version : int, optional
            Service-schema version for role resolution

        Returns
        -------
        config : dict

        Raises
        ------
        MissingRequiredAttribute
        HEROAPIResponseException
        """
        if app_type is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_type"')
        if app_id is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_id"')
        if allowed_domains is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "allowed_domains"'
            )
        if requestable_roles is None:
            raise MissingRequiredAttribute(
                'Missing required attribute: "requestable_roles"'
            )

        resolved_resource_type = resource_type if resource_type is not None else app_type
        resolved_resource_id = resource_id if resource_id is not None else app_id

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/access-request/{app_type}/{app_id}/{resolved_resource_type}/{resolved_resource_id}/config"
        data = json.dumps(
            {
                "allowedDomains": allowed_domains,
                "requestableRoles": requestable_roles,
                "schemaVersion": schema_version,
            }
        )

        try:
            response = self.api.request("PUT", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    # ─── Service Schema ───────────────────────────────────────────────────────

    def register_service_schema(
        self,
        app_type=None,
        version=None,
        permissions=None,
        roles=None,
        resource_types=None,
    ):
        """
        Registers or overwrites a service's permission and role schema with hero-auth-api.
        Requires the hero-auth/admin role or the REGISTER_SERVICE_SCHEMA OAuth scope.
        Intended to be called at deploy time from each service's deploy pipeline.

        Parameters
        ----------
        app_type : str, required
            The service identifier (e.g. 'data-repo', 'task-engine')
        version : int, required
            The schema version as a positive integer
        permissions : list, required
            Full list of permission strings the service defines
        roles : dict, optional
            Map of role names to permission subsets. Either roles or resource_types is required.
        resource_types : list, optional
            Resource type definitions. Either roles or resource_types is required.

        Returns
        -------
        schema : dict

        Raises
        ------
        MissingRequiredAttribute
        HEROAPIResponseException
        """
        if app_type is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_type"')
        if version is None:
            raise MissingRequiredAttribute('Missing required attribute: "version"')
        if permissions is None:
            raise MissingRequiredAttribute('Missing required attribute: "permissions"')
        if roles is None and resource_types is None:
            raise MissingRequiredAttribute(
                'Either "roles" or "resource_types" is required'
            )

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/service-schema/{app_type}/{version}"
        body = {"appType": app_type, "version": version, "permissions": permissions}
        if roles is not None:
            body["roles"] = roles
        if resource_types is not None:
            body["resourceTypes"] = resource_types
        data = json.dumps(body)

        try:
            response = self.api.request("POST", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def read_service_schema(self, app_type=None, version=None):
        """
        Reads the registered permission and role schema for a specific service version.

        Parameters
        ----------
        app_type : str, required
            The service identifier
        version : int, required
            The schema version as a positive integer

        Returns
        -------
        schema : dict

        Raises
        ------
        MissingRequiredAttribute
        HEROAPIResponseException
        """
        if app_type is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_type"')
        if version is None:
            raise MissingRequiredAttribute('Missing required attribute: "version"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/service-schema/{app_type}/{version}"

        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def list_service_schema_versions(self, app_type=None):
        """
        Lists all registered versions of a service's schema.

        Parameters
        ----------
        app_type : str, required
            The service identifier

        Returns
        -------
        schemas : list

        Raises
        ------
        MissingRequiredAttribute
        HEROAPIResponseException
        """
        if app_type is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_type"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/service-schema/{app_type}"

        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def delete_service_schema(self, app_type=None, version=None):
        """
        Deletes a specific versioned service schema.
        Requires the hero-auth/admin role or the REGISTER_SERVICE_SCHEMA OAuth scope.

        Parameters
        ----------
        app_type : str, required
            The service identifier
        version : int, required
            The schema version as a positive integer

        Returns
        -------
        schema : dict

        Raises
        ------
        MissingRequiredAttribute
        HEROAPIResponseException
        """
        if app_type is None:
            raise MissingRequiredAttribute('Missing required attribute: "app_type"')
        if version is None:
            raise MissingRequiredAttribute('Missing required attribute: "version"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/service-schema/{app_type}/{version}"

        try:
            response = self.api.request("DELETE", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def list_service_schemas(self):
        """
        Lists all registered service schemas across all appTypes and versions.

        Returns
        -------
        schemas : list

        Raises
        ------
        HEROAPIResponseException
        """
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/service-schemas"

        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def get_tvm_session(
        self,
        app_id=None,
        app_type=None,
        resource_id=None,
        resource_type=None,
        action=None,
    ):
        """
        Retrieves temporary AWS credentials from the Token Vending Machine (TVM) endpoint.

        Parameters
        ----------
        app_id : str, required
            The ID of the application
        app_type : str, required
            The type of the application
        resource_id : str, optional
            The ID of the specific resource. When provided with resource_type,
            enables fine-grained access control to specific resources.
        resource_type : str, optional
            The type of the resource. When provided with resource_id,
            enables fine-grained access control to specific resources.
        action : str, required
            The action to perform (e.g., 'readFile', 'executeQuery')

        Returns
        -------
        credentials : dict
        Temporary AWS credentials containing AccessKeyId, SecretAccessKey,
        SessionToken, and Expiration

        Raises
        ------
        MissingRequiredAttribute
            If a required attribute is missing
        HEROAPIResponseException
            If the API response is not parsable JSON
        """
        if app_id is None:
            raise MissingRequiredAttribute("Missing required attribute: 'app_id'")
        if app_type is None:
            raise MissingRequiredAttribute("Missing required attribute: 'app_type'")
        if action is None:
            raise MissingRequiredAttribute("Missing required attribute: 'action'")

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/tvm"

        params = {
            "applicationId": app_id,
            "applicationType": app_type,
            "action": action,
        }

        if resource_id is not None:
            params["resourceId"] = resource_id
        if resource_type is not None:
            params["resourceType"] = resource_type

        try:
            response = self.api.request("GET", url, headers=headers, params=params)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e
