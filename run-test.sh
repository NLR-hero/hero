export HERO_ENV="dev"
export HERO_PROJECT="aeroportal-app"
export HERO_CLIENT_ID="REDACTED_CLIENT_ID"
export HERO_CLIENT_SECRET="REDACTED_CLIENT_SECRET"
# export HERO_RESILIENT_SESSION=true
# export HERO_M3S_TRACKER_URL="http://localhost:8010/m3s/api/v1"

poetry run pytest -s

unset HERO_ENV
unset HERO_PROJECT
unset HERO_CLIENT_ID
unset HERO_CLIENT_SECRET
# unset HERO_RESILIENT_SESSION