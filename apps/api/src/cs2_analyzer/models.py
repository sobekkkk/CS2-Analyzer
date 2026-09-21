from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Participant(BaseModel):
    """Identite visible localement, sans SteamID brut."""

    id: str = Field(description="Identifiant local pseudonymise et stable")
    display_name: str = Field(description="Pseudo affiche dans la demo")


class DemoInspection(BaseModel):
    source_sha256: str
    source_filename: str
    size_bytes: int
    map_name: str
    parser_version: str
    tick_interval_seconds: float | None
    competitive_start_tick: int = Field(
        description="Tous les evenements anterieurs sont exclus de l'analyse."
    )
    participants: list[Participant]
    suggested_participant_id: str | None = None
    rounds_observed: int
    player_deaths_after_start: int
    player_hurts_after_start: int


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, str] = {}


class PendingAnalysis(BaseModel):
    id: str
    status: Literal["awaiting_player"] = "awaiting_player"
    created_at: datetime
    expires_at: datetime
    inspection: DemoInspection


class PlayerSelection(BaseModel):
    participant_id: str


class AnalysisReady(BaseModel):
    id: str
    status: Literal["ready"] = "ready"
    match_id: str


class MatchOverview(BaseModel):
    match_id: str
    map_name: str
    selected_player: Participant
    rounds_played: int
    player_kills: int
    player_deaths: int
    damage_received: int


class TimelineEvent(BaseModel):
    kind: Literal["damage", "kill"]
    round_number: int
    tick: int
    actor_id: str | None
    actor_name: str | None
    victim_id: str | None
    victim_name: str | None
    weapon: str
    damage_health: int | None = None
