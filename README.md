# HERO Python SDK

This is the Python SDK for HERO.

## Using the HERO SDK

### Installation

```
pip install git+https://github.nrel.gov/Hero/hero@0.4.0#egg=hero
```

### Execute

You need to have the following environment variables defined.

```
export HERO_ENV=["dev", "stage", "prod"]
export HERO_PROJECT="aeroportal-app"
export HERO_CLIENT_ID="*******************************"
export HERO_CLIENT_SECRET="*******************************"
```

### Examples

Note: these are stale and need to be updated.

Please check out the [HERO examples](https://github.nrel.gov/Hero/hero-examples).



### Development: Local install / Editable Mode

#### Pip

```
pip install virtualenv
python -m virtualenv venv
source venv/bin/activate
python -m pip install --editable '.[dev]'
```

#### Poetry

When using Poetry to manage your Python environment + dependencies, you can do the following to install.

1. Clone this repo locally
2. Ensure you checkout the target branch you wish to work from (e.g. `git checkout THE-TARGET-BRANCH-YOU-WISH-TO-WORK-FROM`)
2. Open your project's `pyproject.toml` file
3. Add the `hero = {path="THE-PATH-TO-THE-NEWLY-CLONED-HERO-REPO", develop=true}` to your dependencies


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

## How to Release

- [] Update the version in `pyproject.toml`.
- [] Update the version in the Installation section in the README.
- [] Merge the working branch into main.
- [] Tag the main branch with the new version
- [] Push with tags
