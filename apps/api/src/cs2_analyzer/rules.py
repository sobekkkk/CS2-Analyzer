from __future__ import annotations

import math

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
