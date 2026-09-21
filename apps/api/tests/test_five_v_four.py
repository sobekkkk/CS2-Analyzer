from __future__ import annotations

import pandas as pd

from cs2_analyzer.rules import five_v_four_cells_for_player, five_v_four_sample_ticks


def test_five_v_four_samples_only_the_advantaged_alive_player_before_next_death() -> None:
    kills = pd.DataFrame(
        [
            {
                "round_number": 4,
                "tick": 100,
                "killer_id": "ally-1",
                "victim_id": "enemy-1",
                "killer_team": 2,
                "victim_team": 3,
            },
            {
                "round_number": 4,
                "tick": 125,
                "killer_id": "ally-2",
                "victim_id": "enemy-2",
                "killer_team": 2,
                "victim_team": 3,
            },
        ]
    )
    rounds = pd.DataFrame([{"round_number": 4, "end_tick": 200}])
    player_samples = pd.DataFrame(
        [
            {
                "player_id": "target",
                "tick": 110,
                "team_num": 2,
                "is_alive": True,
                "x": 300.0,
                "y": -300.0,
            },
            {
                "player_id": "target",
                "tick": 120,
                "team_num": 2,
                "is_alive": True,
                "x": 350.0,
                "y": -300.0,
            },
            {
                "player_id": "target",
                "tick": 130,
                "team_num": 2,
                "is_alive": True,
                "x": 400.0,
                "y": -300.0,
            },
            {
                "player_id": "target",
                "tick": 110,
                "team_num": 2,
                "is_alive": False,
                "x": 300.0,
                "y": -300.0,
            },
            {
                "player_id": "target",
                "tick": 120,
                "team_num": 3,
                "is_alive": True,
                "x": 350.0,
                "y": -300.0,
            },
        ]
    )

    result = five_v_four_cells_for_player(
        kills,
        rounds,
        player_samples,
        "target",
        tick_interval_seconds=0.1,
        cell_size=256,
    )

    assert five_v_four_sample_ticks(kills, rounds, tick_interval_seconds=0.1) == [110, 120]
    assert [cell.model_dump() for cell in result] == [
        {
            "rule_id": "H-03",
            "rule_version": "0.1",
            "cell_x": 1,
            "cell_y": -2,
            "sample_count": 2,
            "round_count": 1,
            "round_numbers": [4],
            "confidence": "inferred",
            "evidence": [
                {"round_number": 4, "tick": 110, "kind": "position_sample"},
                {"round_number": 4, "tick": 120, "kind": "position_sample"},
            ],
        }
    ]


def test_five_v_four_does_not_treat_four_vs_three_as_a_new_window() -> None:
    kills = pd.DataFrame(
        [
            {
                "round_number": 7,
                "tick": 100,
                "killer_id": "ally-1",
                "victim_id": "enemy-1",
                "killer_team": 2,
                "victim_team": 3,
            },
            {
                "round_number": 7,
                "tick": 120,
                "killer_id": "enemy-2",
                "victim_id": "ally-2",
                "killer_team": 3,
                "victim_team": 2,
            },
            {
                "round_number": 7,
                "tick": 140,
                "killer_id": "ally-3",
                "victim_id": "enemy-3",
                "killer_team": 2,
                "victim_team": 3,
            },
        ]
    )
    rounds = pd.DataFrame([{"round_number": 7, "end_tick": 300}])

    assert five_v_four_sample_ticks(kills, rounds, tick_interval_seconds=0.1) == [110]


def test_five_v_four_returns_no_signal_when_an_old_report_has_no_position_table() -> None:
    kills = pd.DataFrame(
        [
            {
                "round_number": 2,
                "tick": 100,
                "killer_id": "ally",
                "victim_id": "enemy",
                "killer_team": 2,
                "victim_team": 3,
            }
        ]
    )
    rounds = pd.DataFrame([{"round_number": 2, "end_tick": 200}])

    assert (
        five_v_four_cells_for_player(
            kills,
            rounds,
            pd.DataFrame(),
            "target",
            tick_interval_seconds=0.1,
        )
        == []
    )
