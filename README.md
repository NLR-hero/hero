# Hero

This is the Python client for Hero.

## Installation

```
pip install git+https://github.nrel.gov/Hero/hero@master#egg=hero
```

### Execute

You need to have the following environment variables defined.

```
export HERO_ENV=["dev", "stage", "prod"]
export HERO_PROJECT="aeroportal-app"
export HERO_CLIENT_ID="*******************************"
export HERO_CLIENT_SECRET="*******************************"
```

## Examples



## Development

```
pip install virtualenv
python -m virtualenv venv
source venv/bin/activate
python -m pip install --editable '.[dev]'
```



### Building Pdoc in CodeBuild

aws codebuild start-build \
--project-name "REDACTED_CODEBUILD_PROJECT" \
--source-version "scaling-nw" \
--buildspec-override "pdoc/buildspec.yml" \
--environment-variables-override \
name=GITHUB_TOKEN_ARN,value='arn:aws:secretsmanager:us-west-2:REDACTED_AWS_ACCOUNT_ID:secret:/nrel/github_packages/REDACTED_SECRET_PATH:GITHUB_TOKEN',type=PLAINTEXT \
name=DISTRIBUTION_ID,value=REDACTED_CF_DIST_ID,type=PLAINTEXT