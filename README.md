# Gantry

## Install

    conda env create
    conda activate gantry
    python setup.py develop

## Running

You will need to assign the following environment variables:

    export GANTRY_JOB_ID="******"
    export GANTRY_BASE_API_URL="https://********.execute-api.us-west-2.amazonaws.com/dev"
    export GANTRY_AUTH_URL="https://dev-nrel-research.auth.us-west-2.amazoncognito.com/oauth2/token"
    export GANTRY_APP_CLIENT="********"

    export GANTRY_RESOURCE_NAME="harbor.nrel.gov/dav-data-library/hero_dev_template:0.0.1"

Then you can test `gantry` using the command line interface.

    gantry list

    gantry remove

    gantry create '{ "name": "Example hero job", "param_1": 10, "param_2": 20, "param_3": 30}'

