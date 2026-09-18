from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .models import DemoInspection
from .normalization import CanonicalMatch

MATCH_ID_PATTERN = re.compile(r"[a-f0-9]{16}")


@dataclass(frozen=True)
class StoredMatch:
    match_id: str
    selected_player_id: str
    match: CanonicalMatch


class LocalMatchStore:
    """Persistance locale des tables derivees ; le fichier .dem n'est jamais copie."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def save(self, match: CanonicalMatch, selected_player_id: str) -> Path:
        match_id = match.inspection.source_sha256[:16]
        destination = self.root / "matches" / match_id
        destination.mkdir(parents=True, exist_ok=True)
        metadata = match.inspection.model_dump()
        metadata["selected_player_id"] = selected_player_id
        (destination / "metadata.json").write_text(
            json.dumps(metadata, indent=2, default=str), encoding="utf-8"
        )
        match.rounds.to_parquet(destination / "rounds.parquet", index=False)
        match.kills.to_parquet(destination / "kills.parquet", index=False)
        match.damages.to_parquet(destination / "damages.parquet", index=False)
        match.player_samples.to_parquet(destination / "player_samples.parquet", index=False)
        (destination / "manifest.json").write_text(
            json.dumps(
                {
                    "format_version": 2,
                    "tables": [
                        "rounds.parquet",
                        "kills.parquet",
                        "damages.parquet",
                        "player_samples.parquet",
                    ],
                    "raw_demo_retained": False,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return destination

    def load(self, match_id: str) -> StoredMatch | None:
        """Charge uniquement un match derive, avec un identifiant non traversable."""
        if not MATCH_ID_PATTERN.fullmatch(match_id):
            return None
        destination = self.root / "matches" / match_id
        metadata_path = destination / "metadata.json"
        manifest_path = destination / "manifest.json"
        if not metadata_path.is_file() or not manifest_path.is_file():
            return None

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        selected_player_id = metadata.pop("selected_player_id", None)
        if not isinstance(selected_player_id, str):
            return None
        inspection = DemoInspection.model_validate(metadata)
        return StoredMatch(
            match_id=match_id,
            selected_player_id=selected_player_id,
            match=CanonicalMatch(
                inspection=inspection,
                rounds=pd.read_parquet(destination / "rounds.parquet"),
                kills=pd.read_parquet(destination / "kills.parquet"),
                damages=pd.read_parquet(destination / "damages.parquet"),
                player_samples=(
                    pd.read_parquet(destination / "player_samples.parquet")
                    if (destination / "player_samples.parquet").is_file()
                    else pd.DataFrame(
                        columns=["player_id", "tick", "team_num", "is_alive", "x", "y"]
                    )
                ),
            ),
        )
