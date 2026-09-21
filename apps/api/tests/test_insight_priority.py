from __future__ import annotations

from cs2_analyzer.models import Evidence, Insight
from cs2_analyzer.report import prioritize_insights


def _insight(
    identifier: str,
    rule_id: str,
    confidence: str,
    occurrences: int,
) -> Insight:
    return Insight(
        id=identifier,
        rule_id=rule_id,  # type: ignore[arg-type]
        rule_version="v0",
        title="Observation",
        observation="Fait source.",
        confidence=confidence,  # type: ignore[arg-type]
        occurrence_count=occurrences,
        evidence=[Evidence(round_number=1, tick=120, kind="kill")],
    )


def test_priorities_are_rule_aware_explainable_and_sorted() -> None:
    insights = [
        _insight("five-v-four", "H-03", "inferred", 4),
        _insight("opening-kill", "H-02", "direct", 1),
        _insight("damage", "H-04", "direct", 3),
        _insight("untraded", "H-01", "inferred", 2),
    ]

    prioritized = prioritize_insights(insights)

    assert [insight.id for insight in prioritized] == [
        "untraded",
        "damage",
        "five-v-four",
        "opening-kill",
    ]
    assert prioritized[0].priority_level == "review"
    assert prioritized[0].priority_reasons == ["impact", "repetition", "inferred_context"]
    assert prioritized[0].recommendation == (
        "Ouvrez le round source pour vérifier la séquence avant d’en tirer une conclusion."
    )
    assert prioritized[1].priority_level == "review"
    assert prioritized[1].priority_reasons == ["impact", "repetition", "direct_evidence"]
    assert prioritized[2].priority_level == "context"
    assert prioritized[3].priority_level == "context"
    assert all(0 <= insight.priority_score <= 100 for insight in prioritized)
