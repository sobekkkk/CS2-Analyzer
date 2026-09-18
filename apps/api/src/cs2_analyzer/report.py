from __future__ import annotations

import pandas as pd

from .models import MatchOverview, TimelineEvent
from .normalization import CanonicalMatch


def _optional_text(value: object) -> str | None:
    """Convertit les valeurs manquantes Pandas en null pour le contrat API."""
    return None if value is None or pd.isna(value) else str(value)


def _enemy_kills(kills: pd.DataFrame) -> pd.DataFrame:
    if kills.empty:
        return kills
    return kills[
        kills["killer_id"].notna()
        & kills["victim_id"].notna()
        & kills["killer_team"].notna()
        & kills["victim_team"].notna()
        & (kills["killer_team"] != kills["victim_team"])
    ]


def build_match_overview(
    match: CanonicalMatch, selected_player_id: str, match_id: str
) -> MatchOverview:
    """Produit les compteurs de base sans inferer une notion de performance."""
    participants = {participant.id: participant for participant in match.inspection.participants}
    selected_player = participants.get(selected_player_id)
    if selected_player is None:
        raise ValueError("selected player is absent from match participants")

    kills = _enemy_kills(match.kills)
    player_kills = int((kills["killer_id"] == selected_player_id).sum())
    player_deaths = int((kills["victim_id"] == selected_player_id).sum())
    damage_received = (
        0
        if match.damages.empty
        else int(
            match.damages.loc[
                (match.damages["victim_id"] == selected_player_id)
                & match.damages["damage_health"].notna()
                & (match.damages["damage_health"] > 0),
                "damage_health",
            ].sum()
        )
    )
    return MatchOverview(
        match_id=match_id,
        map_name=match.inspection.map_name,
        selected_player=selected_player,
        rounds_played=len(match.rounds),
        player_kills=player_kills,
        player_deaths=player_deaths,
        damage_received=damage_received,
    )


def timeline_for_match(
    match: CanonicalMatch, *, round_number: int | None = None
) -> list[TimelineEvent]:
    """Fusionne les faits bruts utiles a la relecture d'un round."""
    events: list[TimelineEvent] = []
    damages = match.damages
    kills = match.kills
    if round_number is not None:
        damages = damages[damages["round_number"] == round_number]
        kills = kills[kills["round_number"] == round_number]

    for damage in damages.sort_values("tick").itertuples(index=False):
        events.append(
            TimelineEvent(
                kind="damage",
                round_number=int(damage.round_number),
                tick=int(damage.tick),
                actor_id=_optional_text(damage.attacker_id),
                victim_id=_optional_text(damage.victim_id),
                weapon=str(damage.weapon),
                damage_health=int(damage.damage_health),
            )
        )
    for kill in kills.sort_values("tick").itertuples(index=False):
        events.append(
            TimelineEvent(
                kind="kill",
                round_number=int(kill.round_number),
                tick=int(kill.tick),
                actor_id=_optional_text(kill.killer_id),
                victim_id=_optional_text(kill.victim_id),
                weapon=str(kill.weapon),
            )
        )
    return sorted(events, key=lambda event: (event.tick, event.kind))
