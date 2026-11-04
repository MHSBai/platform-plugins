"""Tests for tools/pack_evals.py: every case passes, and defective fragments fail their cases."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import pack_evals  # noqa: E402

GA_AND_PILOT = (
    "mhsb-pack-personal-injury",
    "mhsb-pack-business-transactional",
    "mhsb-pack-estate-probate",
    "mhsb-pack-criminal-defense",
    "mhsb-pack-civil-litigation",
    "mhsb-pack-real-estate",
)
SKILLS = ("dates", "intake-triage", "checklist", "brief")
PI = "plugins/mhsb-pack-personal-injury/fragment/fragment.yaml"


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    for part in ("plugins", "evals"):
        shutil.copytree(ROOT / part, target / part)
    return target


def results(root: Path, pack: str | None = None) -> dict[str, pack_evals.CaseResult]:
    return {r.case_id: r for r in (pack_evals.run_case(root, p) for p in pack_evals.collect(root, pack))}


def test_all_cases_pass() -> None:
    found = results(ROOT)
    failed = {cid: r.problems for cid, r in found.items() if not r.ok}
    assert not failed, failed
    assert pack_evals.main(["--root", str(ROOT)]) == 0


@pytest.mark.parametrize("pack", GA_AND_PILOT)
def test_each_ga_and_pilot_pack_has_the_four_cases(pack: str) -> None:
    import yaml

    skills = {yaml.safe_load(p.read_text(encoding="utf-8"))["skill"] for p in pack_evals.collect(ROOT, pack)}
    assert set(SKILLS) <= skills


def test_dates_case_fails_when_statutory_category_turns_firm_set(repo: Path) -> None:
    path = repo / PI
    text = path.read_text(encoding="utf-8")
    marker = "- id: government_notice_of_claim\n  name: \"Government notice-of-claim window\"\n  kind: statutory"
    assert marker in text
    path.write_text(text.replace(marker, marker.replace("statutory", "firm_set")), encoding="utf-8")
    assert not results(repo)["pi-dates-01"].ok


def test_triage_case_fails_when_sensitive_field_reaches_scoring(repo: Path) -> None:
    path = repo / PI
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        'prompt: "Injuries and treatment to date, in the person\'s words", answer_type: text, required: false, '
        "sensitive_tag: health}",
        'prompt: "Injuries and treatment to date, in the person\'s words", answer_type: text, required: true, '
        "sensitive_tag: null}")
    text = text.replace("- {field: intake.injuries_treatment, tag: health, excluded_from_scoring: true}\n", "")
    path.write_text(text, encoding="utf-8")
    problems = results(repo)["pi-intake-triage-01"].problems
    assert any("scoring_inputs" in p or "changed the score" in p for p in problems), problems


def test_triage_case_fails_when_flag_is_removed(repo: Path) -> None:
    path = repo / PI
    path.write_text(path.read_text(encoding="utf-8").replace("- conflict_match\n", ""), encoding="utf-8")
    assert not results(repo)["pi-intake-triage-01"].ok


def test_brief_case_refuses_undeclared_view(repo: Path) -> None:
    path = repo / PI
    path.write_text(path.read_text(encoding="utf-8").replace(
        '- {id: incident_aging, name: "Incident aging"}\n', ""), encoding="utf-8")
    assert not results(repo)["pi-brief-01"].ok


def test_outreach_refused_without_verified_rule(repo: Path) -> None:
    path = repo / "plugins/mhsb-pack-family-law/fragment/fragment.yaml"
    text = path.read_text(encoding="utf-8")
    assert "- {id: verified_contact_rule," in text
    path.write_text(text.replace("- {id: verified_contact_rule,", "- {id: unverified_note,"), encoding="utf-8")
    found = results(repo, "mhsb-pack-family-law")
    assert not found["fam-outreach-03"].ok
    gate = pack_evals.eval_outreach(pack_evals._load(path), {"channel": "sms", "record": {}})
    assert gate["draft"] == "refused"


def test_dates_refuses_without_mapping() -> None:
    fragment = pack_evals._load(ROOT / PI)
    assert "refused" in pack_evals.eval_dates(fragment, {"mapping": {}})


def test_triage_never_declines_and_rejects_undeclared_signal() -> None:
    fragment = pack_evals._load(ROOT / PI)
    out = pack_evals.eval_intake_triage(fragment, {"answers": {}})
    assert out["decline"] is False and out["action"] == "request_missing_information"
    with pytest.raises(pack_evals.EvalError):
        pack_evals.eval_intake_triage(fragment, {"signals": {"attorney_signals": ["eligibility_question"]}})
