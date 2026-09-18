from __future__ import annotations

import pandas as pd

from cs2_analyzer.rules import opening_kills_for_player


def test_opening_kills_ignore_team_kills_and_keep_first_enemy_kill_per_round() -> None:
    kills = pd.DataFrame(
        [
            {
                "round_number": 4,
                "tick": 100,
                "killer_id": "friend",
                "victim_id": "ally",
                "killer_team": 2,
                "victim_team": 2,
                "weapon": "ak47",
            },
            {
                "round_number": 4,
                "tick": 120,
                "killer_id": "target",
                "victim_id": "enemy",
                "killer_team": 2,
                "victim_team": 3,
                "weapon": "ak47",
            },
            {
                "round_number": 4,
                "tick": 140,
                "killer_id": "target",
                "victim_id": "enemy-2",
                "killer_team": 2,
                "victim_team": 3,
                "weapon": "ak47",
            },
            {
                "round_number": 5,
                "tick": 200,
                "killer_id": "other",
                "victim_id": "target",
                "killer_team": 3,
                "victim_team": 2,
                "weapon": "awp",
            },
        ]
    )

    result = opening_kills_for_player(kills, "target")

    assert len(result) == 1
    assert result[0].round_number == 4
    assert result[0].tick == 120
    assert result[0].weapon == "ak47"
