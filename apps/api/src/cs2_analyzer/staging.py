from __future__ import annotations

import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from .models import DemoInspection, PendingAnalysis

STAGING_TTL = timedelta(minutes=30)


class PendingAnalysisStore:
    """Conserve temporairement une demo seulement jusqu'au choix du joueur."""

    def __init__(self, root: Path) -> None:
        self.root = root / "staging"

    def create(self, source: Path, inspection: DemoInspection) -> PendingAnalysis:
        self.purge_expired()
        self.root.mkdir(parents=True, exist_ok=True)
        analysis_id = uuid4().hex
        now = datetime.now(UTC)
        pending = PendingAnalysis(
            id=analysis_id,
            created_at=now,
            expires_at=now + STAGING_TTL,
            inspection=inspection,
        )
        shutil.copyfile(source, self.demo_path(analysis_id))
        self.metadata_path(analysis_id).write_text(
            pending.model_dump_json(indent=2), encoding="utf-8"
        )
        return pending

    def get(self, analysis_id: str) -> PendingAnalysis | None:
        try:
            path = self.metadata_path(analysis_id)
        except ValueError:
            return None
        if not path.is_file():
            return None
        try:
            pending = PendingAnalysis.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        if pending.expires_at <= datetime.now(UTC):
            self.delete(analysis_id)
            return None
        return pending

    def demo_path(self, analysis_id: str) -> Path:
        return self.root / f"{self._safe_id(analysis_id)}.dem"

    def metadata_path(self, analysis_id: str) -> Path:
        return self.root / f"{self._safe_id(analysis_id)}.json"

    def delete(self, analysis_id: str) -> None:
        try:
            paths = (self.demo_path(analysis_id), self.metadata_path(analysis_id))
        except ValueError:
            return
        for path in paths:
            path.unlink(missing_ok=True)

    def purge_expired(self) -> None:
        if not self.root.is_dir():
            return
        for metadata_path in self.root.glob("*.json"):
            analysis_id = metadata_path.stem
            pending = self.get(analysis_id)
            if pending is None:
                self.delete(analysis_id)

    @staticmethod
    def _safe_id(analysis_id: str) -> str:
        if len(analysis_id) != 32 or any(
            character not in "0123456789abcdef" for character in analysis_id
        ):
            raise ValueError("Invalid analysis identifier")
        return analysis_id
