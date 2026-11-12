"""Tests of tools/release-gate.sh (Design v2.1 Section 12; Prompts v2.0 Prompt 12 step 4).

The checks the gate runs have their own tests (lint, evals, license gate). These tests pin the
gate itself: it names every item, a missing service checkout is a failure and not a skip, the
model eval release check is not narrowed to the deterministic suites, and unknown arguments are
refused.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "tools" / "release-gate.sh"
TEXT = GATE.read_text(encoding="utf-8")


def test_the_gate_names_every_item() -> None:
    for item in (
        "P0 committed tree",
        "P1 generated files current",
        "P2 lint",
        "P3 release lint",
        "P4 unit tests",
        "P5 pack evals",
        "P6 routing suite",
        "P7 skill evals",
        "P8 model eval release gate",
        "P9 PROVENANCE and license gate",
        "P10 firm service items",
    ):
        assert item in TEXT, item
    assert GATE.stat().st_mode & 0o111


def test_the_model_eval_release_check_is_part_of_the_gate() -> None:
    assert "tools/model_evals.py --check-release" in TEXT
    assert "tools/license_gate.py --upstream" in TEXT


def test_a_missing_service_checkout_is_a_failure() -> None:
    block = TEXT[TEXT.index("== P10") : TEXT.index("== summary")]
    assert 'mark "P10 firm service items" 1' in block
    assert "--own-only" in block


def test_the_gate_sets_pipefail_before_its_first_pipe() -> None:
    lines = TEXT.splitlines()
    first_pipe = next(i for i, ln in enumerate(lines) if "|" in ln and not ln.lstrip().startswith("#"))
    assert any("set -uo pipefail" in ln for ln in lines[:first_pipe])


def test_the_gate_refuses_an_unknown_argument() -> None:
    proc = subprocess.run(["bash", str(GATE), "--green"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert proc.returncode == 2
    assert "usage" in proc.stderr


def test_the_service_checkout_must_be_the_service_and_not_this_one() -> None:
    """Rule 9 review R9-3: a stand-in directory whose gate exits 3 is not the firm service."""
    block = TEXT[TEXT.index("== P10") : TEXT.index("== summary")]
    assert '"$SERVICE/tools/controls.py"' in block and '"$SERVICE/tools/release_gate.py"' in block
    assert 'pwd -P)" != "$(cd "$ROOT" && pwd -P)"' in block


def test_untracked_files_make_the_tree_uncommitted() -> None:
    """Rule 9 review R9-4: P0 counts untracked files, which pytest would collect."""
    block = TEXT[TEXT.index("== P0") : TEXT.index('step "P1')]
    assert "git status --porcelain | wc -l" in block and "--untracked-files=no" not in block


def test_own_only_never_reports_green() -> None:
    assert 'RELEASE GATE: PARTIAL' in TEXT
    assert TEXT.index('if [ "$MODE" = "own" ]; then echo "RELEASE GATE: PARTIAL') < TEXT.index(
        'echo "RELEASE GATE: GREEN"'
    )
