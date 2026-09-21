from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from .rules import trade_assessments_for_player


class GoldenMismatch(AssertionError):
    """Une scene golden ne correspond plus aux faits normalises."""


class GoldenCase(BaseModel):
    """Une observation stable du corpus golden, sans aucune donnee joueur."""

    id: str = Field(pattern=r"^G(?:0[1-9]|[1-4][0-9]|50)$")
    signal: Literal["trade", "untraded", "opening_kill", "five_v_four", "hp_lost"]
    demo_id: str = Field(min_length=1)
    round_number: int = Field(ge=0)
    tick: int = Field(ge=0)
    expected: str = Field(min_length=1)


def golden_manifest_path() -> Path:
    return Path(__file__).resolve().parents[4] / "fixtures" / "manifests" / "golden.v0.json"


@lru_cache
def load_golden_cases() -> tuple[GoldenCase, ...]:
    """Charge les attentes golden versionnees et independantes des demos brutes."""
    with golden_manifest_path().open(encoding="utf-8") as source:
        payload = json.load(source)
    return tuple(GoldenCase.model_validate(case) for case in payload["cases"])


@lru_cache
def golden_demo_filenames() -> dict[str, str]:
    with golden_manifest_path().open(encoding="utf-8") as source:
        payload = json.load(source)
    return {str(demo_id): str(filename) for demo_id, filename in payload["demos"].items()}


def default_golden_demo_roots() -> tuple[Path, ...]:
    configured = os.environ.get("CS2_ANALYZER_GOLDEN_DEMO_ROOTS")
    if configured:
        return tuple(Path(raw_path) for raw_path in configured.split(os.pathsep) if raw_path)
    program_files_x86 = Path(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"))
    return (
        Path.home() / "Downloads",
        program_files_x86
        / "Steam"
        / "steamapps"
        / "common"
        / "Counter-Strike Global Offensive"
        / "game"
        / "csgo"
        / "replays",
    )


def resolve_golden_demo_paths(*, roots: list[Path] | None = None) -> dict[str, Path]:
    """Retrouve les demoes locales sans versionner leurs chemins absolus."""
    search_roots = roots if roots is not None else list(default_golden_demo_roots())
    resolved: dict[str, Path] = {}
    missing: list[str] = []
    for demo_id, filename in golden_demo_filenames().items():
        path = next(
            (candidate for root in search_roots if (candidate := root / filename).is_file()),
            None,
        )
        if path is None:
            missing.append(f"{demo_id} ({filename})")
        else:
            resolved[demo_id] = path
    if missing:
        raise GoldenMismatch("Demos golden introuvables : " + ", ".join(missing))
    return resolved


def _events_at(kills, case: GoldenCase):
    return kills[(kills["round_number"] == case.round_number) & (kills["tick"] == case.tick)]


def _validate_trade(case: GoldenCase, kills, *, tick_interval_seconds: float | None) -> None:
    for death in _events_at(kills, case).itertuples(index=False):
        if death.victim_id is None:
            continue
        assessments = trade_assessments_for_player(
            kills, str(death.victim_id), tick_interval_seconds=tick_interval_seconds
        )
        if any(
            assessment.death_tick == case.tick and assessment.classification == case.expected
            for assessment in assessments
        ):
            return
    raise GoldenMismatch(f"{case.id}: trade attendu {case.expected} absent au tick {case.tick}")


def _validate_opening_kill(case: GoldenCase, kills) -> None:
    required_columns = {
        "round_number",
        "tick",
        "killer_id",
        "victim_id",
        "killer_team",
        "victim_team",
    }
    if not required_columns.issubset(kills.columns):
        raise GoldenMismatch(f"{case.id}: colonnes de kill insuffisantes")
    enemy_kills = kills[
        kills["killer_id"].notna()
        & kills["victim_id"].notna()
        & kills["killer_team"].notna()
        & kills["victim_team"].notna()
        & (kills["killer_team"] != kills["victim_team"])
        & (kills["round_number"] == case.round_number)
    ]
    if enemy_kills.empty or int(enemy_kills["tick"].min()) != case.tick:
        raise GoldenMismatch(
            f"{case.id}: le tick {case.tick} n'est pas le premier kill ennemi du round"
        )


def _validate_five_v_four(case: GoldenCase, kills) -> None:
    required_columns = {
        "round_number",
        "tick",
        "killer_id",
        "victim_id",
        "killer_team",
        "victim_team",
    }
    if not required_columns.issubset(kills.columns):
        raise GoldenMismatch(f"{case.id}: colonnes de kill insuffisantes")
    expected_team = int(case.expected.removeprefix("advantaged_team_"))
    enemy_kills = kills[
        kills["killer_id"].notna()
        & kills["victim_id"].notna()
        & kills["killer_team"].notna()
        & kills["victim_team"].notna()
        & (kills["killer_id"] != kills["victim_id"])
        & (kills["killer_team"] != kills["victim_team"])
        & (kills["round_number"] == case.round_number)
    ].sort_values("tick")
    dead_players_by_team: dict[int, set[str]] = {}
    for kill in enemy_kills.itertuples(index=False):
        victim_team = int(kill.victim_team)
        killer_team = int(kill.killer_team)
        victim_id = str(kill.victim_id)
        dead_players = dead_players_by_team.setdefault(victim_team, set())
        if victim_id in dead_players:
            continue
        dead_players.add(victim_id)
        if int(kill.tick) != case.tick:
            continue
        alive_killer_team = 5 - len(dead_players_by_team.get(killer_team, set()))
        alive_victim_team = 5 - len(dead_players)
        if killer_team == expected_team and alive_killer_team == 5 and alive_victim_team == 4:
            return
    raise GoldenMismatch(f"{case.id}: ouverture 5v4 attendue absente au tick {case.tick}")


def _validate_damage(case: GoldenCase, damages) -> None:
    required_columns = {"round_number", "tick", "damage_health", "victim_x", "victim_y"}
    if not required_columns.issubset(damages.columns):
        raise GoldenMismatch(f"{case.id}: colonnes de dommage insuffisantes")
    expected_damage = int(case.expected.removeprefix("damage_health_"))
    matches = damages[
        (damages["round_number"] == case.round_number)
        & (damages["tick"] == case.tick)
        & (damages["damage_health"] == expected_damage)
        & damages["victim_x"].notna()
        & damages["victim_y"].notna()
    ]
    if matches.empty:
        raise GoldenMismatch(
            f"{case.id}: dommage {expected_damage} avec position absent au tick {case.tick}"
        )


def validate_golden_case(
    case: GoldenCase,
    *,
    kills,
    damages,
    competitive_start_tick: int,
    tick_interval_seconds: float | None,
) -> None:
    """Verifie une scene golden contre les faits normalises d'une demo locale."""
    if case.tick < competitive_start_tick:
        raise GoldenMismatch(f"{case.id}: la scene appartient a la phase knife exclue")
    if case.signal in {"trade", "untraded"}:
        _validate_trade(case, kills, tick_interval_seconds=tick_interval_seconds)
    elif case.signal == "opening_kill":
        _validate_opening_kill(case, kills)
    elif case.signal == "five_v_four":
        _validate_five_v_four(case, kills)
    else:
        _validate_damage(case, damages)
