"""Lightweight player analysis utilities used in tests.

This module provides a small ``CleanPlayerAnalyzer`` class that can load the
cleaned player dataset produced in the tests and exposes a handful of helper
methods.  The implementation intentionally focuses on the behaviour exercised
by the unit tests rather than providing a full production ready feature set.

The analyzer expects a directory containing a ``player_standard_clean.csv``
file whose index columns are ``league``, ``season``, ``team`` and ``player``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pandas as pd

from .utils import calculate_potential_score


@dataclass
class CleanPlayerAnalyzer:
    """Simple wrapper around the cleaned player dataset.

    The class is deliberately small – only the features required by the unit
    tests are implemented.  Each public method verifies that data has been
    loaded and raises ``ValueError`` otherwise so that tests can exercise error
    paths easily.
    """

    data_dir: Path
    standard_data: Optional[pd.DataFrame] = None

    def __init__(self, data_dir: str | Path) -> None:
        data_path = Path(data_dir)
        if not data_path.exists():
            raise FileNotFoundError("Data directory does not exist")

        csv_path = data_path / "player_standard_clean.csv"
        if not csv_path.exists():
            raise FileNotFoundError("Standard data file not found")

        # The test data writes the MultiIndex to CSV; restoring it requires
        # specifying the index columns explicitly.
        self.standard_data = pd.read_csv(csv_path, index_col=[0, 1, 2, 3])
        self.data_dir = data_path

    # ------------------------------------------------------------------
    # Internal helpers
    def _check_loaded(self) -> pd.DataFrame:
        if self.standard_data is None:
            raise ValueError("No data loaded")
        return self.standard_data

    # ------------------------------------------------------------------
    # Query helpers used throughout the tests
    def search_players(
        self,
        name: str,
        position: Optional[str] = None,
        min_minutes: Optional[int] = None,
    ) -> pd.DataFrame:
        """Return players whose name matches ``name``.

        Parameters mirror those used in the tests allowing filtering by
        position and minimum number of minutes played.
        """

        df = self._check_loaded()
        result = df[df.index.get_level_values("player").str.contains(name, case=False)]

        if position is not None:
            result = result[result["position"].str.contains(position, case=False)]
        if min_minutes is not None:
            result = result[result["minutes"] >= min_minutes]

        return result

    def compare_players(self, players: List[str]) -> pd.DataFrame:
        """Return rows for the given ``players``.

        Raises ``ValueError`` if none of the players are present.
        """

        df = self._check_loaded().reset_index()
        result = df[df["player"].isin(players)]

        if result.empty:
            raise ValueError("No players found from the provided list")

        return result

    def get_players_by_position(self, position: str) -> pd.DataFrame:
        df = self._check_loaded()
        return df[df["position"].str.contains(position, case=False)]

    def get_position_leaders(
        self, position: str, stat: str, top_n: int = 5
    ) -> pd.DataFrame:
        df = self._check_loaded()

        if stat not in df.columns:
            raise ValueError(f"Stat '{stat}' not found")

        pos_df = df[df["position"].str.contains(position, case=False)]
        return pos_df.sort_values(stat, ascending=False).head(top_n)

    def get_young_prospects(
        self, max_age: int = 23, min_minutes: int = 1000
    ) -> pd.DataFrame:
        df = self._check_loaded()
        prospects = df[(df["age"] < max_age) & (df["minutes"] >= min_minutes)].copy()

        if prospects.empty:
            return prospects

        prospects["potential_score"] = prospects.apply(
        lambda row: calculate_potential_score(row), axis=1
        )
        return prospects.sort_values("potential_score", ascending=False)

    # ------------------------------------------------------------------
    @property
    def data_summary(self) -> dict:
        df = self._check_loaded()
        leagues = list(df.index.get_level_values("league").unique())
        return {
            "total_players": len(df),
            "data_shape": df.shape,
            "leagues": leagues,
            "age_range": (int(df["age"].min()), int(df["age"].max())),
        }

