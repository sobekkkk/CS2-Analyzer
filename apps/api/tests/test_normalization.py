from __future__ import annotations

import pandas as pd

from cs2_analyzer.inspection import participant_id
from cs2_analyzer.normalization import DemoNormalizer


def test_normalizes_requested_player_samples_without_raw_steam_ids() -> None:
    raw_samples = pd.DataFrame(
        [
            {
                "tick": 90,
                "steamid": "76561198000000001",
                "team_num": 2,
                "is_alive": True,
                "X": 128.5,
                "Y": -256.5,
            },
            {
                "tick": 110,
                "steamid": "76561198000000002",
                "team_num": 3,
                "is_alive": False,
                "X": 512.0,
                "Y": -512.0,
            },
        ]
    )

    result = DemoNormalizer._normalize_player_samples(raw_samples, start_tick=100)

    assert result.to_dict("records") == [
        {
            "player_id": participant_id("76561198000000002"),
            "tick": 110,
            "team_num": 3,
            "is_alive": False,
            "x": 512.0,
            "y": -512.0,
        }
    ]


def test_normalizes_round_end_with_the_same_zero_based_number_as_kills() -> None:
    round_ends = pd.DataFrame(
        [
            {
                "tick": 0,
                "total_rounds_played": 0,
                "winner": None,
                "reason": None,
            },
            {
                "tick": 13387,
                "total_rounds_played": 1,
                "winner": "CT",
                "reason": "ct_killed",
            },
        ]
    )

    result = DemoNormalizer._normalize_rounds(round_ends, start_tick=0)

    assert result.to_dict("records") == [
        {
            "round_number": 0,
            "end_tick": 13387,
            "winner_side": "CT",
            "end_reason": "ct_killed",
        }
    ]
