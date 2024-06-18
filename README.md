# Hero

This is the Python client for Hero.

Please check out the [HERO examples](https://github.nrel.gov/Hero/hero-examples).

## Installation

```
pip install git+https://github.nrel.gov/Hero/hero@main#egg=hero
```

### Execute

You need to have the following environment variables defined.

```
export HERO_ENV=["dev", "stage", "prod"]
export HERO_PROJECT="aeroportal-app"
export HERO_CLIENT_ID="*******************************"
export HERO_CLIENT_SECRET="*******************************"
```

## Development

```
pip install virtualenv
python -m virtualenv venv
source venv/bin/activate
python -m pip install --editable '.[dev]'
```

## Using Poetry

To start the shell and install any packages (note, Poetry will create a local .venv for you if one does not exist)

```
poetry shell
poetry install
```

(develop as normal)

To deactivate the poetry shell

```
deactivate
```




export HERO_ENV="dev"
export HERO_PROJECT="aeroportal-app"
export HERO_CLIENT_ID="1c5ngb6o6lvtdfkus0sflstdq4"
export HERO_CLIENT_SECRET="102hhfk1bdvc7cu307s15ljkda56hhc09qh4cp3b9hj6juhf5"

export HERO_RESILIENT_SESSION=true

hero
    requests
    config
    errors
    logging
    DataRepo
    TaskEngine
    M3s

