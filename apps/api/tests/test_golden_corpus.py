from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd
import pytest

from cs2_analyzer.golden import (
    GoldenCase,
    GoldenMismatch,
    golden_demo_filenames,
    load_golden_cases,
    resolve_golden_demo_paths,
    validate_golden_case,
)


def test_golden_v0_contains_the_complete_immutable_signal_set() -> None:
    cases = load_golden_cases()

    assert len(cases) == 50
    assert [case.id for case in cases] == [f"G{number:02d}" for number in range(1, 51)]
    assert Counter(case.signal for case in cases) == {
        "trade": 20,
        "untraded": 10,
        "opening_kill": 10,
        "five_v_four": 5,
        "hp_lost": 5,
    }
    assert cases[0].model_dump() == {
        "id": "G01",
        "signal": "trade",
        "demo_id": "faceit-3-1",
        "round_number": 6,
        "tick": 47261,
        "expected": "immediate_trade",
    }


@pytest.mark.parametrize(
    ("case", "kills", "damages"),
    [
        (
            GoldenCase(
                id="G01",
                signal="trade",
                demo_id="demo",
                round_number=0,
                tick=100,
                expected="immediate_trade",
            ),
            pd.DataFrame(
                [
                    {
                        "round_number": 0,
                        "tick": 100,
                        "killer_id": "enemy",
                        "victim_id": "target",
                        "killer_team": 3,
                        "victim_team": 2,
                    },
                    {
                        "round_number": 0,
                        "tick": 105,
                        "killer_id": "ally",
                        "victim_id": "enemy",
                        "killer_team": 2,
                        "victim_team": 3,
                    },
                ]
            ),
            pd.DataFrame(),
        ),
        (
            GoldenCase(
                id="G21",
                signal="untraded",
                demo_id="demo",
                round_number=0,
                tick=100,
                expected="untraded",
            ),
            pd.DataFrame(
                [
                    {
                        "round_number": 0,
                        "tick": 100,
                        "killer_id": "enemy",
                        "victim_id": "target",
                        "killer_team": 3,
                        "victim_team": 2,
                    }
                ]
            ),
            pd.DataFrame(),
        ),
        (
            GoldenCase(
                id="G31",
                signal="opening_kill",
                demo_id="demo",
                round_number=0,
                tick=100,
                expected="first_enemy_kill",
            ),
            pd.DataFrame(
                [
                    {
                        "round_number": 0,
                        "tick": 90,
                        "killer_id": "ally",
                        "victim_id": "friend",
                        "killer_team": 2,
                        "victim_team": 2,
                    },
                    {
                        "round_number": 0,
                        "tick": 100,
                        "killer_id": "target",
                        "victim_id": "enemy",
                        "killer_team": 2,
                        "victim_team": 3,
                    },
                ]
            ),
            pd.DataFrame(),
        ),
        (
            GoldenCase(
                id="G41",
                signal="five_v_four",
                demo_id="demo",
                round_number=0,
                tick=100,
                expected="advantaged_team_2",
            ),
            pd.DataFrame(
                [
                    {
                        "round_number": 0,
                        "tick": 100,
                        "killer_id": "target",
                        "victim_id": "enemy",
                        "killer_team": 2,
                        "victim_team": 3,
                    }
                ]
            ),
            pd.DataFrame(),
        ),
        (
            GoldenCase(
                id="G46",
                signal="hp_lost",
                demo_id="demo",
                round_number=0,
                tick=100,
                expected="damage_health_71",
            ),
            pd.DataFrame(),
            pd.DataFrame(
                [
                    {
                        "round_number": 0,
                        "tick": 100,
                        "damage_health": 71,
                        "victim_x": 10.0,
                        "victim_y": -10.0,
                    }
                ]
            ),
        ),
    ],
)
def test_validates_each_golden_signal_against_normalized_facts(case, kills, damages) -> None:
    validate_golden_case(
        case,
        kills=kills,
        damages=damages,
        competitive_start_tick=0,
        tick_interval_seconds=0.1,
    )


def test_rejects_a_golden_scene_from_before_competitive_start() -> None:
    case = GoldenCase(
        id="G01",
        signal="trade",
        demo_id="demo",
        round_number=0,
        tick=99,
        expected="immediate_trade",
    )

    with pytest.raises(GoldenMismatch, match="phase knife"):
        validate_golden_case(
            case,
            kills=pd.DataFrame(),
            damages=pd.DataFrame(),
            competitive_start_tick=100,
            tick_interval_seconds=0.1,
        )


def test_resolves_the_local_demos_without_storing_their_absolute_paths(tmp_path: Path) -> None:
    filenames = golden_demo_filenames()
    for filename in filenames.values():
        (tmp_path / filename).touch()

    paths = resolve_golden_demo_paths(roots=[tmp_path])

    assert set(paths) == set(filenames)
    assert all(path.parent == tmp_path for path in paths.values())
