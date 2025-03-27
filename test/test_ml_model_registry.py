import hero

TESTABLE_EXPERIMENT_ID = "1"
TESTABLE_RUN_ID = "c863ba10af2143129a31f2ceecf9d66d"

# def test_tracking_uri():
#     hero_client = hero.HeroClient()
#     model_registry = hero_client.MLModelRegistry()
#     uri = model_registry.get_tracking_uri()
#     assert uri == 'https://REDACTED_APIGW_ID.execute-api.us-west-2.amazonaws.com/dev/m3s/api/v1/proxy/sandbox-m3s'


def test_list_experiments():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()
    res = model_registry.list_experiments()
    assert isinstance(res, list)
    assert len(res) > 0


def test_read_experiment():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()
    res = model_registry.read_experiment(TESTABLE_EXPERIMENT_ID)
    assert isinstance(res, dict)
    assert res["id"] == TESTABLE_EXPERIMENT_ID


def test_list_runs():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()
    res = model_registry.list_runs(TESTABLE_EXPERIMENT_ID)
    assert isinstance(res, list)
    assert len(res) > 0


def test_read_run():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()
    res = model_registry.read_run(TESTABLE_RUN_ID)
    assert isinstance(res, dict)
    assert res["id"] == TESTABLE_RUN_ID


def test_list_artifacts():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()
    res = model_registry.list_artifacts(TESTABLE_RUN_ID)
    assert isinstance(res, list)
    assert len(res) > 0
