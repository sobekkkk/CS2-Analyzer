from __future__ import annotations

import pandas as pd

from cs2_analyzer.inspection import participant_id
from cs2_analyzer.models import DemoInspection
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


def test_requests_death_coordinates_and_preserves_them_for_h01(monkeypatch, tmp_path) -> None:
    """H-01 needs the victim position attached to the death event."""

    calls: list[tuple[str, list[str] | None]] = []

    class FakeParser:
        def __init__(self, _path: str) -> None:
            pass

        def parse_event(self, event_name: str, *, player=None, other=None):
            calls.append((event_name, player))
            if event_name == "player_death":
                return pd.DataFrame(
                    [
                        {
                            "tick": 100,
                            "total_rounds_played": 1,
                            "user_steamid": "76561198000000001",
                            "attacker_steamid": "76561198000000002",
                            "user_team_num": 2,
                            "attacker_team_num": 3,
                            "user_X": 128.5,
                            "user_Y": -256.5,
                            "user_Z": 64.0,
                            "weapon": "ak47",
                        }
                    ]
                )
            return pd.DataFrame(columns=["tick"])

        def parse_ticks(self, _props, *, ticks):
            return pd.DataFrame(columns=["tick", "steamid", "team_num", "is_alive", "X", "Y"])

    inspection = DemoInspection(
        source_filename="mirage.dem",
        source_sha256="a" * 64,
        size_bytes=1,
        map_name="de_mirage",
        parser_version="0.42.0",
        tick_interval_seconds=0.015625,
        competitive_start_tick=0,
        participants=[],
        rounds_observed=1,
        player_deaths_after_start=1,
        player_hurts_after_start=0,
    )

    class FakeInspector:
        def inspect(self, _path):
            return inspection

    monkeypatch.setattr("cs2_analyzer.normalization.DemoParser", FakeParser)

    match = DemoNormalizer(inspector=FakeInspector()).normalize(tmp_path / "mirage.dem")

    assert ("player_death", ["team_num", "X", "Y", "Z"]) in calls
    assert match.kills.loc[0, ["victim_x", "victim_y", "victim_z"]].to_dict() == {
        "victim_x": 128.5,
        "victim_y": -256.5,
        "victim_z": 64.0,
    }
