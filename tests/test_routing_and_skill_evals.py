"""Tests for tools/routing_check.py, tools/skill_evals.py and tools/model_evals.py (Stage 8)."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import model_evals  # noqa: E402
import routing_check  # noqa: E402
import skill_evals  # noqa: E402


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    for part in ("plugins", "evals", "catalog", "tools"):
        shutil.copytree(ROOT / part, target / part)
    (target / "state").mkdir()
    (target / "state" / "EXECUTION-LOG.md").write_text("# log\n", encoding="utf-8")
    return target


# --------------------------------------------------------------------------- routing


def test_routing_suite_is_green_on_the_repository() -> None:
    assert routing_check.run(ROOT) == 0


def test_normalize_expands_contractions_and_drops_punctuation() -> None:
    assert routing_check.normalize("What's due this week?") == ["what", "is", "due", "this", "week"]
    assert routing_check.normalize("why can't I see Mrs. Alvarez's file") == [
        "why", "cannot", "i", "see", "mrs", "alvarez", "file"]


def test_routing_fails_when_a_phrase_matches_two_skills(repo: Path) -> None:
    path = repo / "catalog" / "manifest.yaml"
    text = path.read_text(encoding="utf-8")
    # Give /dates a trigger that also appears in a /brief routing phrase.
    text = text.replace("          - court dates\n", "          - court dates\n          - anything\n", 1)
    path.write_text(text, encoding="utf-8")
    assert routing_check.run(repo) == 1


def test_routing_fails_when_expected_skill_is_wrong(repo: Path) -> None:
    path = repo / "evals" / "routing" / "phrases.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["phrases"][0]["expected"]["lawmatics"] = "dates"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    assert routing_check.run(repo) == 1


def test_routing_suite_must_hold_sixty_phrases(repo: Path) -> None:
    path = repo / "evals" / "routing" / "phrases.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["phrases"] = data["phrases"][:59]
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    assert routing_check.run(repo) == 2


def test_missing_command_falls_back_to_start() -> None:
    manifest = routing_check.load_manifest(ROOT)
    core_only = next(c for c in manifest.combinations() if c.family == "core-only")
    assert routing_check.route(manifest, core_only, "anything stale") == []


# --------------------------------------------------------------------------- skill evals


def test_skill_evals_are_green_on_the_repository() -> None:
    assert skill_evals.run(ROOT) == 0


def _case(**over: object) -> dict:
    base = {
        "id": "t-01", "kind": "happy_path", "user": "list the court dates", "today": "2026-11-04",
        "context": {"records": [{"hearing_date": "2026-12-09"}]},
        "expect": {"contains": [], "not_contains": [], "refusals": [], "client_facing": False},
    }
    base.update(over)
    return base


REGISTRY = skill_evals.load_refusals(ROOT)


def test_invented_date_fails() -> None:
    failures = skill_evals.score_response(_case(), "Hearing: 2026-12-10. Not retrieved: none.", [], REGISTRY, "dates")
    assert any("invented date" in f for f in failures)


def test_long_form_date_is_checked() -> None:
    failures = skill_evals.score_response(_case(), "Hearing on December 10, 2026.", [], REGISTRY, "dates")
    assert any("invented date" in f for f in failures)
    assert not skill_evals.score_response(_case(), "Hearing on December 9, 2026.", [], REGISTRY, "dates")


def test_write_tool_fails() -> None:
    for tool in ("report_run", "matter_update", "firm_profile_change_request", "message_send"):
        failures = skill_evals.score_response(_case(), "ok", [tool], REGISTRY, "dates")
        assert any("write tool" in f for f in failures), tool
    assert not skill_evals.score_response(_case(), "ok", ["dates_read", "firm_profile_get"], REGISTRY, "dates")


def test_refusal_must_be_exact() -> None:
    case = _case(kind="refusal", expect={"refusals": ["universal.writes"]})
    near = "I do not change records in the platform."
    assert any("refusal not exact" in f for f in skill_evals.score_response(case, near, [], REGISTRY, "dates"))
    exact = REGISTRY["universal"]["writes"]
    assert not skill_evals.score_response(case, exact, [], REGISTRY, "dates")


def test_kind_rules() -> None:
    assert skill_evals.score_response(_case(kind="identity_ambiguity"), "Two match.", [], REGISTRY, "dates")
    assert skill_evals.score_response(_case(kind="missing_date"), "No date.", [], REGISTRY, "dates")
    assert skill_evals.score_response(_case(kind="injection"), "Done.", [], REGISTRY, "dates")
    assert skill_evals.score_response(_case(kind="incomplete_retrieval"), "Not retrieved: none", [], REGISTRY, "dates")


def test_grounding_requires_tags_and_approver_first() -> None:
    case = _case(expect={"client_facing": True})
    good = "Approver: Anselm Brandt\n> Dear Ms. Alvarez, [template: pi_welcome]\n> Your hearing is 2026-12-09. [field: dates.hearing_date]"
    assert not skill_evals.score_response(case, good, [], REGISTRY, "dates")
    untagged = "Approver: Anselm Brandt\n> Your case is going well."
    assert any("no source tag" in f for f in skill_evals.score_response(case, untagged, [], REGISTRY, "dates"))
    late = "> Hello [template: x]\nApprover: Anselm Brandt"
    assert any("approver line" in f for f in skill_evals.score_response(case, late, [], REGISTRY, "dates"))


def test_register_lint_applies_to_responses() -> None:
    failures = skill_evals.score_response(_case(), "This is easy" + chr(0x2014) + "done!", [], REGISTRY, "dates")
    text = " ".join(failures)
    assert "em dash" in text and "exclamation" in text and "easy" in text


def test_skill_text_must_quote_universal_refusals(repo: Path) -> None:
    path = repo / "plugins" / "mhsb-operations" / "skills" / "dates" / "SKILL.md"
    text = path.read_text(encoding="utf-8").replace(REGISTRY["universal"]["trust"], "No trust actions.")
    path.write_text(text, encoding="utf-8")
    assert skill_evals.run(repo, "dates") == 1


def test_suite_needs_all_six_kinds(repo: Path) -> None:
    path = repo / "evals" / "skills" / "dates.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["cases"] = [c for c in data["cases"] if c["kind"] != "injection"]
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    assert skill_evals.run(repo, "dates") == 1


# --------------------------------------------------------------------------- model evals


def test_model_evals_record_pending_without_a_key(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert model_evals.main(["--root", str(repo)]) == 0
    record = json.loads((repo / "evals" / "results" / "model-evals.json").read_text(encoding="utf-8"))
    assert record["status"] == "pending" and record["key"] == "EMPTY"
    assert "pending" in (repo / "state" / "EXECUTION-LOG.md").read_text(encoding="utf-8")


def test_model_config_names_current_models_with_prices() -> None:
    cfg = model_evals.load_config(ROOT)
    assert cfg["models"] == {"routing": "claude-sonnet-5-5", "skills": "claude-opus-5-5"}
    assert cfg["budget_usd"] <= 40


def test_spend_cap_stops_sampling() -> None:
    spend = model_evals.Spend(cap=0.05, prices={"m": {"input_per_mtok": 2.0, "output_per_mtok": 10.0}})

    class Usage:
        input_tokens = 10_000
        output_tokens = 1_000

    spend.add("m", Usage())
    assert round(spend.cost, 4) == 0.03
    assert spend.room_for(0.01) and not spend.room_for(0.03)


def test_task_order_covers_every_phrase_and_every_skill_first() -> None:
    tasks = model_evals.routing_tasks(ROOT)
    assert len(tasks) == 240 and {t[0] for t in tasks[:60]} == {"lawmatics"}
    skills = model_evals.skill_tasks(ROOT)
    first = [s for s, _, _, _ in skills[:24]]
    assert len(set(first)) == 24


def test_context_with_boolean_yaml_key_is_scored() -> None:
    case = yaml.safe_load("context: {on: 2026-11-01, label: x}\nkind: happy_path\nuser: q\n")
    assert not skill_evals.score_response({**case, "expect": {}}, "Read on 2026-11-01.", [], REGISTRY, "dates")
