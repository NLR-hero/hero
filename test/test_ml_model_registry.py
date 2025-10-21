import hero

TESTABLE_PROJECT_ID = "dev-hero-test-framework"
TESTABLE_EXPERIMENT_ID = "2"
TESTABLE_RUN_ID = "18c463a886dd46bd8b4b2bf19408b36c"
TESTABLE_MODEL_ID = "Test Experiment 1"
TESTABLE_MODEL_VERSION_ID = "1"


def get_tag_map(ob):
    tags = ob.get("tags", [])
    tags_map = {}
    for tag in tags:
        tags_map[tag["key"]] = tag["value"]
    return tags_map


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


def test_update_experiment():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    # get original experiment
    original_experiment = model_registry.read_experiment(TESTABLE_EXPERIMENT_ID)
    original_name = original_experiment["name"]
    updated_name = "Updated Experiment Name"
    original_description = original_experiment.get("description", "")
    updated_description = "Updated Description"

    # update experiment with new values
    updated_experiment = model_registry.update_experiment(
        TESTABLE_EXPERIMENT_ID,
        name=updated_name,
        description=updated_description,
    )
    assert isinstance(updated_experiment, dict)
    assert updated_experiment["name"] == updated_name
    assert updated_experiment["description"] == updated_description

    # reset experiment to original values
    reset_experiment = model_registry.update_experiment(
        TESTABLE_EXPERIMENT_ID,
        name=original_name,
        description=original_description,
    )
    assert isinstance(reset_experiment, dict)
    assert reset_experiment["name"] == original_name
    assert reset_experiment["description"] == original_description


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


def test_update_run():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    # get original run
    original_run = model_registry.read_run(TESTABLE_EXPERIMENT_ID, TESTABLE_RUN_ID)
    original_name = original_run["name"]
    updated_name = "Updated Run Name"
    original_description = original_run["description"]
    updated_description = "Updated Description"

    # update run with new values
    updated_run = model_registry.update_run(
        TESTABLE_EXPERIMENT_ID,
        TESTABLE_RUN_ID,
        name=updated_name,
        description=updated_description,
    )
    assert isinstance(updated_run, dict)
    assert updated_run["name"] == updated_name
    assert updated_run["description"] == updated_description

    # reset run to original values
    reset_run = model_registry.update_run(
        TESTABLE_EXPERIMENT_ID,
        TESTABLE_RUN_ID,
        name=original_name,
        description=original_description,
    )
    assert isinstance(reset_run, dict)
    assert reset_run["name"] == original_name
    assert reset_run["description"] == original_description


def test_list_artifacts():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()
    res = model_registry.list_artifacts(TESTABLE_EXPERIMENT_ID, TESTABLE_RUN_ID)
    assert isinstance(res, list)
    assert len(res) > 0


def test_list_registered_models():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()
    res = model_registry.list_registered_models(TESTABLE_PROJECT_ID)
    assert isinstance(res, dict)
    assert isinstance(res.get("registered_models"), list)


def test_read_registered_model():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()
    res = model_registry.read_registered_model(TESTABLE_MODEL_ID)
    assert isinstance(res, dict)
    assert res["name"] == TESTABLE_MODEL_ID


def test_update_registered_model():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    # get original model
    original_model = model_registry.read_registered_model(TESTABLE_MODEL_ID)
    original_description = original_model["description"]
    updated_description = "Updated Description"

    # update model with new values
    updated_model = model_registry.update_registered_model(
        TESTABLE_MODEL_ID, description=updated_description
    )
    assert isinstance(updated_model, dict)
    assert updated_model["description"] == updated_description

    # reset model to original values
    reset_model = model_registry.update_registered_model(
        TESTABLE_MODEL_ID, description=original_description
    )
    assert isinstance(reset_model, dict)
    assert reset_model["description"] == original_description


def test_update_registered_model_tag():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()
    key = "test-key"
    value = "test-value"

    model_registry.update_registered_model_tag(TESTABLE_MODEL_ID, key, value)
    model = model_registry.read_registered_model(TESTABLE_MODEL_ID)
    tags_map = get_tag_map(model)
    assert tags_map.get(key) == value
    model_registry.delete_registered_model_tag(TESTABLE_MODEL_ID, key)
    model = model_registry.read_registered_model(TESTABLE_MODEL_ID)
    tags_map = get_tag_map(model)
    assert key not in tags_map


def test_update_registered_model_version_tag():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()
    key = "test-key"
    value = "test-value"

    model_registry.update_registered_model_version_tag(
        TESTABLE_MODEL_ID, TESTABLE_MODEL_VERSION_ID, key, value
    )
    version = model_registry.read_registered_model_version(
        TESTABLE_MODEL_ID, TESTABLE_MODEL_VERSION_ID
    )
    tags_map = get_tag_map(version)
    assert tags_map.get(key) == value
    model_registry.delete_registered_model_version_tag(
        TESTABLE_MODEL_ID, TESTABLE_MODEL_VERSION_ID, key
    )
    version = model_registry.read_registered_model_version(
        TESTABLE_MODEL_ID, TESTABLE_MODEL_VERSION_ID
    )
    tags_map = get_tag_map(version)
    assert key not in tags_map
