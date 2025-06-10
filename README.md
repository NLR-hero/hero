# HERO Python SDK

This is the Python SDK for HERO.

## Installation

The HERO team recommends using [poetry](https://python-poetry.org/) or [pip](https://pypi.org/project/pip/) to install and manage project dependencies.


### Using Poetry

```
poetry add git+https://github.nrel.gov/Hero/hero@v0.9.0
```


### Using Pip


```
pip install git+https://github.nrel.gov/Hero/hero@v0.9.0#egg=hero
```

## Development Installation and Release

Similar to above, during development we currently support using [poetry](https://python-poetry.org/) or [pip](https://pypi.org/project/pip/) to install and manage project dependencies for local development. Both have their advantages/trade offs. We will outline specific installation options below.

First, clone this repo locally. Then...

### Using Poetry

Next, install the dependencies, and the pre-commit hooks.

- `poetry install`
- `poetry run pre-commit install`

To run the tests, execute the following

- `poetry shell` (ensure you are in the Poetry shell)
- `./run_test.sh`

If you wish to link the local HERO codebase to a project for feature development, testing, etc., you may do the following. The below assumes you are using poetry for the consuming application(s).

- Ensure you checkout the target branch you wish to work from in this repository (e.g. `git checkout THE-TARGET-BRANCH-YOU-WISH-TO-WORK-FROM`)
- Open your _consuming_ project's `pyproject.toml` file
- Add the `hero = {path="THE-PATH-TO-THE-NEWLY-CLONED-HERO-REPO", develop=true}` to your dependencies. The _develop_ flag will ensure updates to this codebase are reflected in the consuming application.


### Using Pip

Next, install the dependencies, and the pre-commit hooks.
- `pip install virtualenv`
- `python -m virtualenv venv`
- `source venv/bin/activate`
- `pip install`
- `pre-commit install`

To run the tests, execute the following

- `./run_test.sh`

When using Poetry to manage your Python environment + dependencies, you can do the following to install.

1. Clone this repo locally
2. Ensure you checkout the target branch you wish to work from (e.g. `git checkout THE-TARGET-BRANCH-YOU-WISH-TO-WORK-FROM`)
2. Open your project's `pyproject.toml` file
3. Add the `hero = {path="THE-PATH-TO-THE-NEWLY-CLONED-HERO-REPO", develop=true}` to your dependencies

If you wish to link the local HERO codebase to a project for feature development, testing, etc., you may do the following.

**TODO: ADD/UPDATE pip details below. Something akin to the following!!**

```
pip install virtualenv
python -m virtualenv venv
source venv/bin/activate
python -m pip install --editable '.[dev]'
```

### Releasing a New Version

Once development is complete on a given feature/bugfix/etc, pleaes do the following to tag a new release.
- Update the version in `pyproject.toml`.
- Update the version in the Installation section(s) in the `README.md` (this file).
- Add and commit the changes made in the above two steps.
- Perform a non fast-forward the working branch into main
    - `git checkout main`
    - `git merge --no-ff THE-BRANCH-NAME-YOU-ARE-MERGING`.
- Tag the main branch with the new version via `git tag THE-NEW-VERSION-NUMBER`
- Push with tags `git push && git push --tags`


## Usage

You need to have the following environment variables defined.

```
export HERO_ENV=["dev", "stage", "prod"]
export HERO_PROJECT="aeroportal-app"
export HERO_CLIENT_ID="*******************************"
export HERO_CLIENT_SECRET="*******************************"
```

### Examples

~~Please check out the [HERO examples](https://github.nrel.gov/Hero/hero-examples).~~

_Note: the above examples are stale and need to be updated. Please refer to the tests in the `test` directory for basic usage examples._
