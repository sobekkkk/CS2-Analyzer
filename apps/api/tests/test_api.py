from __future__ import annotations

import pandas as pd
from fastapi.testclient import TestClient

from cs2_analyzer import main
from cs2_analyzer.models import DemoInspection, Participant
from cs2_analyzer.normalization import CanonicalMatch
from cs2_analyzer.profile import LocalProfileStore
from cs2_analyzer.staging import PendingAnalysisStore
from cs2_analyzer.storage import LocalMatchStore


def test_health() -> None:
    response = TestClient(main.app).get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rejects_non_demo_upload() -> None:
    response = TestClient(main.app).post(
        "/api/v1/demos", files={"file": ("notes.txt", b"not a demo", "text/plain")}
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "unsupported_file"


def test_rejects_malformed_analysis_identifier() -> None:
    response = TestClient(main.app).post(
        "/api/v1/analyses/not-an-analysis-id/player", json={"participant_id": "player-a"}
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "analysis_not_found"


def test_import_select_and_delete_temporary_demo(tmp_path, monkeypatch) -> None:
    inspection = DemoInspection(
        source_sha256="c" * 64,
        source_filename="sample.dem",
        size_bytes=16,
        map_name="de_mirage",
        parser_version="0.42.0",
        tick_interval_seconds=0.015625,
        competitive_start_tick=0,
        participants=[Participant(id="player-a", display_name="Sobek")],
        rounds_observed=1,
        player_deaths_after_start=1,
        player_hurts_after_start=1,
    )

    class FakeInspector:
        def inspect(self, path):
            return inspection

    class FakeNormalizer:
        def normalize(self, path):
            return CanonicalMatch(
                inspection=inspection,
                rounds=pd.DataFrame(
                    [
                        {
                            "round_number": 0,
                            "end_tick": 100,
                            "winner_side": "T",
                            "end_reason": "t_killed",
                        }
                    ]
                ),
                kills=pd.DataFrame(),
                damages=pd.DataFrame(),
            )

    monkeypatch.setattr(main, "inspector", FakeInspector())
    monkeypatch.setattr(main, "normalizer", FakeNormalizer())
    monkeypatch.setattr(main, "pending_store", PendingAnalysisStore(tmp_path))
    monkeypatch.setattr(main, "profile_store", LocalProfileStore(tmp_path))
    monkeypatch.setattr(main, "match_store", LocalMatchStore(tmp_path))
    client = TestClient(main.app)

    created = client.post(
        "/api/v1/demos",
        files={"file": ("sample.dem", b"PBDEMS2\x00demo", "application/octet-stream")},
    )
    assert created.status_code == 200
    analysis_id = created.json()["id"]

    selected = client.post(
        f"/api/v1/analyses/{analysis_id}/player", json={"participant_id": "player-a"}
    )
    assert selected.status_code == 200
    assert selected.json()["status"] == "ready"
    assert not main.pending_store.demo_path(analysis_id).exists()
    assert (tmp_path / "matches" / ("c" * 16) / "metadata.json").is_file()


def test_exposes_saved_match_overview_and_filtered_timeline(tmp_path, monkeypatch) -> None:
    inspection = DemoInspection(
        source_sha256="d" * 64,
        source_filename="sample.dem",
        size_bytes=16,
        map_name="de_mirage",
        parser_version="0.42.0",
        tick_interval_seconds=0.015625,
        competitive_start_tick=0,
        participants=[
            Participant(id="target", display_name="Sobek"),
            Participant(id="enemy", display_name="Enemy"),
        ],
        rounds_observed=2,
        player_deaths_after_start=1,
        player_hurts_after_start=1,
    )
    match = CanonicalMatch(
        inspection=inspection,
        rounds=pd.DataFrame(
            [
                {
                    "round_number": 1,
                    "end_tick": 200,
                    "winner_side": "T",
                    "end_reason": "t_killed",
                },
                {
                    "round_number": 2,
                    "end_tick": 200,
                    "winner_side": "CT",
                    "end_reason": "ct_killed",
                },
            ]
        ),
        kills=pd.DataFrame(
            [
                {
                    "round_number": 1,
                    "tick": 80,
                    "killer_id": "target",
                    "victim_id": "enemy",
                    "killer_team": 2,
                    "victim_team": 3,
                    "weapon": "ak47",
                    "victim_x": 100.0,
                    "victim_y": -100.0,
                },
                {
                    "round_number": 2,
                    "tick": 180,
                    "killer_id": "enemy",
                    "victim_id": "target",
                    "killer_team": 3,
                    "victim_team": 2,
                    "weapon": "awp",
                    "victim_x": 300.0,
                    "victim_y": -300.0,
                },
            ]
        ),
        damages=pd.DataFrame(
            [
                {
                    "round_number": 2,
                    "tick": 150,
                    "attacker_id": "enemy",
                    "victim_id": "target",
                    "damage_health": 70,
                    "weapon": "awp",
                    "victim_x": 300.0,
                    "victim_y": -300.0,
                }
            ]
        ),
        player_samples=pd.DataFrame(
            [
                {
                    "player_id": "target",
                    "tick": 80,
                    "team_num": 2,
                    "is_alive": True,
                    "x": 300.0,
                    "y": -300.0,
                },
                {
                    "player_id": "target",
                    "tick": 144,
                    "team_num": 2,
                    "is_alive": True,
                    "x": 300.0,
                    "y": -300.0,
                },
            ]
        ),
    )
    store = LocalMatchStore(tmp_path)
    store.save(match, "target")
    monkeypatch.setattr(main, "match_store", store)
    client = TestClient(main.app)

    overview = client.get(f"/api/v1/matches/{'d' * 16}/overview")
    timeline = client.get(f"/api/v1/matches/{'d' * 16}/timeline?round_number=2")
    damage_cells = client.get(f"/api/v1/matches/{'d' * 16}/heatmaps/damage?cell_size=256")
    opening_kills = client.get(f"/api/v1/matches/{'d' * 16}/highlights/opening-kills")
    opening_kill_cells = client.get(
        f"/api/v1/matches/{'d' * 16}/heatmaps/opening-kills?cell_size=256"
    )
    untraded_death_cells = client.get(
        f"/api/v1/matches/{'d' * 16}/heatmaps/untraded-deaths?cell_size=256"
    )
    five_v_four_cells = client.get(
        f"/api/v1/matches/{'d' * 16}/heatmaps/five-vs-four?cell_size=256"
    )
    insights = client.get(f"/api/v1/matches/{'d' * 16}/insights")

    assert overview.status_code == 200
    assert overview.json()["selected_player"]["display_name"] == "Sobek"
    assert overview.json()["player_deaths"] == 1
    assert timeline.status_code == 200
    assert [(event["kind"], event["tick"]) for event in timeline.json()] == [
        ("damage", 150),
        ("kill", 180),
    ]
    assert damage_cells.status_code == 200
    assert damage_cells.json()[0]["total_damage"] == 70
    assert damage_cells.json()[0]["cell_x"] == 1
    assert damage_cells.json()[0]["cell_y"] == -2
    assert opening_kills.status_code == 200
    assert opening_kills.json() == [
        {
            "rule_id": "H-02",
            "rule_version": "0.1",
            "round_number": 1,
            "tick": 80,
            "weapon": "ak47",
            "killer_team": 2,
            "killer_x": 300.0,
            "killer_y": -300.0,
            "confidence": "direct",
        }
    ]
    assert opening_kill_cells.status_code == 200
    assert opening_kill_cells.json() == [
        {
            "rule_id": "H-02",
            "rule_version": "0.1",
            "cell_x": 1,
            "cell_y": -2,
            "occurrence_count": 1,
            "round_count": 1,
            "round_numbers": [1],
            "confidence": "direct",
            "evidence": [{"round_number": 1, "tick": 80, "kind": "kill"}],
        }
    ]
    assert untraded_death_cells.status_code == 200
    assert untraded_death_cells.json()[0]["occurrence_count"] == 1
    assert untraded_death_cells.json()[0]["cell_x"] == 1
    assert untraded_death_cells.json()[0]["cell_y"] == -2
    assert five_v_four_cells.status_code == 200
    assert five_v_four_cells.json() == [
        {
            "rule_id": "H-03",
            "rule_version": "0.1",
            "cell_x": 1,
            "cell_y": -2,
            "sample_count": 1,
            "round_count": 1,
            "round_numbers": [1],
            "confidence": "inferred",
            "evidence": [
                {"round_number": 1, "tick": 144, "kind": "position_sample"},
            ],
        }
    ]
    assert insights.status_code == 200
    assert insights.json() == [
        {
            "id": "H-01:1:-2",
            "rule_id": "H-01",
            "rule_version": "0.1",
            "title": "Morts sans trade observées",
            "observation": "1 mort non suivie d’un trade dans cette zone de grille.",
            "confidence": "inferred",
            "occurrence_count": 1,
            "evidence": [
                {"round_number": 2, "tick": 180, "kind": "kill"},
            ],
            "priority_score": 75,
            "priority_level": "review",
            "priority_reasons": ["impact", "inferred_context"],
            "recommendation": (
                "Ouvrez le round source pour vérifier la séquence avant d’en tirer une conclusion."
            ),
        },
        {
            "id": "H-04:1:-2",
            "rule_id": "H-04",
            "rule_version": "0.1",
            "title": "HP perdus dans cette zone",
            "observation": "70 HP reçus sur 1 impact dans cette zone de grille.",
            "confidence": "direct",
            "occurrence_count": 1,
            "evidence": [
                {"round_number": 2, "tick": 150, "kind": "damage"},
            ],
            "priority_score": 63,
            "priority_level": "review",
            "priority_reasons": ["impact", "direct_evidence"],
            "recommendation": (
                "Relisez le round source avant d’en déduire une habitude de positionnement."
            ),
        },
        {
            "id": "H-03:1:-2",
            "rule_id": "H-03",
            "rule_version": "0.1",
            "title": "Position après un avantage 5v4",
            "observation": "1 position relevée dans cette zone après un avantage 5v4.",
            "confidence": "inferred",
            "occurrence_count": 1,
            "evidence": [
                {"round_number": 1, "tick": 144, "kind": "position_sample"},
            ],
            "priority_score": 29,
            "priority_level": "context",
            "priority_reasons": ["inferred_context"],
            "recommendation": "Comparez ce placement à la suite du round source.",
        },
        {
            "id": "H-02:1:80",
            "rule_id": "H-02",
            "rule_version": "0.1",
            "title": "Premier kill du round",
            "observation": "Vous obtenez le premier kill adverse du round 2.",
            "confidence": "direct",
            "occurrence_count": 1,
            "evidence": [
                {"round_number": 1, "tick": 80, "kind": "kill"},
            ],
            "priority_score": 28,
            "priority_level": "context",
            "priority_reasons": ["direct_evidence"],
            "recommendation": "Relisez le premier duel dans le round source.",
        },
    ]
