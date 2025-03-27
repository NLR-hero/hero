import os
import functools
import mlflow
from mlflow.tracking import MlflowClient
from mlflow.store.artifact.artifact_repository_registry import get_artifact_repository
from mlflow.store.artifact.artifact_repo import ArtifactRepository

# ------------------------------
# Config
# ------------------------------


def is_preflight_enabled():
    """
    Returns whether preflight checks are enabled.
    Note: this is currently ignored, but can be used to disable preflight checks
    if needed in the future.
    """
    return os.getenv("MLFLOW_PREFLIGHT_ENABLED", "true").lower() in ["1", "true", "yes"]


# ------------------------------
# Preflight Hook
# ------------------------------


def default_preflight_hook(method_name, *args, **kwargs):
    """
    Default preflight hook that prints the method name.
    """
    print(f"✨ Preflight before: {method_name}")


# ------------------------------
# Patched Artifact Repository
# ------------------------------


class PatchedArtifactRepository(ArtifactRepository):
    """
    A patched artifact repository that adds preflight hooks to all methods.
    """

    def __init__(self, base_repo, preflight_hook=None):
        """
        Creates a patched artifact repository.
        """
        self._repo = base_repo
        self._preflight = preflight_hook or default_preflight_hook

    def __getattribute__(self, name):
        """
        Overrides the default __getattribute__ method to add preflight hooks.
        """
        if name in {"_repo", "_preflight", "__class__", "__dict__"}:
            return object.__getattribute__(self, name)

        attr = getattr(self._repo, name)

        if not callable(attr):
            return attr

        @functools.wraps(attr)
        def wrapper(*args, **kwargs):
            self._preflight(name, *args, **kwargs)
            return attr(*args, **kwargs)

        return wrapper


def patch_artifact_repository(preflight_hook=None):
    """
    Patches the artifact repository to add preflight hooks to all methods.
    """
    original_get_repo = get_artifact_repository

    def wrapped_get_repo(artifact_uri, *args, **kwargs):
        repo = original_get_repo(artifact_uri, *args, **kwargs)
        return PatchedArtifactRepository(repo, preflight_hook)

    import mlflow.store.artifact.artifact_repository_registry as registry

    registry.get_artifact_repository = wrapped_get_repo


class PatchedMlflowClient:
    """
    A patched MlflowClient that adds preflight hooks to methods.
    """

    def __init__(self, *args, preflight_hook=None, **kwargs):
        """
        Creates a patched MlflowClient.
        """
        self._client = MlflowClient(*args, **kwargs)
        self._preflight = preflight_hook or default_preflight_hook
        patch_artifact_repository(preflight_hook=self._preflight)

    def __getattribute__(self, name):
        """
        Overrides the default __getattribute__ method to add preflight hooks.
        """
        if name in {"_client", "_preflight", "__class__", "__dict__"}:
            return object.__getattribute__(self, name)

        attr = getattr(self._client, name)

        if not callable(attr):
            return attr

        @functools.wraps(attr)
        def wrapper(*args, **kwargs):
            self._preflight(name, *args, **kwargs)
            return attr(*args, **kwargs)

        return wrapper


def patch_mlflow_module(preflight_hook=None):
    """
    Patches the mlflow module to add preflight hooks to all methods listed in
    `functions_to_patch`.
    """
    preflight = preflight_hook or default_preflight_hook

    functions_to_patch = [
        "log_param",
        "log_params",
        "log_metric",
        "log_metrics",
        "set_tag",
        "set_tags",
        "log_artifact",
        "log_artifacts",
        "start_run",
        "end_run",
        "set_experiment",
        "create_experiment",
        "delete_experiment",
        "get_experiment_by_name",
    ]

    for func_name in functions_to_patch:
        if hasattr(mlflow, func_name):
            original = getattr(mlflow, func_name)

            @functools.wraps(original)
            def wrapper(*args, __original=original, __name=func_name, **kwargs):
                preflight(__name, *args, **kwargs)
                return __original(*args, **kwargs)

            setattr(mlflow, func_name, wrapper)


# ------------------------------
# Entry Point to Enable All
# ------------------------------


def enable_preflight_patching(preflight_hook=None):
    """
    Enables preflight hooks for all mlflow operations.
    Returns a patched MlflowClient instance.
    """
    patch_mlflow_module(preflight_hook=preflight_hook)
    return PatchedMlflowClient(preflight_hook=preflight_hook)


def get_patched_mlflow():
    """
    Returns a patched mlflow module with preflight hooks.
    """
    return mlflow
