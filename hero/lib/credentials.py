from ..client import HeroClient
from typing import Optional, Dict
import os

class HeroCredentialsProvider():
    """
    Provide AWS credentials through Hero's Token Vending Machine.
    """
    def __init__(self):
        self._hero_client = None
        self._auth = None
        self._initialize_hero_client()
    
    def _initialize_hero_client(self):
        try:
            self._hero_client = HeroClient()
            self._auth = self._hero_client.Auth()
            self._hero_client.authenticate()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Hero Client: {e}")
    
    def get_aws_credentials(
            self,
            app_id: str,
            app_type: str,
            action: str,
            resource_id: Optional[str] = None,
            resource_type: Optional[str] = None,
            aws_region: str = "us-west-2"
    ):
        """
        Retrieve temporary AWS credentials from Hero's TVM.

        Parameters
        ----------
        app_id : str, required
            The ID of the application
        app_type: str, required
            The type of application
        action : str, required
            The action to perform (e.g., 'readFile', 'executeQuery')
        resource_id : str, optional
            ID of the specific resource for fine-grained access control
        resource_type : str, optional
            Type of resource for fine-grained access control
        aws_region : str, optional
            AWS region for credentials ( default: 'us-west-2')
        
        Returns
        -------
        dict
            Dictionary containing access_key_id, secret_access_key, 
            session_token, region, and expiration
        """
        try:
            hero_response = self._auth.get_tvm_session(
                app_id=app_id,
                app_type=app_type,
                resource_id=resource_id,
                resource_type=resource_type,
                action=action
            )
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve credentials from Hero TVM: {e}")
        
        credentials = {
            'access_key_id': hero_response.get('AccessKeyId'),
            'secret_access_key': hero_response.get('SecretAccessKey'),
            'session_token': hero_response.get('SessionToken'),
            'region': aws_region,
            'expiration': hero_response.get('Expiration'),
        }

        return credentials
    
    def inject_into_env(self, credentials: Dict[str, str]):
        """
        Inject AWS Credentials into the environment variables

        Parameters
        ----------
        credentials : dict
            Credentials dictionary from get_aws_credentials()
        """
        os.environ['AWS_ACCESS_KEY_ID'] = credentials['access_key_id']
        os.environ['AWS_SECRET_ACCESS_KEY'] = credentials['secret_access_key']
        os.environ['AWS_SESSION_TOKEN'] = credentials['session_token']
        os.environ['AWS_REGION'] = credentials['region']