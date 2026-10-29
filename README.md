# HERO Python SDK

This is the Python SDK for HERO.

## Installation

The HERO team recommends using [uv](https://docs.astral.sh/uv/) to install and manage project dependencies.

### Using uv

```
uv add hero-sdk
```

### Using pip

```
pip install hero-sdk
```

## Development Installation and Release

First, clone this repo locally. Then install dependencies and pre-commit hooks:

```
uv sync
uv run pre-commit install
```

To run the tests:

Export test machine client credentials:
```
export HERO_ENV="dev"
export HERO_PROJECT="************"
export HERO_CLIENT_ID="************"
export HERO_CLIENT_SECRET="************"
```

Run:
```
uv run pytest test/
```

The values can also go in `test/.env` (gitignored), which the tests load when
`python-dotenv` is installed.

#### ML Model Registry tests

`test/test_ml_model_registry.py` and `test/test_ml_model_registry_mlflow.py` run
against the deployed dev API and the `[SEED]` data in the `hero-test-framework`
project (`HERO_PROJECT=hero-test-framework`). Writes go to throwaway experiments
and models that are deleted afterwards.

The MLflow suite drives real MLflow through `get_patched_mlflow()` (training,
logging, artifacts, logged models, registering, aliases, loading). It is skipped
unless `hero-mlflow`, `mlflow` and `scikit-learn` are installed; use an MLflow
version that matches the server:

```
uv venv .venv-mmr-test
uv pip install --python .venv-mmr-test/bin/python -e ".[dev]" \
    "hero-mlflow @ git+https://github.nlr.gov/Hero/hero-mlflow.git" \
    "mlflow==3.16.1" scikit-learn python-dotenv
.venv-mmr-test/bin/python -m pytest test/test_ml_model_registry.py test/test_ml_model_registry_mlflow.py
```

Tests marked `xfail` with a ticket key (HMR-248, HMR-250, HMR-253) document API
or edge bugs. Set `MMR_API_FIXES_DEPLOYED=1` once the API fixes are deployed so
those tests must pass.

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

Will be added in future.

In the mean time, the tests in the `test` directory of this repo may also prove useful for basic usage examples.

SWR 26-024
