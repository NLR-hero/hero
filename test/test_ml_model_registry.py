# test_ml_model_registry.py
import uuid
import pytest
import hero
from hero.lib.errors import (
    MissingRequiredAttribute,
    HEROMLModelRegistryResourceNotFound,
    HEROMLModelRegistryResourceNotFound,
)


TESTABLE_EXPERIMENT_ID = "2"
TESTABLE_EXPERIMENT_NAME = "Wrapped Model Tests"
TESTABLE_RUN_ID = "60c96b78b73649bd91d697ac8a44a1cd"
TESTABLE_MODEL_ID = "Test Experiment 1"
TESTABLE_MODEL_VERSION_ID = "1"


def get_tag_map(tags):
    tags = tags or []
    tags_map = {}
    for tag in tags:
        # HeroObject should behave like a Mapping
        key = tag.get("key")
        if key is not None:
            tags_map[key] = tag.get("value")
    return tags_map


def make_temp_name(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


# ----------------------------
# Experiments
# ----------------------------


def test_list_experiments():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    experiments = model_registry.list_experiments()
    assert experiments is not None
    assert isinstance(experiments, list)
    # smoke check on first item shape (if present)
    if experiments:
        exp0 = experiments[0]
        # HeroObject supports dot access
        assert hasattr(exp0, "id") or hasattr(exp0, "experiment_id")


def test_read_experiment():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    experiment = model_registry.read_experiment(id=TESTABLE_EXPERIMENT_ID)
    assert experiment is not None
    # MLflow uses experiment_id; some APIs also include id
    assert (getattr(experiment, "experiment_id", None) == TESTABLE_EXPERIMENT_ID) or (
        getattr(experiment, "id", None) == TESTABLE_EXPERIMENT_ID
    )


def test_read_experiment_by_name():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    experiment = model_registry.read_experiment_by_name(name=TESTABLE_EXPERIMENT_NAME)
    assert experiment is not None
    assert experiment.name == TESTABLE_EXPERIMENT_NAME


def test_update_experiment_and_reset():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    experiment = model_registry.read_experiment(id=TESTABLE_EXPERIMENT_ID)
    original_name = experiment.name
    original_description = model_registry.get_description_from_tags(experiment.tags)

    updated_name = "Updated Experiment"
    updated_description = "Updated Description"

    # update
    experiment = model_registry.update_experiment(
        id=TESTABLE_EXPERIMENT_ID,
        name=updated_name,
        description=updated_description,
    )
    assert experiment is not None
    assert experiment.name == updated_name
    assert (
        model_registry.get_description_from_tags(experiment.tags) == updated_description
    )

    # reset
    experiment = model_registry.update_experiment(
        id=TESTABLE_EXPERIMENT_ID,
        name=original_name,
        description=original_description,
    )
    assert experiment is not None
    assert experiment.name == original_name
    assert (
        model_registry.get_description_from_tags(experiment.tags)
        == original_description
    )


def test_update_and_delete_experiment_tag():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    key = "test-key"
    value = "test-value"

    model_registry.update_experiment_tag(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        key=key,
        value=value,
    )

    experiment = model_registry.read_experiment(id=TESTABLE_EXPERIMENT_ID)
    tags_map = get_tag_map(experiment.tags)
    assert tags_map.get(key) == value

    model_registry.delete_experiment_tag(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        key=key,
    )

    experiment = model_registry.read_experiment(id=TESTABLE_EXPERIMENT_ID)
    tags_map = get_tag_map(experiment.tags)
    assert key not in tags_map


def test_create_read_or_create_and_delete_experiment():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    temp_name = make_temp_name("sdk-test-exp")

    # create
    created = model_registry.create_experiment(name=temp_name)
    assert created is not None
    created_id = getattr(created, "experiment_id", None) or getattr(created, "id", None)
    assert created_id is not None

    # read_or_create should read existing
    roc = model_registry.read_or_create_experiment(name=temp_name)
    assert roc is not None
    assert roc.name == temp_name

    # delete
    _ = model_registry.delete_experiment(id=created_id)

    # post-conditions: accept hard OR soft delete
    try:
        exp_after = model_registry.read_experiment(id=created_id)
    except HEROMLModelRegistryResourceNotFound:
        # hard delete
        return

    # soft delete – ensure lifecycle + listing behavior
    assert getattr(exp_after, "lifecycle_stage", "").lower() != "active"

    # and it should not be returned by the active list
    listed = model_registry.list_experiments()
    listed_ids = {
        getattr(e, "experiment_id", None) or getattr(e, "id", None)
        for e in (listed or [])
    }
    assert created_id not in listed_ids


def test_read_or_create_experiment_missing_name_raises():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    with pytest.raises(MissingRequiredAttribute):
        model_registry.read_or_create_experiment(name=None)


# ----------------------------
# Runs
# ----------------------------


def test_list_runs():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    runs = model_registry.list_runs(experiment_id=TESTABLE_EXPERIMENT_ID)
    assert runs is not None
    assert isinstance(runs, list)


def test_list_runs_missing_experiment_id_raises():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()
    with pytest.raises(MissingRequiredAttribute):
        model_registry.list_runs(experiment_id=None)


def test_read_run():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    run = model_registry.read_run(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        id=TESTABLE_RUN_ID,
    )
    assert run is not None
    assert run.info.run_id == TESTABLE_RUN_ID


def test_update_run_and_reset():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    run = model_registry.read_run(
        experiment_id=TESTABLE_EXPERIMENT_ID, id=TESTABLE_RUN_ID
    )
    original_name = run.info.run_name
    original_description = model_registry.get_description_from_tags(run.data.tags)

    updated_name = "Updated Run"
    updated_description = "Updated Description"

    run = model_registry.update_run(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        id=TESTABLE_RUN_ID,
        name=updated_name,
        description=updated_description,
    )
    assert run is not None
    assert run.info.run_name == updated_name
    assert (
        model_registry.get_description_from_tags(run.data.tags) == updated_description
    )

    # reset
    run = model_registry.update_run(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        id=TESTABLE_RUN_ID,
        name=original_name,
        description=original_description,
    )
    assert run is not None
    assert run.info.run_name == original_name
    assert (
        model_registry.get_description_from_tags(run.data.tags) == original_description
    )


def test_update_and_delete_run_tag():
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

    run = model_registry.read_run(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        id=TESTABLE_RUN_ID,
    )
    tags_map = get_tag_map(run.data.tags)
    assert tags_map.get(key) == value

    model_registry.delete_run_tag(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        run_id=TESTABLE_RUN_ID,
        key=key,
    )

    run = model_registry.read_run(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        id=TESTABLE_RUN_ID,
    )
    tags_map = get_tag_map(run.data.tags)
    assert key not in tags_map


def test_read_metric_history_validation():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    with pytest.raises(MissingRequiredAttribute):
        model_registry.read_metric_history(
            experiment_id=None, run_id=TESTABLE_RUN_ID, metric="m"
        )
    with pytest.raises(MissingRequiredAttribute):
        model_registry.read_metric_history(
            experiment_id=TESTABLE_EXPERIMENT_ID, run_id=None, metric="m"
        )
    with pytest.raises(MissingRequiredAttribute):
        model_registry.read_metric_history(
            experiment_id=TESTABLE_EXPERIMENT_ID, run_id=TESTABLE_RUN_ID, metric=None
        )


def test_read_bulk_metric_history_validation():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    with pytest.raises(MissingRequiredAttribute):
        model_registry.read_bulk_metric_history(
            experiment_id=None, run_ids=[TESTABLE_RUN_ID], metric="m"
        )
    with pytest.raises(MissingRequiredAttribute):
        model_registry.read_bulk_metric_history(
            experiment_id=TESTABLE_EXPERIMENT_ID, run_ids=[], metric="m"
        )
    with pytest.raises(MissingRequiredAttribute):
        model_registry.read_bulk_metric_history(
            experiment_id=TESTABLE_EXPERIMENT_ID, run_ids=[TESTABLE_RUN_ID], metric=None
        )


def test_list_artifacts():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    artifacts = model_registry.list_artifacts(
        experiment_id=TESTABLE_EXPERIMENT_ID,
        run_id=TESTABLE_RUN_ID,
    )

    # SDK returns HeroObject(data) for artifacts; backend commonly returns a list.
    # Assert it's list-like (many backends return a simple list).
    assert artifacts is not None
    assert isinstance(artifacts, list) or hasattr(artifacts, "__iter__")


# ----------------------------
# Logged Models (optional data)
# ----------------------------


def test_list_logged_models_and_optionally_read_one():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    logged = model_registry.list_logged_models(experiment_id=TESTABLE_EXPERIMENT_ID)
    assert logged is not None
    assert isinstance(logged, list)

    if not logged:
        pytest.skip(
            "No logged models found for the test experiment; skipping detail checks."
        )
    first = logged[0]
    lm = model_registry.read_logged_model(
        experiment_id=TESTABLE_EXPERIMENT_ID, id=first.id
    )
    assert lm is not None
    # Artifacts may or may not exist — if they do, list them
    arts = model_registry.list_logged_model_artifacts(
        experiment_id=TESTABLE_EXPERIMENT_ID, model_id=first.id
    )
    # list_logged_model_artifacts returns HeroObject(data); many backends return list
    assert arts is not None


# ----------------------------
# Registered Models
# ----------------------------


def test_list_registered_models():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    models = model_registry.list_registered_models()
    assert models is not None
    assert isinstance(models, list)


def test_read_registered_model():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    model = model_registry.read_registered_model(id=TESTABLE_MODEL_ID)
    assert model is not None
    assert model.name == TESTABLE_MODEL_ID


def test_update_registered_model_and_reset():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    model = model_registry.read_registered_model(id=TESTABLE_MODEL_ID)
    original_description = model.description
    updated_description = "Updated Description"

    model = model_registry.update_registered_model(
        id=TESTABLE_MODEL_ID,
        description=updated_description,
    )
    assert model is not None
    assert model.description == updated_description

    model = model_registry.update_registered_model(
        id=TESTABLE_MODEL_ID,
        description=original_description,
    )
    assert model is not None
    assert model.description == original_description


def test_update_and_delete_registered_model_tag():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    key = "test-key"
    value = "test-value"

    model_registry.update_registered_model_tag(
        model_id=TESTABLE_MODEL_ID,
        key=key,
        value=value,
    )

    model = model_registry.read_registered_model(id=TESTABLE_MODEL_ID)
    tags_map = get_tag_map(model.tags)
    assert tags_map.get(key) == value

    model_registry.delete_registered_model_tag(
        model_id=TESTABLE_MODEL_ID,
        key=key,
    )

    model = model_registry.read_registered_model(id=TESTABLE_MODEL_ID)
    tags_map = get_tag_map(model.tags)
    assert key not in tags_map


# def test_registered_model_crud_and_rename_cycle():
#     hero_client = hero.HeroClient()
#     model_registry = hero_client.MLModelRegistry()

#     temp_name = make_temp_name("sdk-test-model")

#     # create
#     created = model_registry.create_registered_model(id=temp_name)
#     assert created is not None
#     assert created.name == temp_name

#     # read_or_create should read existing
#     roc = model_registry.read_or_create_registered_model(id=temp_name)
#     assert roc is not None
#     assert roc.name == temp_name

#     # rename (changes the resource path)
#     new_name = f"{temp_name}-renamed"
#     _ = model_registry.rename_registered_model(id=temp_name, new_name=new_name)

#     # read using new name (should succeed)
#     model_after = model_registry.read_registered_model(id=new_name)
#     assert model_after is not None
#     assert model_after.name == new_name

#     # old name should now 404
#     with pytest.raises(HEROMLModelRegistryResourceNotFound):
#         model_registry.read_registered_model(id=temp_name)

#     # delete using new name
#     deleted = model_registry.delete_registered_model(id=new_name)
#     assert deleted is not None

#     # both old and new names should now 404
#     with pytest.raises(HEROMLModelRegistryResourceNotFound):
#         model_registry.read_registered_model(id=new_name)
#     with pytest.raises(HEROMLModelRegistryResourceNotFound):
#         model_registry.read_registered_model(id=temp_name)


def test_registered_model_version_read_update_and_tag_flow():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    version = model_registry.read_registered_model_version(
        model_id=TESTABLE_MODEL_ID, id=TESTABLE_MODEL_VERSION_ID
    )
    assert version is not None

    orig_desc = getattr(version, "description", None)
    upd_desc = "Updated Version Description"

    _ = model_registry.update_registered_model_version(
        model_id=TESTABLE_MODEL_ID,
        id=TESTABLE_MODEL_VERSION_ID,
        description=upd_desc,
    )
    version_after = model_registry.read_registered_model_version(
        model_id=TESTABLE_MODEL_ID, id=TESTABLE_MODEL_VERSION_ID
    )
    assert getattr(version_after, "description", None) == upd_desc

    _ = model_registry.update_registered_model_version(
        model_id=TESTABLE_MODEL_ID,
        id=TESTABLE_MODEL_VERSION_ID,
        description=orig_desc,
    )
    version_reset = model_registry.read_registered_model_version(
        model_id=TESTABLE_MODEL_ID, id=TESTABLE_MODEL_VERSION_ID
    )
    assert getattr(version_reset, "description", None) == orig_desc

    key = "test-key"
    value = "test-value"

    model_registry.update_registered_model_version_tag(
        model_id=TESTABLE_MODEL_ID, id=TESTABLE_MODEL_VERSION_ID, key=key, value=value
    )

    version = model_registry.read_registered_model_version(
        model_id=TESTABLE_MODEL_ID, id=TESTABLE_MODEL_VERSION_ID
    )
    tags_map = get_tag_map(version.tags)
    assert tags_map.get(key) == value

    model_registry.delete_registered_model_version_tag(
        model_id=TESTABLE_MODEL_ID, id=TESTABLE_MODEL_VERSION_ID, key=key
    )

    version = model_registry.read_registered_model_version(
        model_id=TESTABLE_MODEL_ID, id=TESTABLE_MODEL_VERSION_ID
    )
    tags_map = get_tag_map(version.tags)
    assert key not in tags_map


def test_list_registered_model_versions_shape():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    # SDK currently returns `.model_version` from this method
    versions = model_registry.list_registered_model_versions(model_id=TESTABLE_MODEL_ID)
    assert versions is not None
    # Some APIs return a list; the SDK exposes `.model_version`—assert it is list-like or object
    assert isinstance(versions, list) or hasattr(versions, "version")


# ----------------------------
# Tracking URI & Patched MLflow (optional)
# ----------------------------


def test_get_tracking_uri_basic_shape():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()
    uri = model_registry.get_tracking_uri()
    assert isinstance(uri, str)
    assert "/proxy/" in uri


def test_patched_mlflow_optional_dependency():
    hero_client = hero.HeroClient()
    model_registry = hero_client.MLModelRegistry()

    # This should either return a client or raise a RuntimeError if hero-mlflow isn't installed.
    try:
        mlf = model_registry.get_patched_mlflow()
        assert mlf is not None
    except RuntimeError as e:
        assert "hero-mlflow is not installed" in str(e)

    try:
        mlc = model_registry.get_patched_mlflow_client()
        assert mlc is not None
    except RuntimeError as e:
        assert "hero-mlflow is not installed" in str(e)
