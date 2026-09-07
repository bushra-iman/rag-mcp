import os
import sys

# Make the project root importable regardless of the current working directory
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    ),
)

import pytest

from app import app as flask_app


@pytest.fixture()
def app():
    # Default: auth disabled so endpoint tests don't need headers.
    # Individual tests can enable auth via app.config["API_KEY"].
    flask_app.config.update(TESTING=True, API_KEY="")
    return flask_app


@pytest.fixture()
def client(app):
    return app.test_client()
