from unittest.mock import patch, Mock

import pytest
from fastapi import FastAPI

from llm_homology_api.src.clients import CachedAuthClient
from llm_homology_api.src.factory import create_app


@pytest.fixture
def mock_env_vars(monkeypatch):
    # TODO
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("SENTRY_DSN", "mock_sentry_dsn")
    monkeypatch.setenv("METRICS_USERNAME", "user")
    monkeypatch.setenv("METRICS_PASSWORD", "password")
    monkeypatch.setenv("DOTENV_FILE_LOCATION", ".env")


def test_create_app_with_defaults(mock_env_vars):
    #TODO
    app = create_app()
    assert isinstance(app, FastAPI)
    assert isinstance(app.state.auth_client, CachedAuthClient.CachedAuthClient)
