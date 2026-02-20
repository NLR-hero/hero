import json
from ..lib import ServiceBase, decorate_all, log_errors

@decorate_all(log_errors)
class AssistantService(ServiceBase):

    def _configure(self):
        """
        
        Parameters
        ----------
        data_repo : str
            The path to file output
        """
        self.data_repo = self.client.DataRepo(self.application_id)

    def download_state(self, file_path, file_resource):
        """
        Download state file from DataRepo to disk

        Parameters
        ----------
        file_path : str
            The path to file output

        file_resource : str
            The DataRepo file resource to upload state file to

        Returns
        -------
        file_resource : str
            The DataRepo new or updated file resource
        """
        self.data_repo.download_file_by_id(file_id=file_resource["id"], local_filepath=file_path)

    def upload_state(self, file_path, file_resource):
        """
        Upload state file to DataRepo

        Parameters
        ----------
        file_path : str
            The path to file output

        file_resource : str
            The DataRepo file resource to upload state file to

        Returns
        -------
        file_resource : str
            The DataRepo new or updated file resource
        """
        return self.data_repo.add_or_replace_file(
            dataset_id=file_resource["datasetId"],
            local_filepath=file_path,
            name=file_resource["name"]
        )
    
    def load_state(self, file_path="./state.json"):
        """
        Load state from disk for langchain

        Parameters
        ----------
        file_path : str
            The path to input file

        Returns
        -------
        state : array
            The set of LangChain messages
        """
        try:
            from langchain_core.messages import (
                messages_from_dict,
            )
        except ImportError as e:
            raise ImportError(
                "AssistantService requires the optional dependency 'langchain_core'.\n"
                "Install with: uv add langchain_core"
            ) from e
        
        try:
            with open(file_path, "r") as f:
                json_list = json.load(f)  # load the JSON list from file
        except FileNotFoundError:
            # If file doesn't exist, return empty state
            json_list = []

        return messages_from_dict(json_list)

    def save_state(self, state, file_path="./state.json"):
        """
        Save state from langchain to disk

        Parameters
        ----------
        state : array
            The set of LangChain messages
        
        file_path : str
            The path to file output

        Returns
        -------
        None

        """
        try:
            from langchain_core.messages import (
                messages_to_dict,
            )
        except ImportError as e:
            raise ImportError(
                "AssistantService requires the optional dependency 'langchain_core'.\n"
                "Install with: uv add langchain_core"
            ) from e
    
        try: 
            with open(file_path, "w") as f:
                json.dump(messages_to_dict(state), f, indent=2)
        except Exception as e:
            print(e)