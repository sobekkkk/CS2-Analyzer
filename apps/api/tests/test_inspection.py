from __future__ import annotations

import pandas as pd

from cs2_analyzer.inspection import competitive_start_tick, participant_id


def test_competitive_start_excludes_only_initial_knife_phase() -> None:
    deaths = pd.DataFrame(
        [
            {"tick": 120, "weapon": "knife"},
            {"tick": 220, "weapon": "knife_karambit"},
            {"tick": 800, "weapon": "glock"},
        ]
    )
    starts = pd.DataFrame([{"tick": 250}, {"tick": 400}])
    officially_ended = pd.DataFrame([{"tick": 1000}])

    assert competitive_start_tick(deaths, starts, officially_ended) == 250


def test_competitive_start_does_not_remove_a_normal_pistol_round() -> None:
    deaths = pd.DataFrame([{"tick": 800, "weapon": "glock"}])
    starts = pd.DataFrame([{"tick": 400}])
    officially_ended = pd.DataFrame([{"tick": 1000}])

    assert competitive_start_tick(deaths, starts, officially_ended) == 0


def test_participant_id_is_stable_and_does_not_return_raw_steam_id() -> None:
    first = participant_id("76561198000000000")

    assert first == participant_id("76561198000000000")
    assert "76561198000000000" not in first
