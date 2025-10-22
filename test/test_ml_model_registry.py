# test_ml_model_registry.py
import hero

TESTABLE_EXPERIMENT_ID = "2"
TESTABLE_EXPERIMENT_NAME = "Wrapped Model Tests"
TESTABLE_RUN_ID = "60c96b78b73649bd91d697ac8a44a1cd"
TESTABLE_MODEL_ID = "Test Experiment 1"
TESTABLE_MODEL_VERSION_ID = "1"


def get_tag_map(tags):
    tags = tags or []
    tags_map = {}
    for tag in tags:
        key = tag.get("key")
        if key is not None:
            tags_map[key] = tag.get("value")
    return tags_map


def test_list_experiments():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    res = model_registry.list_experiments()
    experiments = res.get("experiments")

    assert experiments is not None
    assert isinstance(experiments, list)


def test_read_experiment():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    res = model_registry.read_experiment(
        id=TESTABLE_EXPERIMENT_ID,
    )
    experiment = res.get("experiment")

    assert experiment is not None
    assert experiment.get("experiment_id") == TESTABLE_EXPERIMENT_ID


def test_read_experiment_by_name():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    res = model_registry.read_experiment_by_name(
        name=TESTABLE_EXPERIMENT_NAME,
    )
    experiment = res.get("experiment")

    assert experiment is not None
    assert experiment.get("name") == TESTABLE_EXPERIMENT_NAME


def test_update_experiment():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    # get original experiment
    res = model_registry.read_experiment(
        id=TESTABLE_EXPERIMENT_ID,
    )
    experiment = res.get("experiment")

    original_name = experiment.get("name")
    original_description = model_registry.get_description_from_tags(
        experiment.get("tags")
    )

    updated_name = "Updated Experiment"
    updated_description = "Updated Description"

    # update experiment w/ new vals
    res = model_registry.update_experiment(
        id=TESTABLE_EXPERIMENT_ID,
        name=updated_name,
        description=updated_description,
    )
    experiment = res.get("experiment")

    assert experiment is not None
    assert experiment.get("name") == updated_name
    assert (
        model_registry.get_description_from_tags(experiment.get("tags"))
        == updated_description
    )

    # reset experiment to original vals
    res = model_registry.update_experiment(
        id=TESTABLE_EXPERIMENT_ID,
        name=original_name,
        description=original_description,
    )
    experiment = res.get("experiment")

    assert experiment is not None
    assert experiment.get("name") == original_name
    assert (
        model_registry.get_description_from_tags(experiment.get("tags"))
        == original_description
    )


def test_update_experiment_tag():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    key = "test-key"
    value = "test-value"

    model_registry.update_experiment_tag(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        key=key,
        value=value,
    )

    res = model_registry.read_experiment(
        id=TESTABLE_EXPERIMENT_ID,
    )
    experiment = res.get("experiment")
    tags_map = get_tag_map(experiment.get("tags"))

    assert tags_map.get(key) == value

    model_registry.delete_experiment_tag(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        key=key,
    )

    res = model_registry.read_experiment(
        id=TESTABLE_EXPERIMENT_ID,
    )
    experiment = res.get("experiment")
    tags_map = get_tag_map(experiment.get("tags"))

    assert key not in tags_map


def test_list_runs():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    res = model_registry.list_runs(
        experiment_id=TESTABLE_EXPERIMENT_ID,
    )
    runs = res.get("runs")

    assert runs is not None
    assert isinstance(runs, list)


def test_read_run():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    res = model_registry.read_run(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        id=TESTABLE_RUN_ID,
    )
    run = res.get("run")

    assert run is not None
    assert run.get("info", {}).get("run_id") == TESTABLE_RUN_ID


def test_update_run():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    # get original run
    res = model_registry.read_run(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        id=TESTABLE_RUN_ID,
    )
    run = res.get("run")

    original_name = run.get("info", {}).get("run_name")
    original_description = model_registry.get_description_from_tags(
        run.get("data", {}).get("tags")
    )

    updated_name = "Updated Run"
    updated_description = "Updated Description"

    # update run w/ new vals
    res = model_registry.update_run(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        id=TESTABLE_RUN_ID,
        name=updated_name,
        description=updated_description,
    )
    run = res.get("run")

    assert run is not None
    assert run.get("info", {}).get("run_name") == updated_name
    assert (
        model_registry.get_description_from_tags(run.get("data", {}).get("tags"))
        == updated_description
    )

    # reset run to original vals
    res = model_registry.update_run(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        id=TESTABLE_RUN_ID,
        name=original_name,
        description=original_description,
    )
    run = res.get("run")

    assert run is not None
    assert run.get("info", {}).get("run_name") == original_name
    assert (
        model_registry.get_description_from_tags(run.get("data", {}).get("tags"))
        == original_description
    )


def test_update_run_tag():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    key = "test-key"
    value = "test-value"

    model_registry.update_run_tag(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        run_id=TESTABLE_RUN_ID,
        key=key,
        value=value,
    )

    res = model_registry.read_run(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        id=TESTABLE_RUN_ID,
    )
    run = res.get("run")
    tags_map = get_tag_map(run.get("data", {}).get("tags"))

    assert tags_map.get(key) == value

    model_registry.delete_run_tag(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        run_id=TESTABLE_RUN_ID,
        key=key,
    )

    res = model_registry.read_run(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        id=TESTABLE_RUN_ID,
    )
    run = res.get("run")
    tags_map = get_tag_map(run.get("data", {}).get("tags"))

    assert key not in tags_map


def test_list_artifacts():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    artifacts = model_registry.list_artifacts(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        run_id=TESTABLE_RUN_ID,
    )

    assert artifacts is not None
    assert isinstance(artifacts, list)


def test_list_registered_models():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    res = model_registry.list_registered_models()
    models = res.get("registered_models")

    assert models is not None
    assert isinstance(models, list)


def test_read_registered_model():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    res = model_registry.read_registered_model(
        id=TESTABLE_MODEL_ID,
    )
    model = res.get("registered_model")

    assert model is not None
    assert model.get("name") == TESTABLE_MODEL_ID


def test_update_registered_model():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    # get original model
    res = model_registry.read_registered_model(
        id=TESTABLE_MODEL_ID,
    )
    model = res.get("registered_model")

    original_description = model.get("description")
    updated_description = "Updated Description"

    # update model
    res = model_registry.update_registered_model(
        id=TESTABLE_MODEL_ID,
        description=updated_description,
    )
    model = res.get("registered_model")

    assert model is not None
    assert model.get("description") == updated_description

    # reset model
    res = model_registry.update_registered_model(
        id=TESTABLE_MODEL_ID,
        description=original_description,
    )
    model = res.get("registered_model")

    assert model is not None
    assert model.get("description") == original_description


def test_update_registered_model_tag():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    key = "test-key"
    value = "test-value"

    model_registry.update_registered_model_tag(
        model_id=TESTABLE_MODEL_ID,
        key=key,
        value=value,
    )

    res = model_registry.read_registered_model(
        id=TESTABLE_MODEL_ID,
    )
    model = res.get("registered_model")
    tags_map = get_tag_map(model.get("tags"))

    assert tags_map.get(key) == value

    model_registry.delete_registered_model_tag(
        model_id=TESTABLE_MODEL_ID,
        key=key,
    )

    res = model_registry.read_registered_model(
        id=TESTABLE_MODEL_ID,
    )
    model = res.get("registered_model")
    tags_map = get_tag_map(model.get("tags"))

    assert key not in tags_map


def test_update_registered_model_version_tag():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    key = "test-key"
    value = "test-value"

    model_registry.update_registered_model_version_tag(
        model_id=TESTABLE_MODEL_ID,
        id=TESTABLE_MODEL_VERSION_ID,
        key=key,
        value=value,
    )

    res = model_registry.read_registered_model_version(
        model_id=TESTABLE_MODEL_ID,
        id=TESTABLE_MODEL_VERSION_ID,
    )
    version = res.get("model_version")
    tags_map = get_tag_map(version.get("tags"))

    assert tags_map.get(key) == value

    model_registry.delete_registered_model_version_tag(
        model_id=TESTABLE_MODEL_ID,
        id=TESTABLE_MODEL_VERSION_ID,
        key=key,
    )

    res = model_registry.read_registered_model_version(
        model_id=TESTABLE_MODEL_ID,
        id=TESTABLE_MODEL_VERSION_ID,
    )
    version = res.get("model_version")
    tags_map = get_tag_map(version.get("tags"))

    assert key not in tags_map
