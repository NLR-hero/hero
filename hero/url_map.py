
URL_MAP = {
    'dev': {
        'HERO_TASK_ENGINE_API_URL': 'https://dev-hero.nrel.gov/task-engine/api/v1',
        'HERO_DATA_REPO_API_URL': 'https://dev-hero.nrel.gov/data-repo/api/v1',
        'HERO_SEARCH_API_URL': 'https://dev-hero.nrel.gov/search/api/v1',
        'HERO_AUTH_API_URL': 'https://dev-hero.nrel.gov/auth/api/v1',
        'HERO_COGNITO_API_URL': 'https://dev-nrel-research.auth.us-west-2.amazoncognito.com/oauth2/token',
        'HERO_M3S_TRACKER_URL': 'https://REDACTED_APIGW_ID.execute-api.us-west-2.amazonaws.com/dev/m3s/api/v1/proxy',
    },
    'stage': {
        'HERO_TASK_ENGINE_API_URL': 'https://stage-hero.nrel.gov/task-engine/api/v1',
        'HERO_DATA_REPO_API_URL': 'https://stage-hero.nrel.gov/data-repo/api/v1',
        'HERO_SEARCH_API_URL': 'https://stage-hero.nrel.gov/search/api/v1',
        'HERO_AUTH_API_URL': 'https://stage-hero.nrel.gov/auth/api/v1',
        'HERO_COGNITO_API_URL': 'https://stage-nrel-research.auth.us-west-2.amazoncognito.com/oauth2/token',
        'HERO_M3S_TRACKER_URL': 'https://REDACTED_APIGW_ID.execute-api.us-west-2.amazonaws.com/dev/m3s/api/v1/proxy',

    },
    'production': {
        'HERO_TASK_ENGINE_API_URL': 'https://hero.nrel.gov/task-engine/api/v1',
        'HERO_DATA_REPO_API_URL': 'https://hero.nrel.gov/data-repo/api/v1',
        'HERO_SEARCH_API_URL': 'https://hero.nrel.gov/search/api/v1',
        'HERO_AUTH_API_URL': 'https://hero.nrel.gov/auth/api/v1',
        'HERO_COGNITO_API_URL': 'https://nrel-research.auth.us-west-2.amazoncognito.com/oauth2/token',
        'HERO_M3S_TRACKER_URL': 'https://REDACTED_APIGW_ID.execute-api.us-west-2.amazonaws.com/dev/m3s/api/v1/proxy',

    },
}