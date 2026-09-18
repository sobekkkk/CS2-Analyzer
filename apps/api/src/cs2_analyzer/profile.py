from __future__ import annotations

import json
from pathlib import Path

from .models import Participant


class LocalProfileStore:
    """Un seul choix de joueur, local et pseudonymise."""

    def __init__(self, root: Path) -> None:
        self.path = root / "profile.json"

    def remember(self, participant_id: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps({"participant_id": participant_id}), encoding="utf-8")
        temporary.replace(self.path)

    def suggestion(self, participants: list[Participant]) -> str | None:
        if not self.path.is_file():
            return None
        try:
            saved_id = json.loads(self.path.read_text(encoding="utf-8")).get("participant_id")
        except (OSError, json.JSONDecodeError):
            return None
        return saved_id if any(player.id == saved_id for player in participants) else None
