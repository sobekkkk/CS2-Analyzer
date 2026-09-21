from __future__ import annotations

import pandas as pd

from cs2_analyzer.rules import trade_assessments_for_player, untraded_death_cells_for_player


def _kills() -> pd.DataFrame:
    return pd.DataFrame(
        [
            # Round 1: trade immediate (0.5 s).
            {
                "round_number": 1,
                "tick": 100,
                "killer_id": "enemy-a",
                "victim_id": "target",
                "killer_team": 3,
                "victim_team": 2,
                "weapon": "ak47",
                "victim_x": 12.0,
                "victim_y": -12.0,
            },
            {
                "round_number": 1,
                "tick": 105,
                "killer_id": "mate-a",
                "victim_id": "enemy-a",
                "killer_team": 2,
                "victim_team": 3,
                "weapon": "m4a1",
            },
            # Round 2: trade timely (2 s).
            {
                "round_number": 2,
                "tick": 200,
                "killer_id": "enemy-b",
                "victim_id": "target",
                "killer_team": 3,
                "victim_team": 2,
                "weapon": "ak47",
                "victim_x": 15.0,
                "victim_y": -12.0,
            },
            {
                "round_number": 2,
                "tick": 220,
                "killer_id": "mate-b",
                "victim_id": "enemy-b",
                "killer_team": 2,
                "victim_team": 3,
                "weapon": "m4a1",
            },
            # Round 3: trade late (4 s).
            {
                "round_number": 3,
                "tick": 300,
                "killer_id": "enemy-c",
                "victim_id": "target",
                "killer_team": 3,
                "victim_team": 2,
                "weapon": "ak47",
                "victim_x": 16.0,
                "victim_y": -12.0,
            },
            {
                "round_number": 3,
                "tick": 340,
                "killer_id": "mate-c",
                "victim_id": "enemy-c",
                "killer_team": 2,
                "victim_team": 3,
                "weapon": "m4a1",
            },
            # Round 4: no trade; two teammates already died, so the death remains
            # eligible for the H-01 map (two teammates were alive before it).
            {
                "round_number": 4,
                "tick": 360,
                "killer_id": "enemy-d",
                "victim_id": "mate-d",
                "killer_team": 3,
                "victim_team": 2,
                "weapon": "ak47",
            },
            {
                "round_number": 4,
                "tick": 370,
                "killer_id": "enemy-e",
                "victim_id": "mate-e",
                "killer_team": 3,
                "victim_team": 2,
                "weapon": "ak47",
            },
            {
                "round_number": 4,
                "tick": 400,
                "killer_id": "enemy-f",
                "victim_id": "target",
                "killer_team": 3,
                "victim_team": 2,
                "weapon": "awp",
                "victim_x": 24.0,
                "victim_y": -4.0,
            },
        ]
    )


def test_trade_assessments_classify_first_eligible_trade_and_untraded_death() -> None:
    result = trade_assessments_for_player(_kills(), "target", tick_interval_seconds=0.1)

    assert [assessment.classification for assessment in result] == [
        "immediate_trade",
        "timely_trade",
        "late_trade",
        "untraded",
    ]
    assert [assessment.trade_delay_seconds for assessment in result] == [0.5, 2.0, 4.0, None]
    assert result[3].alive_teammates_before_death == 2
    assert result[3].killer_id == "enemy-f"


def test_untraded_death_cells_only_keep_eligible_untraded_deaths_with_positions() -> None:
    result = untraded_death_cells_for_player(
        _kills(), "target", tick_interval_seconds=0.1, cell_size=16
    )

    assert len(result) == 1
    assert result[0].cell_x == 1
    assert result[0].cell_y == -1
    assert result[0].occurrence_count == 1
    assert result[0].round_numbers == [4]
    assert result[0].death_ticks == [400]
    assert [evidence.model_dump() for evidence in result[0].evidence] == [
        {"round_number": 4, "tick": 400, "kind": "kill"},
    ]


def test_trade_assessments_do_not_infer_time_without_a_tick_interval() -> None:
    assert trade_assessments_for_player(_kills(), "target", tick_interval_seconds=None) == []
