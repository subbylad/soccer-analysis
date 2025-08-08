import pandas as pd
import pytest

from analysis.utils import calculate_potential_score


def test_calculate_potential_score_separate_weights():
    player = pd.Series(
        {
            "age": 20,
            "goals_per_90": 0,
            "assists_per_90": 0,
            "progressive_carries": 10,
            "progressive_passes": 5,
            "expected_goals": 2,
            "expected_assists": 1,
            "minutes": 1000,
        }
    )

    score = calculate_potential_score(player)

    # 10*0.05 + 5*0.02 + 1000*0.002 + (23-20)*10 + 2*5 + 1*5 = 47.6
    assert score == pytest.approx(47.6)

