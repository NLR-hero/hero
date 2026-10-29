# test_ml_model_registry_mlflow.py
#
# Real MLflow workflows through the HERO proxy, as in hero-examples/ml-model-registry
# (ex_01 training + logging, ex_02 evaluating + registering): the patched mlflow
# module from get_patched_mlflow() logs runs, params, metrics, datasets, artifacts
# and a wrapped pyfunc model, then loads and registers it.
#
# Everything is written to a throwaway experiment and registered model that are
# deleted when the module finishes. MLflow soft-deletes runs, so the S3 artifacts
# stay until the server's gc removes them.
#
# Needs: hero-mlflow, mlflow (match the server, 3.16.x), scikit-learn, numpy.
# Skipped when they aren't installed. Same env as test_ml_model_registry.py.
import os
import time
import uuid

import pytest

mlflow_mod = pytest.importorskip("mlflow")
pytest.importorskip("hero_mlflow")
pytest.importorskip("sklearn")
np = pytest.importorskip("numpy")

from mlflow.exceptions import MlflowException, RestException
from mlflow.pyfunc import PythonModel
from sklearn.datasets import load_diabetes
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

import hero
from hero.lib.errors import HEROMLModelRegistryResourceNotFound

SEED = 86

# MLflow branches on the proxy's error_code; needs the hero-ml-model-registry-api
# fix for HMR-248 deployed. Set MMR_API_FIXES_DEPLOYED=1 once it is.
needs_hmr248 = pytest.mark.xfail(
    not os.environ.get("MMR_API_FIXES_DEPLOYED"),
    reason="HMR-248: proxy drops MLflow error_code until the API fix is deployed",
    strict=False,
)
PREPROCESS_SOURCE = "def preprocess(model_input):\n    return model_input\n"


class ModelWrapper(PythonModel):
    """The ex_01 pattern: a pyfunc wrapper that preprocesses before predicting."""

    def __init__(self, model):
        self.model = model

    def predict(self, context, model_input, params=None):
        from preprocess import preprocess

        return self.model.predict(preprocess(model_input))


def evaluate(y, pred):
    return {
        "rmse": float(np.sqrt(mean_squared_error(y, pred))),
        "mae": float(mean_absolute_error(y, pred)),
        "r2": float(r2_score(y, pred)),
    }


@pytest.fixture(scope="module")
def model_registry():
    return hero.HeroClient().MLModelRegistry()


@pytest.fixture(scope="module")
def mlflow(model_registry):
    mf = model_registry.get_patched_mlflow()
    mf.set_tracking_uri(model_registry.get_tracking_uri())
    return mf


@pytest.fixture(scope="module")
def experiment(model_registry):
    name = f"hero-python-sdk mlflow test {uuid.uuid4().hex[:8]}"
    exp = model_registry.read_or_create_experiment(name)
    yield exp
    model_registry.delete_experiment(id=exp.experiment_id)


@pytest.fixture(scope="module")
def registered_model_name(model_registry):
    name = f"hero_python_sdk_mlflow_test_{uuid.uuid4().hex[:8]}"
    yield name
    try:
        # deleting the model also removes its versions and aliases
        model_registry.delete_registered_model(id=name)
    except HEROMLModelRegistryResourceNotFound:
        pass


@pytest.fixture(scope="module")
def data():
    db = load_diabetes()
    return train_test_split(db.data, db.target, random_state=SEED)


@pytest.fixture(scope="module")
def trained_run(mlflow, experiment, data, tmp_path_factory):
    """Trains and logs a wrapped model the way ex_01 does; returns (run, metrics)."""
    X_train, X_test, y_train, y_test = data
    params = {"random_state": SEED, "n_estimators": 20, "max_depth": 4}
    tags = {"Project": "hero-python-sdk tests", "autologging": "false"}

    work = tmp_path_factory.mktemp("mlflow")
    (work / "states").mkdir()
    (work / "states" / "data.json").write_text('{"hello": "world"}')
    (work / "preprocess.py").write_text(PREPROCESS_SOURCE)

    with mlflow.start_run(experiment_id=experiment.experiment_id) as run:
        mlflow.set_tags(tags)
        mlflow.log_params(params)
        mlflow.log_artifacts(str(work / "states"), artifact_path="states")
        mlflow.log_input(mlflow.data.from_numpy(X_train), context="Train")
        mlflow.log_input(mlflow.data.from_numpy(X_test), context="Eval")

        rf = RandomForestRegressor(**params).fit(X_train, y_train)
        predictions = rf.predict(X_test)
        metrics = evaluate(y_test, predictions)
        mlflow.log_metrics(metrics)
        for step, value in enumerate([3.0, 2.0, 1.5]):
            mlflow.log_metric("loss", value, step=step)

        mlflow.pyfunc.log_model(
            name=f"hero-sdk-test-{int(time.time())}",
            python_model=ModelWrapper(rf),
            code_paths=[str(work / "preprocess.py")],
            signature=mlflow.models.infer_signature(X_test, predictions),
        )
    return run, metrics


# ----------------------------
# ex_01: training and logging
# ----------------------------


def test_run_is_visible_through_the_sdk(model_registry, experiment, trained_run):
    run, metrics = trained_run
    read = model_registry.read_run(id=run.info.run_id)
    assert read.info.status == "FINISHED"
    assert read.info.experiment_id == experiment.experiment_id

    params = {p.key: p.value for p in read.data.params}
    assert params["n_estimators"] == "20"
    logged = {m.key: m.value for m in read.data.metrics}
    assert logged["r2"] == pytest.approx(metrics["r2"])
    tags = {t.key: t.value for t in read.data.tags}
    assert tags["Project"] == "hero-python-sdk tests"

    runs = model_registry.list_runs(experiment_id=experiment.experiment_id)
    assert run.info.run_id in [r.info.run_id for r in runs]


def test_metric_history_has_every_step(model_registry, trained_run):
    run, _ = trained_run
    history = model_registry.read_metric_history(run_id=run.info.run_id, metric="loss")
    assert [h.value for h in sorted(history, key=lambda h: h.step)] == [3.0, 2.0, 1.5]


def test_artifacts_were_uploaded(model_registry, mlflow, trained_run):
    run, _ = trained_run
    paths = [a.path for a in model_registry.list_artifacts(run_id=run.info.run_id)]
    assert "states/data.json" in paths or "states" in paths

    local = mlflow.artifacts.download_artifacts(
        run_id=run.info.run_id, artifact_path="states/data.json"
    )
    with open(local) as f:
        assert f.read() == '{"hello": "world"}'


def test_logged_model_is_linked_to_the_run(model_registry, experiment, trained_run):
    run, _ = trained_run
    read = model_registry.read_run(id=run.info.run_id)
    model_id = read.outputs.model_outputs[0].model_id

    logged = model_registry.list_logged_models(experiment_id=experiment.experiment_id)
    assert model_id in [m.info.model_id for m in logged]
    files = [
        f.path for f in model_registry.list_logged_model_artifacts(model_id=model_id)
    ]
    assert "MLmodel" in files


def test_logged_model_loads_and_predicts(model_registry, mlflow, trained_run, data):
    run, metrics = trained_run
    _, X_test, _, y_test = data
    model_id = (
        model_registry.read_run(id=run.info.run_id).outputs.model_outputs[0].model_id
    )

    model = mlflow.pyfunc.load_model(f"models:/{model_id}")
    predictions = model.predict(X_test)
    assert evaluate(y_test, predictions)["r2"] == pytest.approx(metrics["r2"])


# ----------------------------
# ex_02: evaluating and registering
# ----------------------------


def test_best_run_by_metric(model_registry, experiment, trained_run):
    run, _ = trained_run
    ranked = model_registry.list_runs(
        experiment_id=experiment.experiment_id,
        search_key="metrics.r2",
        sort_order="DESC",
    )
    assert ranked[0].info.run_id == run.info.run_id


def logged_model_id(model_registry, run):
    return model_registry.read_run(id=run.info.run_id).outputs.model_outputs[0].model_id


def test_register_through_the_sdk(model_registry, registered_model_name, trained_run):
    run, _ = trained_run
    model_registry.read_or_create_registered_model(id=registered_model_name)
    # ex_02 points the version at the run's artifact_uri; a logged model's URI is
    # what MLflow can load back, so use that
    version = model_registry.create_registered_model_version(
        model_id=registered_model_name,
        run_id=run.info.run_id,
        source=f"models:/{logged_model_id(model_registry, run)}",
    )
    assert version.version == "1"

    versions = model_registry.list_registered_model_versions(
        model_id=registered_model_name
    )
    assert [v.version for v in versions] == ["1"]


def test_alias_and_load_by_alias(
    model_registry, mlflow, registered_model_name, trained_run, data
):
    _, metrics = trained_run
    _, X_test, _, y_test = data

    client = model_registry.get_patched_mlflow_client()
    client.set_registered_model_alias(registered_model_name, "champion", "1")
    model = model_registry.read_registered_model(id=registered_model_name)
    assert {a.alias: a.version for a in model.aliases} == {"champion": "1"}

    loaded = mlflow.pyfunc.load_model(f"models:/{registered_model_name}@champion")
    assert evaluate(y_test, loaded.predict(X_test))["r2"] == pytest.approx(
        metrics["r2"]
    )


@needs_hmr248
def test_register_model_on_an_existing_model(
    model_registry, mlflow, registered_model_name, trained_run
):
    run, _ = trained_run
    # register_model() creates the model first and expects RESOURCE_ALREADY_EXISTS
    # when it's already there, then adds a version (HMR-248)
    mv = mlflow.register_model(
        f"models:/{logged_model_id(model_registry, run)}", registered_model_name
    )
    assert mv.version == "2"
    versions = model_registry.list_registered_model_versions(
        model_id=registered_model_name
    )
    assert sorted(v.version for v in versions) == ["1", "2"]


@needs_hmr248
def test_duplicate_create_raises_mlflow_resource_already_exists(
    mlflow, registered_model_name
):
    client = mlflow.MlflowClient()
    with pytest.raises(MlflowException) as info:
        client.create_registered_model(registered_model_name)
    assert info.value.error_code == "RESOURCE_ALREADY_EXISTS"


@pytest.mark.xfail(
    reason="HMR-250: CloudFront replaces API 404 bodies with the SPA index.html",
    strict=False,
)
def test_missing_model_raises_mlflow_resource_does_not_exist(mlflow):
    client = mlflow.MlflowClient()
    with pytest.raises(RestException) as info:
        client.get_registered_model(f"hero_python_sdk_missing_{uuid.uuid4().hex[:8]}")
    assert info.value.error_code == "RESOURCE_DOES_NOT_EXIST"
