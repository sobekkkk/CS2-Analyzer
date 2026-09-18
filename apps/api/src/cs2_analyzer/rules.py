from __future__ import annotations

import math
from typing import Literal

import pandas as pd
from pydantic import BaseModel


class OpeningKill(BaseModel):
    """Preuve H-02 : premier kill ennemi d'un round par le joueur cible."""

    rule_id: str = "H-02"
    rule_version: str = "0.1"
    round_number: int
    tick: int
    weapon: str
    killer_team: int
    confidence: str = "direct"


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
        )
        for (cell_x, cell_y), assessments_in_cell in grouped.items()
    ]
    return sorted(cells, key=lambda cell: (-cell.occurrence_count, cell.cell_x, cell.cell_y))


def opening_kills_for_player(kills: pd.DataFrame, player_id: str) -> list[OpeningKill]:
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
    return [
        OpeningKill(
            round_number=int(kill.round_number),
            tick=int(kill.tick),
            weapon=str(kill.weapon),
            killer_team=int(kill.killer_team),
        )
        for kill in target_openings.itertuples(index=False)
    ]


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
            )
        )
    return sorted(
        cells,
        key=lambda cell: (-cell.total_damage, -cell.impact_count, cell.cell_x, cell.cell_y),
    )
