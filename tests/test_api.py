import sys
import os
from pathlib import Path

# Ensure project root is on sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from api.ai_native_api import RevolutionaryAIAPI
import pytest

@pytest.fixture(scope="module")
def api():
    """Provide an initialized RevolutionaryAIAPI instance."""
    return RevolutionaryAIAPI(openai_api_key="test")


def test_api_initialization(api):
    """API initializes and provides ai_scout engine."""
    assert isinstance(api, RevolutionaryAIAPI)
    assert api.ai_scout is not None


def test_health_check(api):
    """Health check reports a healthy status."""
    health = api.health_check()
    assert health["status"] == "healthy"
    assert health["service"] == "ai_native_soccer_scout"


def test_short_query_returns_error(api):
    """Short queries should return an error without calling external services."""
    response = api.query("hi")
    assert response["success"] is False
    assert response["error"] == "Query too short - please provide a more detailed question"

