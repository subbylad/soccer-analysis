"""Global pytest fixtures for the repository.

These fixtures provide simple objects used by the hand-written tests which were
originally intended to run as standalone scripts.  By offering them as pytest
fixtures we can execute the same tests under the automated suite.
"""

import pytest

from api.main_api import SoccerAnalyticsAPI


@pytest.fixture
def api() -> SoccerAnalyticsAPI:
    """Return a fresh ``SoccerAnalyticsAPI`` instance for each test."""

    return SoccerAnalyticsAPI()


@pytest.fixture
def openai_key() -> str:
    """Provide a dummy OpenAI API key for tests that expect one."""

    return "test-key"

