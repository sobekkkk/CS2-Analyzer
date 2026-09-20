from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from demoparser2 import DemoParser

from .inspection import DemoInspector, participant_id
from .models import DemoInspection
from .rules import five_v_four_sample_ticks


@dataclass(frozen=True)
class CanonicalMatch:
    """Tables temporelles ne contenant aucun SteamID brut."""

    inspection: DemoInspection
    rounds: pd.DataFrame
    kills: pd.DataFrame
    damages: pd.DataFrame
    player_samples: pd.DataFrame = field(
        default_factory=lambda: pd.DataFrame(
            columns=["player_id", "tick", "team_num", "is_alive", "x", "y"]
        )
    )


def _round_number(value: object) -> int | None:
    if value is None or pd.isna(value):
        return None
    return int(value)


def _player_id(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    return participant_id(value)


def _empty(columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns)


class DemoNormalizer:
    def __init__(self, inspector: DemoInspector | None = None) -> None:
        self.inspector = inspector or DemoInspector()

    def normalize(self, path: Path) -> CanonicalMatch:
        inspection = self.inspector.inspect(path)
        parser = DemoParser(str(path))
        start_tick = inspection.competitive_start_tick
        round_ends = parser.parse_event("round_end", other=["total_rounds_played"])
        deaths = parser.parse_event(
            "player_death",
            player=["team_num", "X", "Y", "Z"],
            other=["total_rounds_played"],
        )
        hurts = parser.parse_event(
            "player_hurt",
            player=["team_num", "X", "Y", "Z"],
            other=["total_rounds_played"],
        )
        rounds = self._normalize_rounds(round_ends, start_tick)
        kills = self._normalize_kills(deaths, start_tick)
        sample_ticks = five_v_four_sample_ticks(
            kills, rounds, tick_interval_seconds=inspection.tick_interval_seconds
        )
        raw_player_samples = (
            parser.parse_ticks(["X", "Y", "is_alive", "team_num"], ticks=sample_ticks)
            if sample_ticks
            else _empty(["tick", "steamid", "team_num", "is_alive", "X", "Y"])
        )
        return CanonicalMatch(
            inspection=inspection,
            rounds=rounds,
            kills=kills,
            damages=self._normalize_damages(hurts, start_tick),
            player_samples=self._normalize_player_samples(raw_player_samples, start_tick),
        )

    @staticmethod
    def _normalize_rounds(events: pd.DataFrame, start_tick: int) -> pd.DataFrame:
        columns = ["round_number", "end_tick", "winner_side", "end_reason"]
        records = []
        for event in events[events["tick"] >= start_tick].to_dict("records"):
            round_number = _round_number(event.get("total_rounds_played"))
            if round_number is not None and round_number > 0:
                winner = event.get("winner")
                reason = event.get("reason")
                records.append(
                    {
                        "round_number": round_number - 1,
                        "end_tick": int(event["tick"]),
                        "winner_side": str(winner)
                        if winner is not None and not pd.isna(winner)
                        else None,
                        "end_reason": str(reason)
                        if reason is not None and not pd.isna(reason)
                        else "unknown",
                    }
                )
        return pd.DataFrame(records, columns=columns) if records else _empty(columns)

    @staticmethod
    def _normalize_kills(events: pd.DataFrame, start_tick: int) -> pd.DataFrame:
        columns = [
            "round_number",
            "tick",
            "killer_id",
            "victim_id",
            "killer_team",
            "victim_team",
            "weapon",
            "victim_x",
            "victim_y",
            "victim_z",
        ]
        records = []
        for event in events[events["tick"] >= start_tick].to_dict("records"):
            victim_id, round_number = (
                _player_id(event.get("user_steamid")),
                _round_number(event.get("total_rounds_played")),
            )
            if victim_id is not None and round_number is not None:
                records.append(
                    {
                        "round_number": round_number,
                        "tick": int(event["tick"]),
                        "killer_id": _player_id(event.get("attacker_steamid")),
                        "victim_id": victim_id,
                        "killer_team": int(event["attacker_team_num"])
                        if not pd.isna(event.get("attacker_team_num"))
                        else None,
                        "victim_team": int(event["user_team_num"])
                        if not pd.isna(event.get("user_team_num"))
                        else None,
                        "weapon": str(event.get("weapon") or "unknown"),
                        "victim_x": float(event["user_X"])
                        if not pd.isna(event.get("user_X"))
                        else None,
                        "victim_y": float(event["user_Y"])
                        if not pd.isna(event.get("user_Y"))
                        else None,
                        "victim_z": float(event["user_Z"])
                        if not pd.isna(event.get("user_Z"))
                        else None,
                    }
                )
        return pd.DataFrame(records, columns=columns) if records else _empty(columns)

    @staticmethod
    def _normalize_damages(events: pd.DataFrame, start_tick: int) -> pd.DataFrame:
        columns = [
            "round_number",
            "tick",
            "attacker_id",
            "victim_id",
            "attacker_team",
            "victim_team",
            "damage_health",
            "damage_armor",
            "weapon",
            "hitgroup",
            "victim_x",
            "victim_y",
            "victim_z",
        ]
        records = []
        for event in events[events["tick"] >= start_tick].to_dict("records"):
            victim_id, round_number, damage_health = (
                _player_id(event.get("user_steamid")),
                _round_number(event.get("total_rounds_played")),
                event.get("dmg_health"),
            )
            if (
                victim_id is None
                or round_number is None
                or damage_health is None
                or pd.isna(damage_health)
                or int(damage_health) <= 0
            ):
                continue
            records.append(
                {
                    "round_number": round_number,
                    "tick": int(event["tick"]),
                    "attacker_id": _player_id(event.get("attacker_steamid")),
                    "victim_id": victim_id,
                    "attacker_team": int(event["attacker_team_num"])
                    if not pd.isna(event.get("attacker_team_num"))
                    else None,
                    "victim_team": int(event["user_team_num"])
                    if not pd.isna(event.get("user_team_num"))
                    else None,
                    "damage_health": int(damage_health),
                    "damage_armor": int(event.get("dmg_armor") or 0),
                    "weapon": str(event.get("weapon") or "unknown"),
                    "hitgroup": str(event.get("hitgroup") or "unknown"),
                    "victim_x": float(event["user_X"])
                    if not pd.isna(event.get("user_X"))
                    else None,
                    "victim_y": float(event["user_Y"])
                    if not pd.isna(event.get("user_Y"))
                    else None,
                    "victim_z": float(event["user_Z"])
                    if not pd.isna(event.get("user_Z"))
                    else None,
                }
            )
        return pd.DataFrame(records, columns=columns) if records else _empty(columns)

    @staticmethod
    def _normalize_player_samples(events: pd.DataFrame, start_tick: int) -> pd.DataFrame:
        """Conserve les positions rares utiles à H-03, jamais le SteamID brut."""
        columns = ["player_id", "tick", "team_num", "is_alive", "x", "y"]
        records = []
        for event in events[events["tick"] >= start_tick].to_dict("records"):
            player_id = _player_id(event.get("steamid"))
            team_num = event.get("team_num")
            is_alive = event.get("is_alive")
            if (
                player_id is None
                or team_num is None
                or pd.isna(team_num)
                or is_alive is None
                or pd.isna(is_alive)
            ):
                continue
            records.append(
                {
                    "player_id": player_id,
                    "tick": int(event["tick"]),
                    "team_num": int(team_num),
                    "is_alive": bool(is_alive),
                    "x": float(event["X"]) if not pd.isna(event.get("X")) else None,
                    "y": float(event["Y"]) if not pd.isna(event.get("Y")) else None,
                }
            )
        return pd.DataFrame(records, columns=columns) if records else _empty(columns)
