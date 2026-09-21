from __future__ import annotations

import pandas as pd

from .models import Evidence, Insight, MatchOverview, TimelineEvent
from .normalization import CanonicalMatch
from .rules import (
    damage_cells_for_player,
    five_v_four_cells_for_player,
    opening_kills_for_player,
    untraded_death_cells_for_player,
)


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
    participant_names = {
        participant.id: participant.display_name for participant in match.inspection.participants
    }
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
                actor_name=participant_names.get(_optional_text(damage.attacker_id)),
                victim_id=_optional_text(damage.victim_id),
                victim_name=participant_names.get(_optional_text(damage.victim_id)),
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
                actor_name=participant_names.get(_optional_text(kill.killer_id)),
                victim_id=_optional_text(kill.victim_id),
                victim_name=participant_names.get(_optional_text(kill.victim_id)),
                weapon=str(kill.weapon),
            )
        )
    return sorted(events, key=lambda event: (event.tick, event.kind))


def prioritize_insights(insights: list[Insight]) -> list[Insight]:
    """Ordonne les observations sans produire de score de joueur.

    Le score est un signal d'ordre de lecture, fondé sur la règle, la répétition
    et le niveau de preuve. Il reste attaché à des recommandations de relecture
    pour éviter de présenter une causalité ou une "mauvaise décision" inférée.
    """
    policy = {
        "H-01": {
            "base_score": 70,
            "level": "review",
            "impact": True,
            "recommendation": (
                "Ouvrez le round source pour vérifier la séquence avant d’en tirer une conclusion."
            ),
        },
        "H-02": {
            "base_score": 20,
            "level": "context",
            "impact": False,
            "recommendation": "Relisez le premier duel dans le round source.",
        },
        "H-03": {
            "base_score": 24,
            "level": "context",
            "impact": False,
            "recommendation": "Comparez ce placement à la suite du round source.",
        },
        "H-04": {
            "base_score": 55,
            "level": "review",
            "impact": True,
            "recommendation": (
                "Relisez le round source avant d’en déduire une habitude de positionnement."
            ),
        },
    }

    prioritized: list[Insight] = []
    for insight in insights:
        rule_policy = policy[insight.rule_id]
        reasons: list[str] = []
        if rule_policy["impact"]:
            reasons.append("impact")
        if insight.occurrence_count > 1:
            reasons.append("repetition")
        reasons.append("direct_evidence" if insight.confidence == "direct" else "inferred_context")
        score = min(100, rule_policy["base_score"] + min(insight.occurrence_count, 3) * 5)
        if insight.confidence == "direct":
            score = min(100, score + 3)
        prioritized.append(
            insight.model_copy(
                update={
                    "priority_score": score,
                    "priority_level": rule_policy["level"],
                    "priority_reasons": reasons,
                    "recommendation": rule_policy["recommendation"],
                }
            )
        )
    return sorted(prioritized, key=lambda insight: (-insight.priority_score, insight.id))


def insights_for_match(match: CanonicalMatch, selected_player_id: str) -> list[Insight]:
    """Assemble et priorise des signaux sourcés, sans jugement de joueur."""
    insights: list[Insight] = []
    for cell in untraded_death_cells_for_player(
        match.kills,
        selected_player_id,
        tick_interval_seconds=match.inspection.tick_interval_seconds,
    ):
        count = cell.occurrence_count
        insights.append(
            Insight(
                id=f"H-01:{cell.cell_x}:{cell.cell_y}",
                rule_id="H-01",
                rule_version=cell.rule_version,
                title="Morts sans trade observées",
                observation=(
                    f"{count} mort{'s' if count > 1 else ''} non suivie"
                    f"{'s' if count > 1 else ''} d’un trade dans cette zone de grille."
                ),
                confidence="inferred",
                occurrence_count=count,
                evidence=cell.evidence,
            )
        )

    for opening_kill in opening_kills_for_player(match.kills, selected_player_id):
        round_display = opening_kill.round_number + 1
        insights.append(
            Insight(
                id=f"H-02:{opening_kill.round_number}:{opening_kill.tick}",
                rule_id="H-02",
                rule_version=opening_kill.rule_version,
                title="Premier kill du round",
                observation=f"Vous obtenez le premier kill adverse du round {round_display}.",
                confidence="direct",
                occurrence_count=1,
                evidence=[
                    Evidence(
                        round_number=opening_kill.round_number,
                        tick=opening_kill.tick,
                        kind="kill",
                    )
                ],
            )
        )

    for cell in five_v_four_cells_for_player(
        match.kills,
        match.rounds,
        match.player_samples,
        selected_player_id,
        tick_interval_seconds=match.inspection.tick_interval_seconds,
    ):
        count = cell.sample_count
        insights.append(
            Insight(
                id=f"H-03:{cell.cell_x}:{cell.cell_y}",
                rule_id="H-03",
                rule_version=cell.rule_version,
                title="Position après un avantage 5v4",
                observation=(
                    f"{count} position{'s' if count > 1 else ''} relevée"
                    f"{'s' if count > 1 else ''} dans cette zone après un avantage 5v4."
                ),
                confidence="inferred",
                occurrence_count=count,
                evidence=cell.evidence,
            )
        )

    for cell in damage_cells_for_player(match.damages, selected_player_id):
        impacts = cell.impact_count
        insights.append(
            Insight(
                id=f"H-04:{cell.cell_x}:{cell.cell_y}",
                rule_id="H-04",
                rule_version=cell.rule_version,
                title="HP perdus dans cette zone",
                observation=(
                    f"{cell.total_damage} HP reçus sur {impacts} impact"
                    f"{'s' if impacts > 1 else ''} dans cette zone de grille."
                ),
                confidence="direct",
                occurrence_count=impacts,
                evidence=cell.evidence,
            )
        )

    return prioritize_insights(insights)
