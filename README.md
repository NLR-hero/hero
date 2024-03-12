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

Please clone and run the  [HERO examples](https://github.nrel.gov/Hero/hero-examples).


## Development

```
pip install virtualenv
python -m virtualenv venv
source venv/bin/activate
python -m pip install --editable '.[dev]'
```
