# from unittest.mock import patch, Mock
#
# import pytest
# from fastapi import FastAPI
#
# from src.clients.CachedAuthClient import CachedAuthClient
# from factory import create_app
#
#
# import pytest
#
#
# # Define a fixture that will be automatically used by all test functions
# @pytest.fixture(autouse=True)
# def mock_env_vars(monkeypatch):
#     # Setting environment variables
#     monkeypatch.setenv("VERSION", "123")
#     monkeypatch.setenv("ROOT_PATH", "mock_sentry_dsn")
#     monkeypatch.setenv("AUTH_URL", "user")
#     monkeypatch.setenv("VCS_REF", "password")
#     monkeypatch.setenv("DOTENV_FILE_LOCATION", ".docker_compose_env")
#
#     # You can also yield here if you need to do some cleanup after tests
#     yield  # This is where the test function will run
#     # Cleanup code goes here (if any)
#
#
# def test_create_app_with_defaults(mock_env_vars):
#     # TODO
#     app = create_app()
#     assert isinstance(app, FastAPI)
#     # TODO Something with paths
#     # assert isinstance(app.state.auth_client, CachedAuthClient)
