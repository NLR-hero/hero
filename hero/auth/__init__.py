"""
Authentication is centrally managed by Amazon Cognito. Authorization depends on what you access and how you get to it. For direct access to AWS via boto3, AWS credentials are required. For access to the Hero API you will need the correct groups and scopes set in the Cognito User Pool.

Either way you access Hero, you will first need to sign into the user pool. For machine-to-machine auth, we follow the client creentials grant flow. You will need a CLIENT_ID, CLIENT_SECRET, and list of scopes.

To request a new app client with client id and client secret, contact us.

Scopes are used to grant access to specific API resources. Each scope follows a similar structure `<RESOURCE>/<THING>`, e.g. `hero-api/user` or `project/example`. These roles are request when you authenticate. For example:

```python
client_id = "MY_CLIENT_ID"
client_secret = "MY_CLIENT_SECRET"
scopes = ['hero-api/user', f'project/example']
access_token = hq.auth.get_token_from_cognito(client_id=client_id, client_secret=client_secret, scopes=scopes)
```

This generates a JWT access token which can be used to access Hero APIs or exchanged for to assume a specific IAM role. To assume an IAM role and use boto3 run:

```python
aws_credentials = hq.auth.assume_role(access_token)
```

Here, `aws_credentials` are your access keys to AWS. Use them as you would typically use AWS access keys.

"""
from . import cognito
from . import utils