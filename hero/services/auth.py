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
        Sets the API, adds data_repo id and required scope
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

