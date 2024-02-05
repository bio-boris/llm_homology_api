import pytest


# Define a fixture that will be automatically used by all test functions
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    # Setting environment variables
    monkeypatch.setenv("VERSION", "123")
    monkeypatch.setenv("ROOT_PATH", "mock_sentry_dsn")
    monkeypatch.setenv("AUTH_URL", "user")
    monkeypatch.setenv("VCS_REF", "password")
    monkeypatch.setenv("DOTENV_FILE_LOCATION", ".docker_compose_env")

    # You can also yield here if you need to do some cleanup after tests
    yield  # This is where the test function will run
    # Cleanup code goes here (if any)
