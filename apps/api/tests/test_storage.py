from __future__ import annotations

import pandas as pd

from cs2_analyzer.models import DemoInspection
from cs2_analyzer.normalization import CanonicalMatch
from cs2_analyzer.storage import LocalMatchStore


def test_store_writes_only_derived_tables(tmp_path) -> None:
    inspection = DemoInspection(
        source_sha256="a" * 64,
        source_filename="sample.dem",
        size_bytes=42,
        map_name="de_mirage",
        parser_version="0.42.0",
        tick_interval_seconds=0.015625,
        competitive_start_tick=0,
        participants=[],
        rounds_observed=1,
        player_deaths_after_start=1,
        player_hurts_after_start=1,
    )
    match = CanonicalMatch(
        inspection=inspection,
        rounds=pd.DataFrame(
            [{"round_number": 0, "end_tick": 100, "winner_side": "T", "end_reason": "t_killed"}]
        ),
        kills=pd.DataFrame(
            [
                {
                    "round_number": 0,
                    "tick": 90,
                    "killer_id": "a",
                    "victim_id": "b",
                    "killer_team": 2,
                    "victim_team": 3,
                    "weapon": "ak47",
                }
            ]
        ),
        damages=pd.DataFrame(
            [
                {
                    "round_number": 0,
                    "tick": 80,
                    "attacker_id": "a",
                    "victim_id": "b",
                    "attacker_team": 2,
                    "victim_team": 3,
                    "damage_health": 30,
                    "damage_armor": 0,
                    "weapon": "ak47",
                    "hitgroup": "chest",
                }
            ]
        ),
    )
    destination = LocalMatchStore(tmp_path).save(match, "player-a")
    assert (destination / "metadata.json").is_file()
    assert (destination / "rounds.parquet").is_file()
    assert (destination / "kills.parquet").is_file()
    assert not list(destination.glob("*.dem"))
