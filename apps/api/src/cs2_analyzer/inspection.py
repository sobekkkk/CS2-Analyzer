from __future__ import annotations

from collections.abc import Iterable
from hashlib import sha256
from pathlib import Path

import pandas as pd
from demoparser2 import DemoParser

from .models import DemoInspection, Participant

DEMO_MAGIC = b"PBDEMS2\x00"
SUPPORTED_MAP = "de_mirage"
MAX_DEMO_SIZE_BYTES = 1_500_000_000
PARSER_VERSION = "0.42.0"


class DemoInspectionError(Exception):
    def __init__(self, code: str, message: str, **details: str) -> None:
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def participant_id(steam_id: object) -> str:
    """Derive un identifiant local sans rendre le SteamID dans l'API."""
    return sha256(f"cs2-round-analyzer:{steam_id}".encode()).hexdigest()[:20]


def competitive_start_tick(
    deaths: pd.DataFrame,
    round_starts: pd.DataFrame,
    officially_ended: pd.DataFrame,
) -> int:
    """Ignore seulement le pre-match knife, sans supprimer le pistol round indexe 0."""
    if deaths.empty or officially_ended.empty or "weapon" not in deaths:
        return 0

    first_official_tick = int(officially_ended["tick"].min())
    initial_knives = deaths[
        (deaths["tick"] < first_official_tick) & deaths["weapon"].fillna("").str.startswith("knife")
    ]
    if initial_knives.empty:
        return 0

    last_knife_tick = int(initial_knives["tick"].max())
    post_knife_starts = round_starts[round_starts["tick"] > last_knife_tick]
    if post_knife_starts.empty:
        return 0
    return int(post_knife_starts["tick"].min())


def tick_interval_seconds(parser: DemoParser) -> float | None:
    samples = parser.parse_ticks(["game_time"], ticks=[100, 101])
    values = sorted({float(value) for value in samples["game_time"].dropna()})
    if len(values) < 2:
        return None
    interval = values[1] - values[0]
    return interval if interval > 0 else None


def unique_participants(rows: Iterable[dict[str, object]]) -> list[Participant]:
    participants: dict[str, Participant] = {}
    for row in rows:
        steam_id = row.get("steamid")
        name = str(row.get("name") or "Joueur inconnu").strip()
        if steam_id is None or pd.isna(steam_id):
            continue
        local_id = participant_id(steam_id)
        participants.setdefault(local_id, Participant(id=local_id, display_name=name))
    return sorted(participants.values(), key=lambda player: player.display_name.casefold())


class DemoInspector:
    def inspect(self, path: Path) -> DemoInspection:
        if path.suffix.casefold() != ".dem":
            raise DemoInspectionError("unsupported_file", "Le fichier doit avoir l'extension .dem.")
        if not path.is_file():
            raise DemoInspectionError("file_not_found", "La demo est introuvable.")
        size_bytes = path.stat().st_size
        if size_bytes > MAX_DEMO_SIZE_BYTES:
            raise DemoInspectionError(
                "file_too_large",
                "La demo depasse la taille maximale autorisee.",
                maximum_bytes=str(MAX_DEMO_SIZE_BYTES),
            )
        with path.open("rb") as source:
            if source.read(len(DEMO_MAGIC)) != DEMO_MAGIC:
                raise DemoInspectionError("invalid_demo", "La signature PBDEMS2 est absente.")

        try:
            parser = DemoParser(str(path))
            header = parser.parse_header()
            map_name = str(header.get("map_name") or "")
            if map_name != SUPPORTED_MAP:
                raise DemoInspectionError(
                    "unsupported_map",
                    "Cette version pilote ne prend en charge que de_mirage.",
                    map=map_name or "unknown",
                )

            deaths = parser.parse_event("player_death", other=["total_rounds_played"])
            hurts = parser.parse_event("player_hurt", other=["total_rounds_played"])
            round_starts = parser.parse_event("round_start")
            officially_ended = parser.parse_event("round_officially_ended")
            start_tick = competitive_start_tick(deaths, round_starts, officially_ended)
            filtered_deaths = deaths[deaths["tick"] >= start_tick]
            filtered_hurts = hurts[hurts["tick"] >= start_tick]
            rounds = parser.parse_event("round_end", other=["total_rounds_played"])
            rounds_observed = (
                int(rounds["total_rounds_played"].max()) + 1
                if not rounds.empty and rounds["total_rounds_played"].notna().any()
                else 0
            )
            players = unique_participants(parser.parse_player_info().to_dict("records"))
        except DemoInspectionError:
            raise
        except Exception as error:
            raise DemoInspectionError(
                "parse_failed", "La demo n'a pas pu etre lue par le parser."
            ) from error

        return DemoInspection(
            source_sha256=file_sha256(path),
            source_filename=path.name,
            size_bytes=size_bytes,
            map_name=map_name,
            parser_version=PARSER_VERSION,
            tick_interval_seconds=tick_interval_seconds(parser),
            competitive_start_tick=start_tick,
            participants=players,
            rounds_observed=rounds_observed,
            player_deaths_after_start=len(filtered_deaths),
            player_hurts_after_start=len(filtered_hurts),
        )
