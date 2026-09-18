from __future__ import annotations

import pandas as pd

from cs2_analyzer.rules import damage_cells_for_player


def test_damage_cells_aggregate_received_hp_by_world_grid_cell() -> None:
    damages = pd.DataFrame(
        [
            {
                "round_number": 2,
                "tick": 100,
                "victim_id": "target",
                "damage_health": 20,
                "victim_x": 50.0,
                "victim_y": -50.0,
            },
            {
                "round_number": 2,
                "tick": 120,
                "victim_id": "target",
                "damage_health": 30,
                "victim_x": 90.0,
                "victim_y": -1.0,
            },
            {
                "round_number": 3,
                "tick": 200,
                "victim_id": "target",
                "damage_health": 80,
                "victim_x": 110.0,
                "victim_y": 10.0,
            },
            {
                "round_number": 3,
                "tick": 220,
                "victim_id": "other",
                "damage_health": 99,
                "victim_x": 50.0,
                "victim_y": -50.0,
            },
            {
                "round_number": 4,
                "tick": 240,
                "victim_id": "target",
                "damage_health": 10,
                "victim_x": None,
                "victim_y": 10.0,
            },
        ]
    )

    result = damage_cells_for_player(damages, "target", cell_size=100)

    assert [(cell.cell_x, cell.cell_y) for cell in result] == [(1, 0), (0, -1)]
    assert result[0].total_damage == 80
    assert result[0].impact_count == 1
    assert result[0].round_count == 1
    assert result[0].average_damage_per_impact == 80.0
    assert result[1].total_damage == 50
    assert result[1].impact_count == 2
    assert result[1].round_count == 1
    assert result[1].average_damage_per_impact == 25.0


def test_damage_cells_reject_non_positive_grid_sizes() -> None:
    damages = pd.DataFrame()

    try:
        damage_cells_for_player(damages, "target", cell_size=0)
    except ValueError as error:
        assert str(error) == "cell_size must be positive"
    else:
        raise AssertionError("A non-positive cell size must be rejected")
