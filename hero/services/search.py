import json
import os
from ..url_map import URL_MAP
from ..lib import ServiceBase, decorate_all, log_errors, get_conf_from_collection
from requests.exceptions import HTTPError, JSONDecodeError
from ..lib.errors import (
    MissingRequiredAttribute,
    HEROAPIResponseException,
    HERODataRepoProjectNotFound,
    HERODataRepoDatasetNotFound,
    HERODataRepoFileNotFound,
    HERODataRepoFileAlreadyExists,
    HERODataRepoDatasetAlreadyExists,
    HERODataRepoProjectAlreadyExists,
)
from ..lib.helpers import kwargs_to_json_for_request


@decorate_all(log_errors)
class SearchService(ServiceBase):

    def _configure(self):
        """
        Sets the API, adds basic information
        """
        # self.search_index = search_index
        self.search_api_url = get_conf_from_collection(URL_MAP, "HERO_SEARCH_API_URL")

    def msearch(self, search_index: str, ndjson_query: list):
        """
        Perform a multi-search query

        Parameters
        ----------
        search_index : str
            The index to be searched
        ndjson_query : list
            The query to be performed in NDJSON format (newline-delimited JSON).
            Each element in the list is a valid JSON object, interpersed of metadata and query JSON.
            If the metadata element is empty, the default index will be used.

        Returns
        -------
        search_results : json
            The results of the search query

        Raises
        ------
        HEROAPIResponseException
            If the API returns non-200 status code

        Examples
        --------
        ** Basic Usage **
        >>> search_service = SearchService(environment="test")
        >>> ndjson_query = [{},{"query": {"match_all": {}}}]
        >>> search_index = 'hero-data-repo-dev-chemcatbio-app'
        >>> search_service.msearch(search_index, ndjson_query)

        ** NOTE on NDJSON format **
        NDJSON is a newline-delimited JSON format. Each line is a valid JSON object.
        The body need to end with a new line character.

        ** NDJSON examples **
        The multi-search request body follows this pattern:
            Metadata\n
            Query\n
            Metadata\n
            Query\n
        Metadata lines include options, such as which indexes to search and the type of search.
        Query lines use the query DSL.
        User input is passed as a JSON object, and converted to NDJSON format before being sent to the API.

        - Basic keyword search
        [{},
        {"query": {"match": {"name": "test"}}}]

        - Basic list resources: list all resources, limit output to 10 results.
        [{},
        {"query":{"match_all":{}},"size": 10}]

        - List resources by resource type, e.g. only Projects or only Files
        [{},
        {"query": {"match": {"metatype": "Project"}}}]

        - List resources by specific metadata fields
        [{},
        {"query": {"match": {"metadata.format": "CSV"}}}]

        - Get resource aggregations by metadata fields: take average of the file size
        (This might now work with search_api for now, as aggs are not supported in permission insersion yet)
        [{},
        {"size":0, "aggs":{"avg_size":{"avg":{"field":"metadata.size"}}}}]

        """

        headers = self.get_headers(self.client.get_token())

        additional_headers = {
            "Content-Type": "Application/x-ndjson",
            "Accept": "Application/json",
        }
        headers.update(additional_headers)

        url = f"{self.search_api_url}/{search_index}/_msearch"

        # Generate NDJSON string
        ndjson_string = (
            "\n".join([json.dumps(action) for action in ndjson_query]) + "\n"
        )

        response = self.api.post(url, headers=headers, data=ndjson_string)

        if response.status_code != 200:
            raise HEROAPIResponseException
        return response.json()
