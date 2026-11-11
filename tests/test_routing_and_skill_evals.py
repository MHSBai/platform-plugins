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
    assert not (repo / "evals" / "results" / "model-evals.json").exists() or json.loads(
        (repo / "evals" / "results" / "model-evals.json").read_text(encoding="utf-8")).get("status") != "pending"
    record = json.loads((repo / "evals" / "results" / "model-evals-last-attempt.json").read_text(encoding="utf-8"))
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


def _passing_record(repo: Path) -> dict:
    """A record in which every routing and skill task ran and passed, on the current tree."""
    routing = [{"id": ph.pid, "set": cset, "expected": exp, "answer": exp, "passed": True}
               for cset, ph, exp in model_evals.routing_tasks(repo)]
    skills = [{"skill": skill, "id": case.get("id"), "kind": case.get("kind"), "passed": True, "failures": []}
              for skill, _, case, _ in model_evals.skill_tasks(repo)]
    return {"status": "ran", "input_digest": model_evals.input_digest(repo),
            "input_files": model_evals.input_files(repo),
            "routing": {"cases": len(routing), "passed": len(routing), "results": routing},
            "skills": {"cases": len(skills), "passed": len(skills), "results": skills}}


def test_release_gate_refuses_pending_and_partial_runs(repo: Path) -> None:
    results = repo / "evals" / "results" / "model-evals.json"
    results.parent.mkdir(parents=True, exist_ok=True)
    results.write_text(json.dumps({"status": "pending"}), encoding="utf-8")
    assert model_evals.main(["--root", str(repo), "--check-release"]) == 1
    routing_total = len(model_evals.routing_tasks(repo))
    skill_total = len(model_evals.skill_tasks(repo))
    digest = model_evals.input_digest(repo)
    partial = {"status": "ran", "input_digest": digest,
               "routing": {"cases": routing_total, "passed": routing_total},
               "skills": {"cases": 24, "passed": 24}}
    results.write_text(json.dumps(partial), encoding="utf-8")
    assert model_evals.main(["--root", str(repo), "--check-release"]) == 1
    full = _passing_record(repo)
    assert full["skills"]["cases"] == skill_total
    results.write_text(json.dumps(full), encoding="utf-8")
    assert model_evals.main(["--root", str(repo), "--check-release"]) == 0
    failing = {**full, "routing": {"cases": routing_total, "passed": routing_total - 1}}
    results.write_text(json.dumps(failing), encoding="utf-8")
    assert model_evals.main(["--root", str(repo), "--check-release"]) == 1


def test_worst_case_bounds_the_cap() -> None:
    spend = model_evals.Spend(cap=0.11, prices={"m": {"input_per_mtok": 4.0, "output_per_mtok": 20.0}})
    worst = spend.worst_case("m", prompt_chars=18_000, max_tokens=4096)
    assert round(worst, 4) == round(6000 * 4 / 1e6 + 4096 * 20 / 1e6, 4)
    assert spend.room_for(worst)
    spend.cost = 0.01
    assert not spend.room_for(worst)


def test_budget_above_cap_is_clamped(repo: Path, monkeypatch: pytest.MonkeyPatch,
                                     capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert model_evals.main(["--root", str(repo), "--budget", "100", "--no-log"]) == 0
    assert "clamped" in capsys.readouterr().out


# --------------------------------------------------------------------------- routing reads descriptions (PP4-M1)


def _add_quoted_phrase(repo: Path, plugin: str, skill: str, phrase: str) -> None:
    path = repo / "plugins" / plugin / "skills" / skill / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    end = text.index("\n---\n", 4)
    front = yaml.safe_load(text[4:end])
    marker = "Use when a user asks, for example: "
    description = " ".join(str(front["description"]).split())
    assert marker in description
    front["description"] = description.replace(marker, f'{marker}"{phrase}"; ', 1)
    head = yaml.safe_dump(front, sort_keys=False, allow_unicode=True, width=100)
    path.write_text(f"---\n{head}---\n{text[end + 5:]}", encoding="utf-8")


def test_routing_reads_the_description_not_metadata(repo: Path) -> None:
    # A phrase quoted in the /dates description that also occurs in a /brief routing
    # phrase makes routing ambiguous, although no manifest trigger changed.
    _add_quoted_phrase(repo, "mhsb-operations", "dates", "anything")
    assert routing_check.run(repo) == 1


def test_manifest_trigger_absent_from_description_fails(repo: Path) -> None:
    path = repo / "catalog" / "manifest.yaml"
    text = path.read_text(encoding="utf-8")
    text = text.replace("          - court dates\n", "          - court dates\n          - calendar rules\n", 1)
    path.write_text(text, encoding="utf-8")
    manifest = routing_check.load_manifest(repo)
    missing = routing_check.missing_triggers(manifest, routing_check.description_phrases(repo, manifest))
    assert missing == ["MISSING mhsb-operations:dates trigger 'calendar rules' is not quoted in the description"]
    assert routing_check.run(repo) == 1


def test_every_manifest_trigger_is_quoted_in_its_description() -> None:
    manifest = routing_check.load_manifest(ROOT)
    assert routing_check.missing_triggers(manifest, routing_check.description_phrases(ROOT, manifest)) == []


def test_release_gate_refuses_a_record_from_other_text(repo: Path) -> None:
    """PP4-N1: a record from other skill text, phrases, cases or scorers does not pass."""
    results = repo / "evals" / "results" / "model-evals.json"
    results.parent.mkdir(parents=True, exist_ok=True)
    record = _passing_record(repo)
    results.write_text(json.dumps(record), encoding="utf-8")
    assert model_evals.main(["--root", str(repo), "--check-release"]) == 0
    skill = repo / "plugins" / "mhsb-operations" / "skills" / "dates" / "SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") + "\nChanged.\n", encoding="utf-8")
    problems = model_evals.release_problems(repo)
    assert len(problems) == 1 and "plugins/mhsb-operations/skills/dates/SKILL.md" in problems[0]
    del record["input_digest"]
    results.write_text(json.dumps(record), encoding="utf-8")
    assert model_evals.main(["--root", str(repo), "--check-release"]) == 1


@pytest.mark.parametrize("path", ["tools/skill_evals.py", "evals/routing/phrases.yaml",
                                  "evals/skills/refusals.yaml"])
def test_digest_covers_scorers_phrases_and_refusals(repo: Path, path: str) -> None:
    before = model_evals.input_digest(repo)
    target = repo / path
    target.write_text(target.read_text(encoding="utf-8") + "\n# changed\n", encoding="utf-8")
    assert model_evals.input_digest(repo) != before


def test_digest_ignores_version_labels(repo: Path) -> None:
    before = model_evals.input_digest(repo)
    path = repo / "catalog" / "manifest.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["defaults"]["version"] = "9.9.9"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    assert model_evals.input_digest(repo) == before


def test_release_gate_blocks_a_ga_plugin_with_a_failed_case(repo: Path) -> None:
    """PP4-N3: --check-release names a ga plugin whose latest record fails."""
    results = repo / "evals" / "results" / "model-evals.json"
    results.parent.mkdir(parents=True, exist_ok=True)
    record = _passing_record(repo)
    row = next(r for r in record["skills"]["results"] if r["skill"] == "follow-up")
    row["passed"] = False
    results.write_text(json.dumps(record), encoding="utf-8")
    problems = model_evals.release_problems(repo)
    assert any(p.startswith("mhsb-firm-core is tier ga") and row["id"] in p for p in problems)
    assert model_evals.main(["--root", str(repo), "--check-release"]) == 1


def test_failed_case_keeps_its_transcript(repo: Path) -> None:
    class Block:
        def __init__(self, text: str) -> None:
            self.type, self.text = "text", text

    class Message:
        def __init__(self, text: str) -> None:
            self.content = [Block(text)]
            self.usage = type("U", (), {"input_tokens": 10, "output_tokens": 10})()

    class Client:
        class messages:  # noqa: N801
            @staticmethod
            def create(**_: object) -> Message:
                return Message("Draft ready.")

    cfg = model_evals.load_config(repo)
    spend = model_evals.Spend(cap=0.5, prices=cfg["prices"])
    result = model_evals.run_skills(Client(), repo, cfg, spend)
    assert result["cases"] >= 1
    failed = [r for r in result["results"] if not r["passed"]]
    assert failed and all(r["response"] == "Draft ready." for r in failed)
    assert all("response" not in r for r in result["results"] if r["passed"])


def test_l06_grades_descriptions_without_the_trigger_sentence() -> None:
    import lint

    long_promise = ("Comprehensive multidimensional organizational documentation, encompassing "
                    "interdisciplinary administrative responsibilities, institutional accountability "
                    "considerations and jurisdictional verification requirements.")
    assert lint.description_promise(long_promise + ' Use when a user asks, for example: "x".') == long_promise
    assert lint.flesch_kincaid_grade(long_promise) > 12
    assert lint.flesch_kincaid_grade("Lists the dates. It shows the owner.") < 9


@pytest.mark.parametrize("text", [
    "Hearing on Dec. 10, 2026.", "Hearing on 10 December 2026.", "Hearing on 12/10/2026.",
    "Hearing on December 10th.", "Hearing on Dec 10.",
])
def test_other_date_forms_are_checked(text: str) -> None:
    failures = skill_evals.score_response(_case(), text, [], REGISTRY, "dates")
    assert any("invented date" in f for f in failures), text


@pytest.mark.parametrize("text", ["Hearing on Dec. 9, 2026.", "Hearing on 12/9/2026.", "Hearing on December 9."])
def test_supported_date_forms_pass(text: str) -> None:
    assert not skill_evals.score_response(_case(), text, [], REGISTRY, "dates")


def test_digest_covers_the_modules_the_scorers_import() -> None:
    files = model_evals.input_files(ROOT)
    assert "tools/lint.py" in files and "tools/manifest_lib.py" in files


def test_complete_record_is_not_overwritten_by_a_pending_run(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    results = repo / "evals" / "results" / "model-evals.json"
    results.parent.mkdir(parents=True, exist_ok=True)
    results.write_text(json.dumps({"status": "ran", "marker": 1}), encoding="utf-8")
    assert model_evals.main(["--root", str(repo), "--no-log"]) == 0
    assert json.loads(results.read_text(encoding="utf-8"))["marker"] == 1


@pytest.mark.parametrize("reply,expected", [
    ("start.", "start"), ("`dates`", "dates"), ("/brief", "brief"), ("The skill is dates,", "dates"),
])
def test_routing_answer_parser(reply: str, expected: str) -> None:
    assert model_evals.parse_routing_answer(reply, {"start", "dates", "brief"}) == expected


def test_prose_lines_ending_in_colon_are_sentences() -> None:
    import lint

    assert lint.prose_for_reading("First line:\nSecond line;") == "First line:. Second line;."
