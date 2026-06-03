# HERO Python SDK

This is the Python SDK for HERO.

## Installation

The HERO team recommends using [uv](https://docs.astral.sh/uv/) to install and manage project dependencies.

### Using uv

```
uv add https://github.nrel.gov/Hero/hero/archive/refs/tags/v0.13.0.zip
```

### Using pip

```
pip install git+https://github.nrel.gov/Hero/hero@v0.13.0#egg=hero
```

## Development Installation and Release

First, clone this repo locally. Then install dependencies and pre-commit hooks:

```
uv sync
uv run pre-commit install
```

To run the tests:

```
./run_test.sh
```

To link the local HERO codebase into a consuming project for feature development:

- Checkout the target branch in this repo
- In your consuming project, run `uv add --editable THE-PATH-TO-THE-NEWLY-CLONED-HERO-REPO`

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

Please check out the [HERO examples](https://github.com/nrel-hero/hero-examples).

Additionally, the tests in the `test` directory of this repo may also prove useful for basic usage examples.

SWR 26-024
