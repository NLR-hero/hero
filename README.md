# Gantry

This is for testing the scaling version of `hero`.

## Install

    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    python setup.py develop

## Execute

You need to have the following environment variables defined.


        export HERO_PROJECT="test-project"
        export HERO_QUEUE="queue-001"
        export HERO_QUEUE_VISIBILITY_TIMEOUT=300

        export HERO_DATABASE_PASSWORD=""

        export AWS_DEFAULT_OUTPUT=json
        export AWS_DEFAULT_REGION=us-west-2

        export AWS_ACCESS_KEY_ID=""
        export AWS_SECRET_ACCESS_KEY=""
        export AWS_SESSION_TOKEN=""

On eagle, you'll need to load the following modules.

        module load openmpi




