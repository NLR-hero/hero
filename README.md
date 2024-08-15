# Hero

This is the Python client for Hero.

## Using the Hero client

### Installation

```
pip install git+https://github.nrel.gov/Hero/hero@0.9.0#egg=hero
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

## Monte's notes


Adding defaults and parameters

        read_project_by_name(self, datarepo_id, name, metatype="Project")

        add_project(self, datarepo_id, project_name, metatype="Project")

        read_dataset_by_name(self, datarepo_id, name, metatype="Dataset")

        def add_dataset(
            self, datarepo_id, project_id, dataset_name, metatype="Dataset", metadata={}
        ):

There is no json response in

        delete_project(self, datarepo_id, project_id) 
        delete_dataset...


The class level decorator makes it not possible to catch errors
@decorate_all(log_errors)

        try:
            project = data_repo.read_project_by_name(DATA_REPO_ID, "streaming")
        except HTTPError as err:
            print("catching error", err)
            project = data_repo.add_project(DATA_REPO_ID, "streaming")




