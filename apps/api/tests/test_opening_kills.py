from __future__ import annotations

import pandas as pd

from cs2_analyzer.rules import opening_kill_cells_for_player, opening_kills_for_player


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


def test_opening_kills_use_only_the_exact_killer_position_sample_and_group_cells() -> None:
    kills = pd.DataFrame(
        [
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
                "round_number": 5,
                "tick": 220,
                "killer_id": "target",
                "victim_id": "enemy-2",
                "killer_team": 2,
                "victim_team": 3,
                "weapon": "m4a1",
            },
        ]
    )
    player_samples = pd.DataFrame(
        [
            {
                "player_id": "target",
                "tick": 119,
                "team_num": 2,
                "is_alive": True,
                "x": 999,
                "y": 999,
            },
            {
                "player_id": "target",
                "tick": 120,
                "team_num": 2,
                "is_alive": True,
                "x": 300,
                "y": -400,
            },
            {
                "player_id": "target",
                "tick": 220,
                "team_num": 2,
                "is_alive": True,
                "x": 310,
                "y": -390,
            },
        ]
    )

    openings = opening_kills_for_player(kills, "target", player_samples)
    cells = opening_kill_cells_for_player(kills, "target", player_samples, cell_size=256)

    assert [(opening.killer_x, opening.killer_y) for opening in openings] == [
        (300.0, -400.0),
        (310.0, -390.0),
    ]
    assert len(cells) == 1
    assert (cells[0].cell_x, cells[0].cell_y) == (1, -2)
    assert cells[0].occurrence_count == 2
    assert cells[0].round_numbers == [4, 5]
    assert [(evidence.round_number, evidence.tick) for evidence in cells[0].evidence] == [
        (4, 120),
        (5, 220),
    ]
