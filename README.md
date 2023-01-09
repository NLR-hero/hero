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

    gantry create '{"name": "Example", "start_date": "2020-01-01", "number_of_months": 24}'


## TODO

Add notion of project
- Add resource_name to project table
- Allow latest resource if not specified
- Projects should have their own keys?

Should the image continue to process jobs?
- default param jobs==1, but it could be >1.
- Constrained jobs based on resource (eagle only, aws memory )

How big can our results be?
- super summary for BTMS
- 256 MB limit
- May need s3

What about a prophet example for the template?
- Adds data to docker
- Must train and predict...
- Nice plots, even from matplotlib.



