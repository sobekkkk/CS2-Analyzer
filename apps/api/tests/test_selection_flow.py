from __future__ import annotations

from pathlib import Path

from cs2_analyzer.models import DemoInspection, Participant
from cs2_analyzer.profile import LocalProfileStore
from cs2_analyzer.staging import PendingAnalysisStore


def inspection() -> DemoInspection:
    return DemoInspection(
        source_sha256="b" * 64,
        source_filename="match.dem",
        size_bytes=32,
        map_name="de_mirage",
        parser_version="0.42.0",
        tick_interval_seconds=0.015625,
        competitive_start_tick=0,
        participants=[Participant(id="player-a", display_name="Sobek")],
        rounds_observed=1,
        player_deaths_after_start=1,
        player_hurts_after_start=1,
    )


def test_pending_analysis_is_temporary_and_can_be_deleted(tmp_path: Path) -> None:
    source = tmp_path / "source.dem"
    source.write_bytes(b"PBDEMS2\x00payload")
    pending = PendingAnalysisStore(tmp_path)

    analysis = pending.create(source, inspection())

    assert pending.demo_path(analysis.id).is_file()
    assert pending.get(analysis.id).inspection.source_sha256 == "b" * 64

    pending.delete(analysis.id)

    assert not pending.demo_path(analysis.id).exists()
    assert pending.get(analysis.id) is None


def test_profile_suggests_the_player_only_when_present(tmp_path: Path) -> None:
    profile = LocalProfileStore(tmp_path)
    profile.remember("player-a")

    assert profile.suggestion(inspection().participants) == "player-a"
    assert profile.suggestion([Participant(id="player-b", display_name="Other")]) is None
