from __future__ import annotations

import pandas as pd

from cs2_analyzer.models import DemoInspection, Participant
from cs2_analyzer.normalization import CanonicalMatch
from cs2_analyzer.report import build_match_overview, timeline_for_match


def _match() -> CanonicalMatch:
    inspection = DemoInspection(
        source_sha256="f" * 64,
        source_filename="sample.dem",
        size_bytes=42,
        map_name="de_mirage",
        parser_version="0.42.0",
        tick_interval_seconds=0.015625,
        competitive_start_tick=0,
        participants=[
            Participant(id="target", display_name="Sobek"),
            Participant(id="enemy", display_name="Enemy"),
        ],
        rounds_observed=2,
        player_deaths_after_start=3,
        player_hurts_after_start=2,
    )
    return CanonicalMatch(
        inspection=inspection,
        rounds=pd.DataFrame(
            [
                {"round_number": 1, "end_tick": 150, "winner_side": "T", "end_reason": "t_killed"},
                {
                    "round_number": 2,
                    "end_tick": 300,
                    "winner_side": "CT",
                    "end_reason": "ct_killed",
                },
            ]
        ),
        kills=pd.DataFrame(
            [
                {
                    "round_number": 1,
                    "tick": 120,
                    "killer_id": "target",
                    "victim_id": "enemy",
                    "killer_team": 2,
                    "victim_team": 3,
                    "weapon": "ak47",
                },
                {
                    "round_number": 2,
                    "tick": 220,
                    "killer_id": "enemy",
                    "victim_id": "target",
                    "killer_team": 3,
                    "victim_team": 2,
                    "weapon": "awp",
                },
                {
                    "round_number": 2,
                    "tick": 240,
                    "killer_id": "target",
                    "victim_id": "target",
                    "killer_team": 2,
                    "victim_team": 2,
                    "weapon": "hegrenade",
                },
                {
                    "round_number": 2,
                    "tick": 260,
                    "killer_id": float("nan"),
                    "victim_id": "target",
                    "killer_team": float("nan"),
                    "victim_team": 2,
                    "weapon": "trigger_hurt",
                },
            ]
        ),
        damages=pd.DataFrame(
            [
                {
                    "round_number": 1,
                    "tick": 100,
                    "attacker_id": "target",
                    "victim_id": "enemy",
                    "damage_health": 40,
                    "weapon": "ak47",
                },
                {
                    "round_number": 2,
                    "tick": 200,
                    "attacker_id": "enemy",
                    "victim_id": "target",
                    "damage_health": 70,
                    "weapon": "awp",
                },
            ]
        ),
    )


def test_match_overview_counts_only_enemy_kills_and_received_hp() -> None:
    overview = build_match_overview(_match(), "target", "f" * 16)

    assert overview.selected_player.display_name == "Sobek"
    assert overview.rounds_played == 2
    assert overview.player_kills == 1
    assert overview.player_deaths == 1
    assert overview.damage_received == 70


def test_timeline_merges_damage_and_kills_in_tick_order_with_round_filter() -> None:
    timeline = timeline_for_match(_match(), round_number=2)

    assert [(event.kind, event.tick) for event in timeline] == [
        ("damage", 200),
        ("kill", 220),
        ("kill", 240),
        ("kill", 260),
    ]
    assert timeline[0].damage_health == 70
    assert timeline[0].actor_name == "Enemy"
    assert timeline[0].victim_name == "Sobek"
    assert timeline[1].weapon == "awp"
    assert timeline[3].actor_id is None
    assert timeline[3].actor_name is None
