from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, status

from .inspection import MAX_DEMO_SIZE_BYTES, DemoInspectionError, DemoInspector
from .models import (
    AnalysisReady,
    ErrorResponse,
    MatchOverview,
    PendingAnalysis,
    PlayerSelection,
    TimelineEvent,
)
from .normalization import DemoNormalizer
from .profile import LocalProfileStore
from .report import build_match_overview, timeline_for_match
from .rules import (
    DamageCell,
    FiveVFourCell,
    OpeningKill,
    UntradedDeathCell,
    damage_cells_for_player,
    five_v_four_cells_for_player,
    opening_kills_for_player,
    untraded_death_cells_for_player,
)
from .staging import PendingAnalysisStore
from .storage import LocalMatchStore

app = FastAPI(title="CS2 Round Analyzer", version="0.1.0")
inspector = DemoInspector()
data_root = Path(os.environ.get("CS2_ANALYZER_DATA_DIR", "data"))
pending_store = PendingAnalysisStore(data_root)
profile_store = LocalProfileStore(data_root)
normalizer = DemoNormalizer(inspector)
match_store = LocalMatchStore(data_root)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _stored_match_or_404(match_id: str):
    stored = match_store.load(match_id)
    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "match_not_found", "message": "Ce match analyse est introuvable."},
        )
    return stored


@app.get(
    "/api/v1/matches/{match_id}/overview",
    response_model=MatchOverview,
    responses={404: {"model": ErrorResponse}},
)
def match_overview(match_id: str) -> MatchOverview:
    stored = _stored_match_or_404(match_id)
    return build_match_overview(stored.match, stored.selected_player_id, stored.match_id)


@app.get(
    "/api/v1/matches/{match_id}/timeline",
    response_model=list[TimelineEvent],
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def match_timeline(
    match_id: str, round_number: int | None = Query(default=None, ge=0)
) -> list[TimelineEvent]:
    stored = _stored_match_or_404(match_id)
    return timeline_for_match(stored.match, round_number=round_number)


@app.get(
    "/api/v1/matches/{match_id}/heatmaps/damage",
    response_model=list[DamageCell],
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def damage_heatmap(
    match_id: str, cell_size: int = Query(default=256, ge=1, le=2_048)
) -> list[DamageCell]:
    stored = _stored_match_or_404(match_id)
    return damage_cells_for_player(
        stored.match.damages,
        stored.selected_player_id,
        cell_size=cell_size,
    )


@app.get(
    "/api/v1/matches/{match_id}/highlights/opening-kills",
    response_model=list[OpeningKill],
    responses={404: {"model": ErrorResponse}},
)
def opening_kill_highlights(match_id: str) -> list[OpeningKill]:
    """Expose les premiers kills du joueur, preuves H-02 par round."""
    stored = _stored_match_or_404(match_id)
    return opening_kills_for_player(stored.match.kills, stored.selected_player_id)


@app.get(
    "/api/v1/matches/{match_id}/heatmaps/untraded-deaths",
    response_model=list[UntradedDeathCell],
    responses={404: {"model": ErrorResponse}},
)
def untraded_death_heatmap(
    match_id: str, cell_size: int = Query(default=256, ge=1, le=2_048)
) -> list[UntradedDeathCell]:
    stored = _stored_match_or_404(match_id)
    return untraded_death_cells_for_player(
        stored.match.kills,
        stored.selected_player_id,
        tick_interval_seconds=stored.match.inspection.tick_interval_seconds,
        cell_size=cell_size,
    )


@app.get(
    "/api/v1/matches/{match_id}/heatmaps/five-vs-four",
    response_model=list[FiveVFourCell],
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def five_v_four_heatmap(
    match_id: str, cell_size: int = Query(default=256, ge=1, le=2_048)
) -> list[FiveVFourCell]:
    """Expose les positions d'un joueur encore vivant après le passage à 5v4."""
    stored = _stored_match_or_404(match_id)
    return five_v_four_cells_for_player(
        stored.match.kills,
        stored.match.rounds,
        stored.match.player_samples,
        stored.selected_player_id,
        tick_interval_seconds=stored.match.inspection.tick_interval_seconds,
        cell_size=cell_size,
    )


@app.post(
    "/api/v1/demos",
    response_model=PendingAnalysis,
    responses={400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}},
)
async def inspect_demo(file: UploadFile = File(...)) -> PendingAnalysis:
    filename = Path(file.filename or "demo.dem").name
    if Path(filename).suffix.casefold() != ".dem":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "unsupported_file", "message": "Le fichier doit etre une demo .dem."},
        )

    with TemporaryDirectory(prefix="cs2-round-analyzer-") as temporary_directory:
        destination = Path(temporary_directory) / filename
        total_bytes = 0
        with destination.open("wb") as target:
            while chunk := await file.read(1024 * 1024):
                total_bytes += len(chunk)
                if total_bytes > MAX_DEMO_SIZE_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail={
                            "code": "file_too_large",
                            "message": "La demo depasse la taille maximale autorisee.",
                        },
                    )
                target.write(chunk)
        try:
            inspection = inspector.inspect(destination)
            suggestion = profile_store.suggestion(inspection.participants)
            inspection = inspection.model_copy(update={"suggested_participant_id": suggestion})
            return pending_store.create(destination, inspection)
        except DemoInspectionError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": error.code, "message": error.message, "details": error.details},
            ) from error
        finally:
            await file.close()


@app.post(
    "/api/v1/analyses/{analysis_id}/player",
    response_model=AnalysisReady,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def select_player(analysis_id: str, selection: PlayerSelection) -> AnalysisReady:
    pending = pending_store.get(analysis_id)
    if pending is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "analysis_not_found",
                "message": "Cette analyse temporaire est introuvable ou expiree.",
            },
        )
    participant_ids = {participant.id for participant in pending.inspection.participants}
    if selection.participant_id not in participant_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "unknown_participant",
                "message": "Le joueur choisi ne fait pas partie de cette demo.",
            },
        )

    try:
        match = normalizer.normalize(pending_store.demo_path(analysis_id))
        destination = match_store.save(match, selection.participant_id)
        profile_store.remember(selection.participant_id)
        return AnalysisReady(id=analysis_id, match_id=destination.name)
    except DemoInspectionError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": error.code, "message": error.message, "details": error.details},
        ) from error
    finally:
        pending_store.delete(analysis_id)
