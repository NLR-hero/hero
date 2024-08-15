import hero

TESTABLE_PROJECT_ID = 'sandbox-m3s'
TESTABLE_EXPERIMENT_ID = '2'
TESTABLE_RUN_ID = '65c9112de0084b208f85b91010fe4c12'

# def test_tracking_uri():
#     hero_client = hero.HeroClient()
#     model_registry = hero_client.MLModelRegistry(TESTABLE_PROJECT_ID)
#     hero_client.authenticate()
#     uri = model_registry.get_tracking_uri()
#     assert uri == 'https://REDACTED_APIGW_ID.execute-api.us-west-2.amazonaws.com/dev/m3s/api/v1/proxy/sandbox-m3s'

def test_read_experiment():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry(TESTABLE_PROJECT_ID)
    hero_client.authenticate()
    res = model_registry.read_experiment(TESTABLE_EXPERIMENT_ID)
    assert res['experiment']['experiment_id'] == TESTABLE_EXPERIMENT_ID

def test_read_run():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry(TESTABLE_PROJECT_ID)
    hero_client.authenticate()
    res = model_registry.read_run(TESTABLE_RUN_ID)
    assert res['run']['info']['run_id'] == TESTABLE_RUN_ID

def test_list_artifacts():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry(TESTABLE_PROJECT_ID)
    hero_client.authenticate()
    res = model_registry.list_artifacts(TESTABLE_RUN_ID)
    assert len(res) == 10
