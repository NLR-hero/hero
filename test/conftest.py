import os

# Integration tests read credentials from the environment; test/.env (gitignored)
# is loaded first when python-dotenv is installed.
try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

# Keep MLflow from creating a local mlflow.db before a test sets the HERO tracking URI
os.environ.setdefault("MLFLOW_TRACKING_URI", "http://localhost:0")
