from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

import pandas as pd
from pydantic import BaseModel

from .models import Evidence


class OpeningKill(BaseModel):
    """Preuve H-02 : premier kill ennemi d'un round par le joueur cible."""

    rule_id: str = "H-02"
    rule_version: str = "0.1"
    round_number: int
    tick: int
    weapon: str
    killer_team: int
    killer_x: float | None = None
    killer_y: float | None = None
    confidence: str = "direct"


class OpeningKillCell(BaseModel):
    """Agrégat spatial H-02, uniquement avec une position de tireur exacte."""

    rule_id: str = "H-02"
    rule_version: str = "0.1"
    cell_x: int
    cell_y: int
    occurrence_count: int
    round_count: int
    round_numbers: list[int]
    confidence: str = "direct"
    evidence: list[Evidence]


class DamageCell(BaseModel):
    """Preuve H-04 : HP recus dans une cellule de grille monde."""

    rule_id: str = "H-04"
    rule_version: str = "0.1"
    cell_x: int
    cell_y: int
    total_damage: int
    impact_count: int
    round_count: int
    round_numbers: list[int]
    average_damage_per_impact: float
    confidence: str = "direct"
    evidence: list[Evidence]


class TradeAssessment(BaseModel):
    """Preuve H-01 : statut du trade apres la mort du joueur cible.

    Le statut est temporel. Il ne pretend pas que les coequipiers avaient une
    ligne de vue, une information ou une trajectoire praticable.
    """

    rule_id: str = "H-01"
    rule_version: str = "0.1"
    round_number: int
    death_tick: int
    killer_id: str
    weapon: str
    classification: Literal["immediate_trade", "timely_trade", "late_trade", "untraded"]
    trade_tick: int | None = None
    trade_delay_seconds: float | None = None
    alive_teammates_before_death: int
    death_x: float | None = None
    death_y: float | None = None
    confidence: str = "inferred"


class UntradedDeathCell(BaseModel):
    """Agregat H-01 pour la grille monde, avec les preuves navigables."""

    rule_id: str = "H-01"
    rule_version: str = "0.1"
    cell_x: int
    cell_y: int
    occurrence_count: int
    round_count: int
    round_numbers: list[int]
    death_ticks: list[int]
    confidence: str = "inferred"
    evidence: list[Evidence]


class FiveVFourCell(BaseModel):
    """Agrégat H-03 des positions fiables après un avantage exactement 5v4."""

    rule_id: str = "H-03"
    rule_version: str = "0.1"
    cell_x: int
    cell_y: int
    sample_count: int
    round_count: int
    round_numbers: list[int]
    confidence: str = "inferred"
    evidence: list[Evidence]


@dataclass(frozen=True)
class _FiveVFourWindow:
    round_number: int
    start_tick: int
    end_tick_exclusive: int
    advantaged_team: int


def _valid_enemy_kills(kills: pd.DataFrame) -> pd.DataFrame:
    required_columns = {
        "round_number",
        "tick",
        "killer_id",
        "victim_id",
        "killer_team",
        "victim_team",
    }
    missing_columns = required_columns.difference(kills.columns)
    if missing_columns:
        raise ValueError("kills is missing columns: " + ", ".join(sorted(missing_columns)))
    return kills[
        kills["killer_id"].notna()
        & kills["victim_id"].notna()
        & kills["killer_team"].notna()
        & kills["victim_team"].notna()
        & (kills["killer_id"] != kills["victim_id"])
        & (kills["killer_team"] != kills["victim_team"])
    ].copy()


def _five_v_four_windows(
    kills: pd.DataFrame,
    rounds: pd.DataFrame,
    *,
    tick_interval_seconds: float | None,
) -> list[_FiveVFourWindow]:
    """Construit les fenêtres strictes qui suivent le passage à 5v4.

    Le modèle est volontairement limité au format compétitif 5v5. Une fenêtre
    se ferme au prochain frag, à la fin du round ou après six secondes. Sa
    borne de fin est exclusive : un échantillon pris sur le tick d'un nouveau
    frag ne peut pas être attribué à l'état précédent.
    """
    if tick_interval_seconds is None or tick_interval_seconds <= 0:
        return []
    valid_kills = _valid_enemy_kills(kills).sort_values(["round_number", "tick"])
    if valid_kills.empty:
        return []

    round_end_ticks: dict[int, int] = {}
    if {"round_number", "end_tick"}.issubset(rounds.columns):
        valid_rounds = rounds[rounds["round_number"].notna() & rounds["end_tick"].notna()]
        round_end_ticks = {
            int(round_.round_number): int(round_.end_tick)
            for round_ in valid_rounds.itertuples(index=False)
        }

    max_window_ticks = round(6 / tick_interval_seconds)
    windows: list[_FiveVFourWindow] = []
    for round_number, round_kills in valid_kills.groupby("round_number", sort=False):
        events = list(round_kills.itertuples(index=False))
        dead_players_by_team: dict[int, set[str]] = {}
        for index, kill in enumerate(events):
            killer_team = int(kill.killer_team)
            victim_team = int(kill.victim_team)
            victim_id = str(kill.victim_id)
            dead_players = dead_players_by_team.setdefault(victim_team, set())
            if victim_id in dead_players:
                continue
            dead_players.add(victim_id)
            alive_killer_team = 5 - len(dead_players_by_team.get(killer_team, set()))
            alive_victim_team = 5 - len(dead_players)
            if alive_killer_team != 5 or alive_victim_team != 4:
                continue

            start_tick = int(kill.tick)
            later_death_ticks = [
                int(later_kill.tick)
                for later_kill in events[index + 1 :]
                if int(later_kill.tick) > start_tick
            ]
            end_tick_candidates = [start_tick + max_window_ticks + 1]
            if later_death_ticks:
                end_tick_candidates.append(min(later_death_ticks))
            round_end_tick = round_end_ticks.get(int(round_number))
            if round_end_tick is not None:
                end_tick_candidates.append(round_end_tick)
            end_tick_exclusive = min(end_tick_candidates)
            if end_tick_exclusive > start_tick:
                windows.append(
                    _FiveVFourWindow(
                        round_number=int(round_number),
                        start_tick=start_tick,
                        end_tick_exclusive=end_tick_exclusive,
                        advantaged_team=killer_team,
                    )
                )
    return windows


def five_v_four_sample_ticks(
    kills: pd.DataFrame,
    rounds: pd.DataFrame,
    *,
    tick_interval_seconds: float | None,
) -> list[int]:
    """Retourne les seuls ticks dont les positions doivent être conservées."""
    if tick_interval_seconds is None or tick_interval_seconds <= 0:
        return []
    one_second_ticks = round(1 / tick_interval_seconds)
    if one_second_ticks <= 0:
        return []
    sample_ticks: set[int] = set()
    for window in _five_v_four_windows(kills, rounds, tick_interval_seconds=tick_interval_seconds):
        for offset in range(one_second_ticks, (6 * one_second_ticks) + 1, one_second_ticks):
            sample_tick = window.start_tick + offset
            if sample_tick < window.end_tick_exclusive:
                sample_ticks.add(sample_tick)
    return sorted(sample_ticks)


def five_v_four_cells_for_player(
    kills: pd.DataFrame,
    rounds: pd.DataFrame,
    player_samples: pd.DataFrame,
    player_id: str,
    *,
    tick_interval_seconds: float | None,
    cell_size: int = 256,
) -> list[FiveVFourCell]:
    """Agrège les positions d'un joueur vivant dans les fenêtres H-03."""
    if cell_size <= 0:
        raise ValueError("cell_size must be positive")
    if player_samples.empty and len(player_samples.columns) == 0:
        return []
    required_columns = {"player_id", "tick", "team_num", "is_alive", "x", "y"}
    missing_columns = required_columns.difference(player_samples.columns)
    if missing_columns:
        raise ValueError("player_samples is missing columns: " + ", ".join(sorted(missing_columns)))
    windows = _five_v_four_windows(kills, rounds, tick_interval_seconds=tick_interval_seconds)
    if not windows:
        return []

    eligible_samples: list[tuple[_FiveVFourWindow, pd.Series]] = []
    target_samples = player_samples[player_samples["player_id"] == player_id]
    for window in windows:
        sample_ticks = {
            tick
            for tick in five_v_four_sample_ticks(
                kills, rounds, tick_interval_seconds=tick_interval_seconds
            )
            if window.start_tick < tick < window.end_tick_exclusive
        }
        in_window = target_samples[
            target_samples["tick"].isin(sample_ticks)
            & (target_samples["team_num"] == window.advantaged_team)
            & target_samples["is_alive"].eq(True)
            & target_samples["x"].notna()
            & target_samples["y"].notna()
        ]
        eligible_samples.extend((window, sample) for _, sample in in_window.iterrows())

    grouped: dict[tuple[int, int], list[tuple[_FiveVFourWindow, pd.Series]]] = {}
    for window, sample in eligible_samples:
        cell = (
            math.floor(float(sample["x"]) / cell_size),
            math.floor(float(sample["y"]) / cell_size),
        )
        grouped.setdefault(cell, []).append((window, sample))
    cells = [
        FiveVFourCell(
            cell_x=cell_x,
            cell_y=cell_y,
            sample_count=len(samples_in_cell),
            round_count=len({window.round_number for window, _ in samples_in_cell}),
            round_numbers=sorted({window.round_number for window, _ in samples_in_cell}),
            evidence=sorted(
                [
                    Evidence(
                        round_number=window.round_number,
                        tick=int(sample["tick"]),
                        kind="position_sample",
                    )
                    for window, sample in samples_in_cell
                ],
                key=lambda evidence: (evidence.round_number, evidence.tick),
            ),
        )
        for (cell_x, cell_y), samples_in_cell in grouped.items()
    ]
    return sorted(cells, key=lambda cell: (-cell.sample_count, cell.cell_x, cell.cell_y))


def trade_assessments_for_player(
    kills: pd.DataFrame, player_id: str, *, tick_interval_seconds: float | None
) -> list[TradeAssessment]:
    """Classe les morts du joueur cible selon le premier trade eligible.

    Le calcul se limite au round de la mort. Sans cadence de ticks fiable, le
    produit prefere ne produire aucune inference plutot que d'utiliser 64 Hz
    comme constante implicite.
    """
    if kills.empty or tick_interval_seconds is None or tick_interval_seconds <= 0:
        return []

    valid_kills = _valid_enemy_kills(kills).sort_values(["round_number", "tick"])
    if valid_kills.empty:
        return []

    all_round_deaths = kills[
        kills["round_number"].notna()
        & kills["tick"].notna()
        & kills["victim_id"].notna()
        & kills["victim_team"].notna()
    ].copy()
    target_deaths = valid_kills[valid_kills["victim_id"] == player_id]
    maximum_tick_delta = 5.0 / tick_interval_seconds
    assessments: list[TradeAssessment] = []

    for death in target_deaths.to_dict("records"):
        round_number = int(death["round_number"])
        death_tick = int(death["tick"])
        victim_team = int(death["victim_team"])
        killer_id = str(death["killer_id"])
        candidates = valid_kills[
            (valid_kills["round_number"] == round_number)
            & (valid_kills["tick"] > death_tick)
            & (valid_kills["tick"] <= death_tick + maximum_tick_delta)
            & (valid_kills["victim_id"] == killer_id)
            & (valid_kills["killer_team"] == victim_team)
            & (valid_kills["killer_id"] != player_id)
        ]
        trade = candidates.iloc[0] if not candidates.empty else None
        prior_deaths = all_round_deaths[
            (all_round_deaths["round_number"] == round_number)
            & (all_round_deaths["tick"] < death_tick)
            & (all_round_deaths["victim_team"] == victim_team)
        ]
        dead_teammates = set(prior_deaths["victim_id"].dropna())
        alive_teammates = max(0, 4 - len(dead_teammates))

        if trade is None:
            classification: Literal["immediate_trade", "timely_trade", "late_trade", "untraded"] = (
                "untraded"
            )
            trade_tick = None
            delay_seconds = None
        else:
            trade_tick = int(trade["tick"])
            delay_seconds = round((trade_tick - death_tick) * tick_interval_seconds, 3)
            if delay_seconds <= 1.0:
                classification = "immediate_trade"
            elif delay_seconds <= 3.0:
                classification = "timely_trade"
            else:
                classification = "late_trade"

        death_x = death.get("victim_x")
        death_y = death.get("victim_y")
        assessments.append(
            TradeAssessment(
                round_number=round_number,
                death_tick=death_tick,
                killer_id=killer_id,
                weapon=str(death.get("weapon") or "unknown"),
                classification=classification,
                trade_tick=trade_tick,
                trade_delay_seconds=delay_seconds,
                alive_teammates_before_death=alive_teammates,
                death_x=float(death_x) if death_x is not None and not pd.isna(death_x) else None,
                death_y=float(death_y) if death_y is not None and not pd.isna(death_y) else None,
            )
        )
    return assessments


def untraded_death_cells_for_player(
    kills: pd.DataFrame,
    player_id: str,
    *,
    tick_interval_seconds: float | None,
    cell_size: int = 256,
) -> list[UntradedDeathCell]:
    """Agrege les morts non tradees avec au moins deux allies vivants.

    La condition de disponibilite suppose le format competitif 5v5 et ne
    formule donc jamais une conclusion de visibilite ou de distance.
    """
    if cell_size <= 0:
        raise ValueError("cell_size must be positive")
    assessments = trade_assessments_for_player(
        kills, player_id, tick_interval_seconds=tick_interval_seconds
    )
    eligible = [
        assessment
        for assessment in assessments
        if assessment.classification == "untraded"
        and assessment.alive_teammates_before_death >= 2
        and assessment.death_x is not None
        and assessment.death_y is not None
    ]
    grouped: dict[tuple[int, int], list[TradeAssessment]] = {}
    for assessment in eligible:
        cell = (
            math.floor(assessment.death_x / cell_size),
            math.floor(assessment.death_y / cell_size),
        )
        grouped.setdefault(cell, []).append(assessment)

    cells = [
        UntradedDeathCell(
            cell_x=cell_x,
            cell_y=cell_y,
            occurrence_count=len(assessments_in_cell),
            round_count=len({assessment.round_number for assessment in assessments_in_cell}),
            round_numbers=sorted({assessment.round_number for assessment in assessments_in_cell}),
            death_ticks=sorted(assessment.death_tick for assessment in assessments_in_cell),
            evidence=sorted(
                [
                    Evidence(
                        round_number=assessment.round_number,
                        tick=assessment.death_tick,
                        kind="kill",
                    )
                    for assessment in assessments_in_cell
                ],
                key=lambda evidence: (evidence.round_number, evidence.tick),
            ),
        )
        for (cell_x, cell_y), assessments_in_cell in grouped.items()
    ]
    return sorted(cells, key=lambda cell: (-cell.occurrence_count, cell.cell_x, cell.cell_y))


def opening_kill_sample_ticks(kills: pd.DataFrame) -> list[int]:
    """Retourne les ticks où une position exacte est nécessaire pour H-02."""
    if kills.empty:
        return []
    valid = _valid_enemy_kills(kills).sort_values(["round_number", "tick"])
    return [int(kill.tick) for kill in valid.drop_duplicates(subset=["round_number"]).itertuples()]


def _opening_kill_position_lookup(
    player_samples: pd.DataFrame | None,
) -> dict[tuple[str, int], tuple[float, float]]:
    if player_samples is None or player_samples.empty:
        return {}
    required_columns = {"player_id", "tick", "x", "y"}
    missing_columns = required_columns.difference(player_samples.columns)
    if missing_columns:
        raise ValueError("player_samples is missing columns: " + ", ".join(sorted(missing_columns)))
    exact_samples = player_samples[
        player_samples["player_id"].notna()
        & player_samples["tick"].notna()
        & player_samples["x"].notna()
        & player_samples["y"].notna()
    ].drop_duplicates(subset=["player_id", "tick"], keep="last")
    return {
        (str(sample.player_id), int(sample.tick)): (float(sample.x), float(sample.y))
        for sample in exact_samples.itertuples(index=False)
    }


def opening_kills_for_player(
    kills: pd.DataFrame, player_id: str, player_samples: pd.DataFrame | None = None
) -> list[OpeningKill]:
    if kills.empty:
        return []
    valid = kills[
        kills["killer_id"].notna()
        & kills["victim_id"].notna()
        & kills["killer_team"].notna()
        & kills["victim_team"].notna()
        & (kills["killer_team"] != kills["victim_team"])
    ].sort_values(["round_number", "tick"])
    first_kills = valid.drop_duplicates(subset=["round_number"], keep="first")
    target_openings = first_kills[first_kills["killer_id"] == player_id]
    positions = _opening_kill_position_lookup(player_samples)
    return [
        OpeningKill(
            round_number=int(kill.round_number),
            tick=int(kill.tick),
            weapon=str(kill.weapon),
            killer_team=int(kill.killer_team),
            killer_x=positions.get((player_id, int(kill.tick)), (None, None))[0],
            killer_y=positions.get((player_id, int(kill.tick)), (None, None))[1],
        )
        for kill in target_openings.itertuples(index=False)
    ]


def opening_kill_cells_for_player(
    kills: pd.DataFrame,
    player_id: str,
    player_samples: pd.DataFrame | None = None,
    *,
    cell_size: int = 256,
) -> list[OpeningKillCell]:
    """Agrège H-02 seulement quand la position du tireur est exacte au tick."""
    if cell_size <= 0:
        raise ValueError("cell_size must be positive")
    openings = [
        opening
        for opening in opening_kills_for_player(kills, player_id, player_samples)
        if opening.killer_x is not None and opening.killer_y is not None
    ]
    grouped: dict[tuple[int, int], list[OpeningKill]] = {}
    for opening in openings:
        cell = (
            math.floor(opening.killer_x / cell_size),
            math.floor(opening.killer_y / cell_size),
        )
        grouped.setdefault(cell, []).append(opening)
    cells = [
        OpeningKillCell(
            cell_x=cell_x,
            cell_y=cell_y,
            occurrence_count=len(openings_in_cell),
            round_count=len({opening.round_number for opening in openings_in_cell}),
            round_numbers=sorted({opening.round_number for opening in openings_in_cell}),
            evidence=[
                Evidence(round_number=opening.round_number, tick=opening.tick, kind="kill")
                for opening in openings_in_cell
            ],
        )
        for (cell_x, cell_y), openings_in_cell in grouped.items()
    ]
    return sorted(cells, key=lambda cell: (-cell.occurrence_count, cell.cell_x, cell.cell_y))


def damage_cells_for_player(
    damages: pd.DataFrame, player_id: str, *, cell_size: int = 256
) -> list[DamageCell]:
    """Agrege les HP recus par le joueur dans une grille monde explicite.

    La position est celle de la victime exposee par ``player_hurt`` au tick du
    dommage. Ce resultat n'est pas encore un callout Mirage : le rendu devra
    indiquer qu'il s'agit d'une cellule de grille tant que l'adaptateur carte
    n'est pas disponible.
    """
    if cell_size <= 0:
        raise ValueError("cell_size must be positive")
    if damages.empty:
        return []

    required_columns = {
        "round_number",
        "tick",
        "victim_id",
        "damage_health",
        "victim_x",
        "victim_y",
    }
    missing_columns = required_columns.difference(damages.columns)
    if missing_columns:
        raise ValueError("damages is missing columns: " + ", ".join(sorted(missing_columns)))

    target_damages = damages[
        (damages["victim_id"] == player_id)
        & damages["damage_health"].notna()
        & (damages["damage_health"] > 0)
        & damages["victim_x"].notna()
        & damages["victim_y"].notna()
    ].copy()
    if target_damages.empty:
        return []

    target_damages["cell_x"] = target_damages["victim_x"].map(
        lambda coordinate: math.floor(float(coordinate) / cell_size)
    )
    target_damages["cell_y"] = target_damages["victim_y"].map(
        lambda coordinate: math.floor(float(coordinate) / cell_size)
    )

    cells = []
    for (cell_x, cell_y), cell_damages in target_damages.groupby(["cell_x", "cell_y"], sort=False):
        damage_values = cell_damages["damage_health"]
        total_damage = int(damage_values.sum())
        impact_count = len(cell_damages)
        round_numbers = sorted({int(round_number) for round_number in cell_damages["round_number"]})
        cells.append(
            DamageCell(
                cell_x=int(cell_x),
                cell_y=int(cell_y),
                total_damage=total_damage,
                impact_count=impact_count,
                round_count=len(round_numbers),
                round_numbers=round_numbers,
                average_damage_per_impact=total_damage / impact_count,
                evidence=sorted(
                    [
                        Evidence(
                            round_number=int(damage.round_number),
                            tick=int(damage.tick),
                            kind="damage",
                        )
                        for damage in cell_damages.itertuples(index=False)
                    ],
                    key=lambda evidence: (evidence.round_number, evidence.tick),
                ),
            )
        )
    return sorted(
        cells,
        key=lambda cell: (-cell.total_damage, -cell.impact_count, cell.cell_x, cell.cell_y),
    )
