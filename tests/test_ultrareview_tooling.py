"""Tests for the six standing findings of the tooling-subset ultrareview of pull request 4.

P1 date forms (tools/skill_evals.py), P2 input digest (tools/model_evals.py), P3 sentence
count (tools/lint.py), P4 budget-cut runs, P5 record protection and P6 the routing answer
parser (tools/model_evals.py). No test calls a model: the runs use a fake client.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import lint  # noqa: E402
import model_evals  # noqa: E402
import skill_evals  # noqa: E402

REGISTRY = skill_evals.load_refusals(ROOT)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    for part in ("plugins", "evals", "catalog", "tools"):
        shutil.copytree(ROOT / part, target / part)
    (target / "state").mkdir()
    (target / "state" / "EXECUTION-LOG.md").write_text("# log\n", encoding="utf-8")
    return target


# --------------------------------------------------------------------------- P1 date forms


def _dates_case() -> dict:
    """The source supplies 2026-12-09 and today is 2026-11-04; 2026-12-10 appears nowhere."""
    return {"id": "t-01", "kind": "happy_path", "user": "list the court dates", "today": "2026-11-04",
            "context": {"records": [{"hearing_date": "2026-12-09"}]},
            "expect": {"contains": [], "not_contains": [], "refusals": [], "client_facing": False}}


# One form per entry: (form, invented date, allowed date).
DATE_FORMS = [
    ("ISO", "2026-12-10", "2026-12-09"),
    ("Month D, YYYY", "December 10, 2026", "December 9, 2026"),
    ("abbreviated month with a period", "Dec. 10, 2026", "Dec. 9, 2026"),
    ("abbreviated month without a period", "Dec 10, 2026", "Dec 9, 2026"),
    ("D Month YYYY", "10 December 2026", "9 December 2026"),
    ("numeric M/D/YYYY", "12/10/2026", "12/9/2026"),
    ("numeric M/D/YY", "12/10/26", "12/9/26"),
    ("month and day with no year", "December 10", "December 9"),
]


def _date_failures(text: str) -> list[str]:
    failures = skill_evals.score_response(_dates_case(), text, [], REGISTRY, "dates")
    return [f for f in failures if "invented date" in f]


@pytest.mark.parametrize("form,invented,allowed", DATE_FORMS, ids=[f[0] for f in DATE_FORMS])
def test_p1_invented_date_is_caught_in_every_form(form: str, invented: str, allowed: str) -> None:
    assert _date_failures(f"Hearing on {invented}. Not retrieved: none."), form


@pytest.mark.parametrize("form,invented,allowed", DATE_FORMS, ids=[f[0] for f in DATE_FORMS])
def test_p1_allowed_date_is_accepted_in_every_form(form: str, invented: str, allowed: str) -> None:
    assert not _date_failures(f"Hearing on {allowed}. Not retrieved: none."), form


# --------------------------------------------------------------------------- P2 input digest


def test_p2_digest_covers_every_imported_scoring_module() -> None:
    files = model_evals.input_files(ROOT)
    for module in ("model_evals", "skill_evals", "routing_check", "lint", "manifest_lib"):
        assert f"tools/{module}.py" in files, module


def test_p2_a_change_to_lint_changes_the_digest(repo: Path) -> None:
    before = model_evals.input_digest(repo)
    path = repo / "tools" / "lint.py"
    path.write_text(path.read_text(encoding="utf-8") + "\n# A change to a register rule.\n", encoding="utf-8")
    assert model_evals.input_digest(repo) != before


def test_p2_digest_follows_a_new_import(repo: Path) -> None:
    """The module list is derived from the imports: a new scorer module enters the digest unlisted."""
    (repo / "tools" / "extra_rule.py").write_text("RULE = 1\n", encoding="utf-8")
    path = repo / "tools" / "skill_evals.py"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("import lint  # noqa: E402\n",
                                 "import lint  # noqa: E402\nimport extra_rule  # noqa: E402,F401\n", 1),
                    encoding="utf-8")
    assert "tools/extra_rule.py" in model_evals.input_files(repo)
