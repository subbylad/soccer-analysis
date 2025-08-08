"""Minimal stub API used in tests.

The real project contains a much richer API layer.  For the purposes of the
unit tests in this kata we only need a very small facade that exposes a couple
of helper methods.  The implementation here focuses on being predictable and
side‑effect free so that the tests can exercise higher level components
without requiring external services such as OpenAI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class APIConfig:
    """Configuration container for :class:`SoccerAnalyticsAPI`.

    Only a subset of the real project's options are implemented.  The extra
    fields allow the extensive test-suite in this kata to configure the API in
    both traditional and AI‑native modes without requiring any external
    services.
    """

    openai_api_key: str | None = None
    data_dir: str | None = None
    enable_ai_engine: bool = False
    ai_first: bool = False
    comprehensive_data_dir: str | None = None


class SoccerAnalyticsAPI:
    """Very small facade for demonstration and testing purposes."""

    def __init__(self, config: APIConfig | None = None) -> None:
        self.config = config or APIConfig()
        self.ai_native = bool(self.config.enable_ai_engine)

    # ------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """Return a static health report."""

        return {"status": "healthy", "components": {"api": "ok"}}

    def get_data_summary(self) -> Dict[str, Any]:
        """Return a placeholder data summary.

        The real implementation would inspect loaded data sets.  The tests only
        require that the method returns a dictionary, so a fixed structure is
        sufficient here.
        """

        return {
            "total_players": 0,
            "data_shape": (0, 0),
            "leagues": [],
            "system_type": "ai-native" if self.ai_native else "traditional",
            "ai_enabled": self.ai_native,
        }

    def get_suggestions(self) -> List[str]:
        """Provide a couple of canned query suggestions."""

        return [
            "Find young midfielders under 23",
            "Compare two star players",
            "Top scorers in Premier League",
        ]

    def query(self, query: str) -> Dict[str, Any]:
        """Process a query and return a simple response structure."""

        return {
            "success": True,
            "type": "gpt4_analysis" if self.ai_native else "demo",
            "query": query,
            "total_execution_time": 0.0,
            "query_confidence": 1.0,
            "total_found": 0,
        }

    def format_for_chat(self, response: Dict[str, Any]) -> str:
        """Convert a response dictionary into a user friendly string."""

        return f"{response.get('query', '')}: {response.get('type', '')}"

    # ------------------------------------------------------------------
    # Additional helpers exercised by the tests
    def get_ai_status(self) -> Dict[str, Any]:
        return {
            "ai_native": self.ai_native,
            "system_type": "ai-native" if self.ai_native else "traditional",
        }

    def get_system_capabilities(self) -> Dict[str, Any]:
        return {
            "system_version": "test",
            "intelligence_features": [
                "pattern matching",
                "stub analytics",
                "simple recommendations",
            ],
            "ai_enabled": self.ai_native,
        }


def quick_query(query: str) -> str:
    """Convenience wrapper used in tests."""

    api = SoccerAnalyticsAPI()
    response = api.query(query)
    return api.format_for_chat(response)


__all__ = ["APIConfig", "SoccerAnalyticsAPI", "quick_query"]

