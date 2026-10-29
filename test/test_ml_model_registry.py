# test_ml_model_registry.py
#
# Runs against a deployed ML Model Registry API. Reads use the [SEED] data in the
# dev test project (seeded by hero-ml-model-registry-api/scripts/seed); writes use
# throwaway entities that are deleted when the module finishes, so a failed test
# can't leave the shared seed data changed.
#
# Env: HERO_ENV=dev, HERO_PROJECT=hero-test-framework, and HERO_CLIENT_ID /
# HERO_CLIENT_SECRET for a client with the ml-model-registry/user scope.
import os
import uuid

import pytest
import hero
from hero.lib.errors import (
    MissingRequiredAttribute,
    HEROMLModelRegistryResourceAlreadyExists,
    HEROMLModelRegistryResourceNotFound,
)

SEED_EXPERIMENT_NAME = "[SEED] Iris Classification"
SEED_REGRESSION_EXPERIMENT_NAME = "[SEED] Diabetes Regression"
SEED_RUN_NAME = "[SEED] pyfunc"
SEED_MODEL_ID = "seed_diabetes_regressor"

# These need the hero-ml-model-registry-api fixes for HMR-248 (error codes) and
# HMR-253 (version delete) deployed; set MMR_API_FIXES_DEPLOYED=1 once they are
needs_api_fixes = pytest.mark.xfail(
    not os.environ.get("MMR_API_FIXES_DEPLOYED"),
    reason="HMR-248/HMR-253: needs the API fix deployed",
    strict=False,
)


def get_tag_map(tags):
    tags_map = {}
    for tag in tags or []:
        key = tag.get("key")
        if key is not None:
            tags_map[key] = tag.get("value")
    return tags_map


def make_temp_name(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def experiment_by_name(model_registry, name):
    for experiment in model_registry.list_experiments():
        if experiment.name == name:
            return experiment
    pytest.fail(f"experiment {name!r} is missing from list_experiments")


@pytest.fixture(scope="module")
def model_registry():
    return hero.HeroClient().MLModelRegistry()


@pytest.fixture(scope="module")
def seed_experiment(model_registry):
    return experiment_by_name(model_registry, SEED_EXPERIMENT_NAME)


@pytest.fixture(scope="module")
def seed_run(model_registry, seed_experiment):
    for run in model_registry.list_runs(experiment_id=seed_experiment.experiment_id):
        if run.info.run_name == SEED_RUN_NAME:
            return run
    pytest.fail(f"run {SEED_RUN_NAME!r} is missing")


@pytest.fixture(scope="module")
def temp_experiment(model_registry):
    created = model_registry.create_experiment(
        name=make_temp_name("hero-python-sdk test")
    )
    # create returns only the experiment_id
    experiment = model_registry.read_experiment(id=created.experiment_id)
    yield experiment
    model_registry.delete_experiment(id=experiment.experiment_id)


@pytest.fixture(scope="module")
def temp_model(model_registry):
    model = model_registry.create_registered_model(
        id=make_temp_name("hero_python_sdk_test")
    )
    yield model
    # deleting the model also removes its versions
    model_registry.delete_registered_model(id=model.name)


# ----------------------------
# Experiments
# ----------------------------


def test_list_experiments(model_registry):
    names = [e.name for e in model_registry.list_experiments()]
    assert SEED_EXPERIMENT_NAME in names
    assert SEED_REGRESSION_EXPERIMENT_NAME in names


def test_read_experiment(model_registry, seed_experiment):
    experiment = model_registry.read_experiment(id=seed_experiment.experiment_id)
    assert experiment.name == SEED_EXPERIMENT_NAME
    assert experiment.lifecycle_stage == "active"


def test_read_experiment_by_name_with_brackets(model_registry, seed_experiment):
    experiment = model_registry.read_experiment_by_name(name=SEED_EXPERIMENT_NAME)
    assert experiment.experiment_id == seed_experiment.experiment_id


def test_read_experiment_by_name_missing_raises(model_registry):
    with pytest.raises(HEROMLModelRegistryResourceNotFound):
        model_registry.read_experiment_by_name(name=make_temp_name("hmr244 missing"))


def test_read_or_create_experiment_returns_existing(model_registry, temp_experiment):
    experiment = model_registry.read_or_create_experiment(name=temp_experiment.name)
    assert experiment.experiment_id == temp_experiment.experiment_id


def test_read_or_create_experiment_creates(model_registry):
    name = make_temp_name("hero-python-sdk read-or-create")
    experiment = model_registry.read_or_create_experiment(name=name)
    try:
        assert experiment.name == name
        again = model_registry.read_experiment_by_name(name=name)
        assert again.experiment_id == experiment.experiment_id
    finally:
        model_registry.delete_experiment(id=experiment.experiment_id)


def test_read_or_create_experiment_missing_name_raises(model_registry):
    with pytest.raises(MissingRequiredAttribute):
        model_registry.read_or_create_experiment(name=None)


@needs_api_fixes
def test_create_duplicate_experiment_raises(model_registry, temp_experiment):
    with pytest.raises(HEROMLModelRegistryResourceAlreadyExists):
        model_registry.create_experiment(name=temp_experiment.name)


def test_update_experiment(model_registry, temp_experiment):
    new_name = f"{temp_experiment.name} updated"
    model_registry.update_experiment(
        id=temp_experiment.experiment_id,
        name=new_name,
        description="Updated Description",
    )
    experiment = model_registry.read_experiment(id=temp_experiment.experiment_id)
    assert experiment.name == new_name
    assert (
        model_registry.get_description_from_tags(experiment.tags)
        == "Updated Description"
    )


def test_update_and_delete_experiment_tag(model_registry, temp_experiment):
    experiment_id = temp_experiment.experiment_id
    model_registry.update_experiment_tag(
        experiment_id=experiment_id, key="test-key", value="test-value"
    )
    experiment = model_registry.read_experiment(id=experiment_id)
    assert get_tag_map(experiment.tags)["test-key"] == "test-value"

    model_registry.delete_experiment_tag(experiment_id=experiment_id, key="test-key")
    experiment = model_registry.read_experiment(id=experiment_id)
    assert "test-key" not in get_tag_map(experiment.tags)


# ----------------------------
# Runs
# ----------------------------


def test_list_runs_includes_failed_and_nested(model_registry, seed_experiment):
    runs = model_registry.list_runs(
        experiment_id=seed_experiment.experiment_id, run_view_type="ALL"
    )
    by_name = {r.info.run_name: r for r in runs}
    assert len(runs) == 5
    assert by_name["[SEED] failed"].info.status == "FAILED"
    parent_id = by_name["[SEED] sweep-parent"].info.run_id
    child = by_name["[SEED] sweep-child-C0.1"]
    assert get_tag_map(child.data.tags)["mlflow.parentRunId"] == parent_id


def test_list_runs_with_filter(model_registry, seed_experiment):
    runs = model_registry.list_runs(
        experiment_id=seed_experiment.experiment_id,
        filter="attributes.status = 'FAILED'",
    )
    assert [r.info.run_name for r in runs] == ["[SEED] failed"]


def test_list_runs_missing_experiment_id_raises(model_registry):
    with pytest.raises(MissingRequiredAttribute):
        model_registry.list_runs(experiment_id=None)


def test_read_run(model_registry, seed_run):
    run = model_registry.read_run(id=seed_run.info.run_id)
    assert run.info.run_id == seed_run.info.run_id
    assert run.data.params
    assert run.outputs.model_outputs, "pyfunc run should have a logged model output"


def test_read_metric_history(model_registry):
    experiment = experiment_by_name(model_registry, SEED_REGRESSION_EXPERIMENT_NAME)
    run = model_registry.list_runs(experiment_id=experiment.experiment_id)[0]
    metric = run.data.metrics[0].key
    history = model_registry.read_metric_history(run_id=run.info.run_id, metric=metric)
    assert len(history) >= 1


def test_read_bulk_metric_history(model_registry):
    experiment = experiment_by_name(model_registry, SEED_REGRESSION_EXPERIMENT_NAME)
    runs = model_registry.list_runs(experiment_id=experiment.experiment_id)
    metric = runs[0].data.metrics[0].key
    history = model_registry.read_bulk_metric_history(
        experiment_id=experiment.experiment_id,
        run_ids=[r.info.run_id for r in runs],
        metric=metric,
    )
    assert len(history) >= len(runs)


def test_read_metric_history_validation(model_registry):
    with pytest.raises(MissingRequiredAttribute):
        model_registry.read_metric_history(run_id=None, metric="m")
    with pytest.raises(MissingRequiredAttribute):
        model_registry.read_metric_history(run_id="r", metric=None)


def test_read_bulk_metric_history_validation(model_registry):
    with pytest.raises(MissingRequiredAttribute):
        model_registry.read_bulk_metric_history(
            experiment_id=None, run_ids=["r"], metric="m"
        )
    with pytest.raises(MissingRequiredAttribute):
        model_registry.read_bulk_metric_history(
            experiment_id="e", run_ids=None, metric="m"
        )
    with pytest.raises(MissingRequiredAttribute):
        model_registry.read_bulk_metric_history(
            experiment_id="e", run_ids=["r"], metric=None
        )


def test_list_artifacts(model_registry, seed_run):
    paths = [a.path for a in model_registry.list_artifacts(run_id=seed_run.info.run_id)]
    assert "predictions.csv" in paths


# ----------------------------
# Logged models
# ----------------------------


def test_list_and_read_logged_models(model_registry, seed_experiment):
    logged = model_registry.list_logged_models(
        experiment_id=seed_experiment.experiment_id
    )
    assert logged, "the Iris experiment has a logged model"

    model_id = logged[0].info.model_id
    model = model_registry.read_logged_model(id=model_id)
    assert model.info.model_id == model_id
    files = model_registry.list_logged_model_artifacts(model_id=model_id)
    assert any(f.path == "MLmodel" for f in files)


# ----------------------------
# Registered models
# ----------------------------


def test_list_registered_models_hides_prompts(model_registry):
    names = [m.name for m in model_registry.list_registered_models()]
    assert SEED_MODEL_ID in names
    assert "seed_iris_classifier" in names
    assert "seed_summarizer_prompt" not in names


def test_list_registered_models_with_filter(model_registry):
    models = model_registry.list_registered_models(filter="name LIKE 'seed_iris%'")
    assert [m.name for m in models] == ["seed_iris_classifier"]


def test_read_registered_model_with_aliases(model_registry):
    model = model_registry.read_registered_model(id=SEED_MODEL_ID)
    aliases = {a.alias: a.version for a in model.aliases}
    assert aliases == {"champion": "2", "challenger": "3"}


def test_read_registered_model_missing_raises(model_registry):
    with pytest.raises(HEROMLModelRegistryResourceNotFound):
        model_registry.read_registered_model(id=make_temp_name("hmr244_missing"))


def test_create_duplicate_registered_model_raises(model_registry, temp_model):
    with pytest.raises(HEROMLModelRegistryResourceAlreadyExists):
        model_registry.create_registered_model(id=temp_model.name)


def test_read_or_create_registered_model_returns_existing(model_registry, temp_model):
    model = model_registry.read_or_create_registered_model(id=temp_model.name)
    assert model.name == temp_model.name


def test_list_registered_model_versions_is_scoped_to_the_model(model_registry):
    versions = model_registry.list_registered_model_versions(model_id=SEED_MODEL_ID)
    assert sorted(v.version for v in versions) == ["1", "2", "3"]
    assert {v.name for v in versions} == {SEED_MODEL_ID}


def test_list_registered_model_versions_sorted(model_registry):
    versions = model_registry.list_registered_model_versions(
        model_id=SEED_MODEL_ID, search_key="version_number", sort_order="DESC"
    )
    assert [v.version for v in versions] == ["3", "2", "1"]


def test_update_registered_model(model_registry, temp_model):
    model = model_registry.update_registered_model(
        id=temp_model.name, description="Updated Description"
    )
    assert model.description == "Updated Description"


def test_update_and_delete_registered_model_tag(model_registry, temp_model):
    model_registry.update_registered_model_tag(
        model_id=temp_model.name, key="test-key", value="test-value"
    )
    model = model_registry.read_registered_model(id=temp_model.name)
    assert get_tag_map(model.tags)["test-key"] == "test-value"

    model_registry.delete_registered_model_tag(model_id=temp_model.name, key="test-key")
    model = model_registry.read_registered_model(id=temp_model.name)
    assert "test-key" not in get_tag_map(model.tags)


def test_rename_registered_model(model_registry):
    old_name = make_temp_name("hero_python_sdk_rename")
    new_name = f"{old_name}_renamed"
    model_registry.create_registered_model(id=old_name)
    try:
        model = model_registry.rename_registered_model(id=old_name, new_name=new_name)
        assert model.name == new_name
        with pytest.raises(HEROMLModelRegistryResourceNotFound):
            model_registry.read_registered_model(id=old_name)
    finally:
        for name in (new_name, old_name):
            try:
                model_registry.delete_registered_model(id=name)
            except HEROMLModelRegistryResourceNotFound:
                pass


@needs_api_fixes
def test_registered_model_version_lifecycle(model_registry, temp_model, seed_run):
    run_id = seed_run.info.run_id
    created = model_registry.create_registered_model_version(
        model_id=temp_model.name, run_id=run_id, source=f"runs:/{run_id}/model"
    )
    version = created.version

    model_registry.update_registered_model_version(
        model_id=temp_model.name, id=version, description="HMR-244 test"
    )
    model_registry.update_registered_model_version_tag(
        model_id=temp_model.name, id=version, key="test-key", value="test-value"
    )
    read = model_registry.read_registered_model_version(
        model_id=temp_model.name, id=version
    )
    assert read.description == "HMR-244 test"
    assert get_tag_map(read.tags)["test-key"] == "test-value"

    model_registry.delete_registered_model_version_tag(
        model_id=temp_model.name, id=version, key="test-key"
    )
    read = model_registry.read_registered_model_version(
        model_id=temp_model.name, id=version
    )
    assert "test-key" not in get_tag_map(read.tags)

    # HMR-253: the API dropped the version number, so this failed until fixed
    model_registry.delete_registered_model_version(model_id=temp_model.name, id=version)
    remaining = model_registry.list_registered_model_versions(model_id=temp_model.name)
    assert [v.version for v in remaining] == []


@needs_api_fixes
def test_read_registered_model_version_missing_raises(model_registry, temp_model):
    # HMR-248: a missing version came back as a generic 400 until fixed
    with pytest.raises(HEROMLModelRegistryResourceNotFound):
        model_registry.read_registered_model_version(model_id=temp_model.name, id="999")


# ----------------------------
# Tracking URI & patched MLflow
# ----------------------------


def test_get_tracking_uri(model_registry):
    uri = model_registry.get_tracking_uri()
    assert uri.endswith(f"/proxy/{model_registry.registry_name}")


def test_patched_mlflow_optional_dependency(model_registry):
    # Either returns the patched module/client or explains how to install hero-mlflow
    try:
        assert model_registry.get_patched_mlflow() is not None
    except RuntimeError as e:
        assert "hero-mlflow is not installed" in str(e)

    try:
        assert model_registry.get_patched_mlflow_client() is not None
    except RuntimeError as e:
        assert "hero-mlflow is not installed" in str(e)
