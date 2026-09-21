from __future__ import annotations

import os

import pytest

from cs2_analyzer.golden import (
    load_golden_cases,
    resolve_golden_demo_paths,
    validate_golden_case,
)
from cs2_analyzer.normalization import DemoNormalizer


@pytest.mark.golden
def test_golden_v0_against_private_local_demos() -> None:
    """Opt-in : les .dem restent hors Git et ne sont jamais executes en CI."""
    if os.environ.get("CS2_ANALYZER_RUN_GOLDEN") != "1":
        pytest.skip("Corpus golden local non demande (definir CS2_ANALYZER_RUN_GOLDEN=1).")

    paths = resolve_golden_demo_paths()
    normalizer = DemoNormalizer()
    matches = {demo_id: normalizer.normalize(path) for demo_id, path in paths.items()}

    for case in load_golden_cases():
        match = matches[case.demo_id]
        validate_golden_case(
            case,
            kills=match.kills,
            damages=match.damages,
            competitive_start_tick=match.inspection.competitive_start_tick,
            tick_interval_seconds=match.inspection.tick_interval_seconds,
        )
