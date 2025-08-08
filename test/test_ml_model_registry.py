import hero

TESTABLE_PROJECT_ID = "dev-hero-test-framework"
TESTABLE_EXPERIMENT_ID = "2"
TESTABLE_RUN_ID = "18c463a886dd46bd8b4b2bf19408b36c"
TESTABLE_MODEL_ID = "30JRWKZ4gEYZRIGY3OGMg7oQWH5"
TESTABLE_MODEL_VERSION_ID = "1"

# def test_tracking_uri():
#     hero_client = hero.HeroClient()
#     model_registry = hero_client.MLModelRegistry()
#     uri = model_registry.get_tracking_uri()
#     assert uri == 'https://REDACTED_APIGW_ID.execute-api.us-west-2.amazonaws.com/dev/m3s/api/v1/proxy/sandbox-m3s'


def test_list_experiments():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()
    res = model_registry.list_experiments()
    assert len(res) > 0
    assert isinstance(res, dict)
    assert isinstance(res.get("experiments"), list)


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
    assert len(res) > 0
    assert isinstance(res, dict)
    assert isinstance(res.get("runs"), list)


def test_list_runs_with_filter():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    filter_expr = "metrics.`r2` > 0.5"
    res = model_registry.list_runs(TESTABLE_EXPERIMENT_ID, filter=filter_expr)

    assert isinstance(res, dict)
    assert isinstance(res.get("runs"), list)
    assert all("metrics" in run or "params" in run for run in res.get("runs"))


def test_list_runs_missing_experiment_id():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    try:
        model_registry.list_runs(None)
    except Exception as e:
        assert str(e) == 'Missing required attribute: "experiment_id"'
    else:
        assert False, "Expected MissingRequiredAttribute exception"


def test_read_run():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()
    res = model_registry.read_run(TESTABLE_EXPERIMENT_ID, TESTABLE_RUN_ID)
    assert isinstance(res, dict)
    assert res["id"] == TESTABLE_RUN_ID


def test_list_artifacts():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()
    res = model_registry.list_artifacts(TESTABLE_EXPERIMENT_ID, TESTABLE_RUN_ID)
    assert isinstance(res, list)
    assert len(res) > 0


def test_list_models():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()
    res = model_registry.list_models(TESTABLE_PROJECT_ID)
    assert isinstance(res, dict)
    assert isinstance(res.get("registered_models"), list)


def test_read_model():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()
    res = model_registry.read_model(TESTABLE_MODEL_ID)
    assert isinstance(res, dict)
    assert res["name"] == TESTABLE_MODEL_ID


def test_update_model():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    # get original model
    original_model = model_registry.read_model(TESTABLE_MODEL_ID)
    original_description = original_model["description"]
    updated_description = "Updated Description"

    # update model with new values
    updated_model = model_registry.update_model(
        TESTABLE_MODEL_ID, description=updated_description
    )
    assert isinstance(updated_model, dict)
    assert updated_model["description"] == updated_description

    # reset model to original values
    reset_model = model_registry.update_model(
        TESTABLE_MODEL_ID, description=original_description
    )
    assert isinstance(reset_model, dict)
    assert reset_model["description"] == original_description
