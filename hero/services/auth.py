import json
import os
from ..url_map import URL_MAP
from ..lib import ServiceBase, decorate_all, log_errors, get_conf_from_collection
from requests.exceptions import HTTPError, JSONDecodeError
from ..lib.errors import MissingRequiredAttribute, HEROAPIResponseException
from ..lib.helpers import kwargs_to_json_for_request

# @decorate_all(log_errors)
class AuthService(ServiceBase):

    def _configure(self):
        """
        Sets the API, adds required scope
        """
        self.client.add_scope("hero-auth/user")
        self.base_url = get_conf_from_collection(URL_MAP, "HERO_AUTH_API_URL")

    def create_permission(self, appType=None, appId=None, principalType=None, principalId=None, resourceType=None, resourceId=None, permissionSet=None):
        """
        Creates a permission for the given app, principal, and resource

        Parameters
        ----------
        appType : str, required
            The type of the app
        appId : str, required
            The ID of the app
        principalType : str, required
            The type of the principal
        principalId : str, required
            The ID of the principal
        resourceType : str, required
            The type of the resource
        resourceId : str, required
            The ID of the resource
        permissionSet : list, required
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

        if appType is None:
            raise MissingRequiredAttribute('Missing required attribute: "appType"')
        if appId is None:
            raise MissingRequiredAttribute('Missing required attribute: "appId"')
        if principalType is None:
            raise MissingRequiredAttribute('Missing required attribute: "principalType"')
        if principalId is None:
            raise MissingRequiredAttribute('Missing required attribute: "principalId"')
        if resourceType is None:
            raise MissingRequiredAttribute('Missing required attribute: "resourceType"')
        if resourceId is None:
            raise MissingRequiredAttribute('Missing required attribute: "resourceId"')
        if permissionSet is None:
            raise MissingRequiredAttribute('Missing required attribute: "permissionSet"')

        attributes = {
            "permissionSet": permissionSet
        }

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/permission/{appType}/{appId}/{principalType}/{principalId}/{resourceType}/{resourceId}"
        data = json.dumps(attributes)

        try:
            response = self.api.request("POST", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def read_permission(self, appType=None, appId=None, principalType=None, principalId=None, resourceType=None, resourceId=None):
        """
        Reads a permission for the given app, principal, and resource

        Parameters
        ----------
        appType : str, required
            The type of the app
        appId : str, required
            The ID of the app
        principalType : str, required
            The type of the principal
        principalId : str, required
            The ID of the principal
        resourceType : str, required
            The type of the resource
        resourceId : str, required
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

        if appType is None:
            raise MissingRequiredAttribute('Missing required attribute: "appType"')
        if appId is None:
            raise MissingRequiredAttribute('Missing required attribute: "appId"')
        if principalType is None:
            raise MissingRequiredAttribute('Missing required attribute: "principalType"')
        if principalId is None:
            raise MissingRequiredAttribute('Missing required attribute: "principalId"')
        if resourceType is None:
            raise MissingRequiredAttribute('Missing required attribute: "resourceType"')
        if resourceId is None:
            raise MissingRequiredAttribute('Missing required attribute: "resourceId"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/permission/{appType}/{appId}/{principalType}/{principalId}/{resourceType}/{resourceId}"

        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def read_permissions(self, appType=None, appId=None):
        """
        Reads and returns a collection of permissions in the given app, principal, and resource

        Parameters
        ----------
        appType : str, required
            The type of the app
        appId : str, required
            The ID of the app

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

        if appType is None:
            raise MissingRequiredAttribute('Missing required attribute: "appType"')
        if appId is None:
            raise MissingRequiredAttribute('Missing required attribute: "appId"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/permissions/{appType}/{appId}"

        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def update_permission(self, appType=None, appId=None, principalType=None, principalId=None, resourceType=None, resourceId=None, permissionSet=None):
        """
        Updates a permission for the given app, principal, and resource

        Parameters
        ----------
        appType : str, required
            The type of the app
        appId : str, required
            The ID of the app
        principalType : str, required
            The type of the principal
        principalId : str, required
            The ID of the principal
        resourceType : str, required
            The type of the resource
        resourceId : str, required
            The ID of the resource
        permissionSet : list, required
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

        if appType is None:
            raise MissingRequiredAttribute('Missing required attribute: "appType"')
        if appId is None:
            raise MissingRequiredAttribute('Missing required attribute: "appId"')
        if principalType is None:
            raise MissingRequiredAttribute('Missing required attribute: "principalType"')
        if principalId is None:
            raise MissingRequiredAttribute('Missing required attribute: "principalId"')
        if resourceType is None:
            raise MissingRequiredAttribute('Missing required attribute: "resourceType"')
        if resourceId is None:
            raise MissingRequiredAttribute('Missing required attribute: "resourceId"')
        if permissionSet is None:
            raise MissingRequiredAttribute('Missing required attribute: "permissionSet"')

        attributes = {
            "permissionSet": permissionSet
        }
        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/permission/{appType}/{appId}/{principalType}/{principalId}/{resourceType}/{resourceId}"
        data = json.dumps(attributes)

        try:
            response = self.api.request("PUT", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def delete_permission(self, appType=None, appId=None, principalType=None, principalId=None, resourceType=None, resourceId=None):
        """
        Deletes a permission for the given app, principal, and resource

        Parameters
        ----------
        appType : str, required
            The type of the app
        appId : str, required
            The ID of the app
        principalType : str, required
            The type of the principal
        principalId : str, required
            The ID of the principal
        resourceType : str, required
            The type of the resource
        resourceId : str, required
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

        if appType is None:
            raise MissingRequiredAttribute('Missing required attribute: "appType"')
        if appId is None:
            raise MissingRequiredAttribute('Missing required attribute: "appId"')
        if principalType is None:
            raise MissingRequiredAttribute('Missing required attribute: "principalType"')
        if principalId is None:
            raise MissingRequiredAttribute('Missing required attribute: "principalId"')
        if resourceType is None:
            raise MissingRequiredAttribute('Missing required attribute: "resourceType"')
        if resourceId is None:
            raise MissingRequiredAttribute('Missing required attribute: "resourceId"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/permission/{appType}/{appId}/{principalType}/{principalId}/{resourceType}/{resourceId}"

        try:
            response = self.api.request("DELETE", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def create_user(self, username=None, name=None, email=None, roles=None):
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
        data = json.dumps({
            "username": username,
            "name": name,
            "email": email,
            "roles": roles
        })

        try:
            response = self.api.request("POST", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def list_users(self, count=20, nextToken=None, filterKey=None, filterVal=None):
        """
        Lists and returns a collection of users

        Parameters
        ----------
        count : int, optional
            The number of users to return
        nextToken : str, optional
            The next token for pagination
        filterKey : str, optional
            An optional key to filter by. Note: this is required if filterVal is provided
        filterVal : str, optional
            An optional value to filter by. Note: this is required if filterKey is provided

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
        if nextToken:
            params["nextToken"] = nextToken
        if filterKey and filterVal:
            params["filterKey"] = filterKey
            params["filterVal"] = filterVal

        try:
            response = self.api.request("GET", url, headers=headers, params=params)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def read_user(self, username=None):
        """
        Reads and returns a user

        Parameters
        ----------
        username : str, required
            The unique username of the user.

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

        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def update_user(self, username=None, enabled=None, roles=None):
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
        data = json.dumps(data)

        try:
            response = self.api.request("PUT", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def delete_user(self, username=None):
        """
        Deletes and returns a user

        Parameters
        ----------
        username : str, required
            The unique username of the user.

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

        try:
            response = self.api.request("DELETE", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def create_machine(self, name=None, roles=None, generateSecret=None, callbackUrls=None, logoutUrls=None):
        """
        Creates a new machine client

        Parameters
        ----------
        name : str, required
            The name of the machine
        roles : list, required
            The roles of the machine
        generateSecret : bool, optional
            Whether to generate a secret for the machine
        callbackUrls : list, optional
            The callback URLs for the machine
        logoutUrls : list, optional
            The logout URLs for the machine

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
        data = json.dumps({
            "name": name,
            "roles": roles,
            "generateSecret": generateSecret,
            "callbackUrls": callbackUrls,
            "logoutUrls": logoutUrls
        })

        try:
            response = self.api.request("POST", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def list_machines(self, count=20, nextToken=None):
        """
        Returns a list of machine clients

        Parameters
        ----------
        count : int, optional
            The number of machines to return
        nextToken : str, optional
            The next token for pagination

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
        if nextToken:
            params["nextToken"] = nextToken

        try:
            response = self.api.request("GET", url, headers=headers, params=params)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def read_machine(self, id=None):
        """
        Reads and returns a machine client

        Parameters
        ----------
        id: str, required
            The unique ID of the machine client

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

        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def update_machine(self, id=None, name=None, roles=None, generateSecret=None, callbackUrls=None, logoutUrls=None):
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
        generateSecret : bool, optional
            Whether to generate a secret for the machine
        callbackUrls : list, optional
            The callback URLs for the machine
        logoutUrls : list, optional
            The logout URLs for the machine

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
        data = json.dumps({
            "name": name,
            "roles": roles,
            "generateSecret": generateSecret,
            "callbackUrls": callbackUrls,
            "logoutUrls": logoutUrls
        })

        try:
            response = self.api.request("PUT", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def delete_machine(self, id=None):
        """
        Deletes a machine client

        Parameters
        ----------
        id: str, required
            The unique ID of the machine client

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

        try:
            response = self.api.request("DELETE", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def create_role(self, resource=None, scope=None, description=None):
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

        data = json.dumps({
            "name": name,
            "description": description
        })

        try:
            response = self.api.request("POST", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def list_roles(self, count=20, nextToken=None):
        """
        Reads and returns a collection of role entries

        Parameters
        ----------
        count : int, optional
            The number of roles to return
        nextToken : str, optional
            The next token for pagination

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
        if nextToken:
            params["nextToken"] = nextToken

        try:
            response = self.api.request("GET", url, headers=headers, params=params)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def read_role(self, resource=None, scope=None):
        """
        Reads and returns a role

        Parameters
        ----------
        resource : str, required
            The resource this role is for
        scope : str, required
            The scope this role covers for the given resource

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

        try:
            response = self.api.request("GET", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e

    def update_role(self, resource=None, scope=None, description=None):
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
        data = json.dumps({
            "description": description
        })

        try:
            response = self.api.request("PUT", url, headers=headers, data=data)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e


    def delete_role(self, resource=None, scope=None):
        """
        Deletes a role

        Parameters
        ----------
        resource : str, required
            The resource this role is for
        scope : str, required
            The scope this role covers for the given resource

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

        try:
            response = self.api.request("DELETE", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e



