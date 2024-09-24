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
        Creates a permission for the data repo
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
        Reads a permission for the data repo
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
        Reads the permissions of the data repo
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
        Updates a permission for the data repo
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
        Deletes a permission for the data repo
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

    def create_role(self, name=None, description=None):
        if name is None:
            raise MissingRequiredAttribute('Missing required attribute: "name"')

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
        if resource is None:
            raise MissingRequiredAttribute('Missing required attribute: "resource"')
        if scope is None:
            raise MissingRequiredAttribute('Missing required attribute: "scope"')

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
        if resource is None:
            raise MissingRequiredAttribute('Missing required attribute: "resource"')

        headers = self.get_headers(self.client.get_token())
        url = f"{self.base_url}/role/{resource}/{scope}"

        try:
            response = self.api.request("DELETE", url, headers=headers)
            return response.json()
        except JSONDecodeError:
            raise HEROAPIResponseException()
        except HTTPError as e:
            raise e



