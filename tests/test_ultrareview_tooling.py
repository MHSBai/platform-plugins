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


# --------------------------------------------------------------------------- P3 sentence count


# Three lines of more than two words each, ending in ':', ';' and '.'.
COLON_FIXTURE = (
    "Check the open matters first:\n"
    "Confirm the owner of each date;\n"
    "Send the summary to the team.\n"
)


def _count_before_the_splitter_change(body: str) -> int:
    """The splitter before fdb496b: sentences end at . ? : ; and need one letter."""
    text = " ".join(line.strip() for line in body.splitlines() if line.strip())
    return len([s for s in re.split(r"[.?:;]+(?:\s|$)", text) if re.search(r"[A-Za-z]", s)])


def test_p3_colon_lines_count_as_sentences_on_the_fallback_path() -> None:
    prose = lint.prose_for_reading(COLON_FIXTURE)
    assert _count_before_the_splitter_change(COLON_FIXTURE) == 3
    assert lint.fk_sentence_count(prose) == 3


def test_p3_colon_lines_count_as_sentences_on_the_textstat_path() -> None:
    textstat = pytest.importorskip("textstat")
    prose = lint.prose_for_reading(COLON_FIXTURE)
    assert textstat.sentence_count(prose) == lint.fk_sentence_count(prose) == 3


# --------------------------------------------------------------------------- P4, P5 fake client


def _fake_anthropic(raise_error: bool = False) -> tuple[types.ModuleType, list[dict]]:
    """A stand-in for the anthropic package: each reply is 'start' and is charged a million input tokens."""
    module = types.ModuleType("anthropic")
    calls: list[dict] = []

    class APIStatusError(Exception):
        status_code = 529

    class APIConnectionError(Exception):
        pass

    class Usage:
        input_tokens = 1_000_000
        output_tokens = 1

    class Block:
        type = "text"
        text = "start"

    class Message:
        content = [Block()]
        usage = Usage()

    class Messages:
        def create(self, **kwargs: object) -> Message:
            calls.append(kwargs)
            if raise_error:
                raise APIStatusError("overloaded")
            return Message()

    class Anthropic:
        def __init__(self) -> None:
            self.messages = Messages()

    module.Anthropic = Anthropic
    module.APIStatusError = APIStatusError
    module.APIConnectionError = APIConnectionError
    return module, calls


def _use_fake_client(monkeypatch: pytest.MonkeyPatch, raise_error: bool = False) -> list[dict]:
    module, calls = _fake_anthropic(raise_error)
    monkeypatch.setitem(sys.modules, "anthropic", module)
    # Not a credential: the fake client never sends a request.
    monkeypatch.setenv("ANTHROPIC_API_KEY", "placeholder-for-the-fake-client")
    return calls


def _write_ran_record(repo: Path) -> Path:
    results = repo / model_evals.RESULTS
    results.parent.mkdir(parents=True, exist_ok=True)
    results.write_text(json.dumps({"status": "ran", "marker": "committed"}), encoding="utf-8")
    return results


def test_p4_budget_cut_run_is_recorded_as_truncated(repo: Path, monkeypatch: pytest.MonkeyPatch,
                                                     capsys: pytest.CaptureFixture[str]) -> None:
    calls = _use_fake_client(monkeypatch)
    # USD 1 admits the first routing request (worst case well under 1); its charged cost
    # (one million input tokens) leaves no room for a second.
    code = model_evals.main(["--root", str(repo), "--budget", "1", "--no-log"])
    out = capsys.readouterr().out
    assert len(calls) == 1
    assert code != 0
    record = json.loads((repo / model_evals.LAST_ATTEMPT).read_text(encoding="utf-8"))
    routing_total = len(model_evals.routing_tasks(repo))
    skill_total = len(model_evals.skill_tasks(repo))
    assert record["status"] == "truncated"
    assert record["truncated"] == {"routing": {"ran": 1, "total": routing_total},
                                   "skills": {"ran": 0, "total": skill_total}}
    assert "status truncated" in out
    assert f"1 of {routing_total} tasks ran" in out and f"0 of {skill_total} tasks ran" in out


def test_p4_release_gate_treats_truncated_as_not_passing(repo: Path,
                                                         capsys: pytest.CaptureFixture[str]) -> None:
    # A record complete in every other respect, marked truncated.
    routing = [{"id": ph.pid, "set": cset, "expected": exp, "answer": exp, "passed": True}
               for cset, ph, exp in model_evals.routing_tasks(repo)]
    skills = [{"skill": skill, "id": case.get("id"), "kind": case.get("kind"), "passed": True, "failures": []}
              for skill, _, case, _ in model_evals.skill_tasks(repo)]
    record = {"status": "truncated", "input_digest": model_evals.input_digest(repo),
              "input_files": model_evals.input_files(repo),
              "routing": {"cases": len(routing), "passed": len(routing), "results": routing},
              "skills": {"cases": len(skills), "passed": len(skills), "results": skills}}
    results = repo / model_evals.RESULTS
    results.parent.mkdir(parents=True, exist_ok=True)
    results.write_text(json.dumps(record), encoding="utf-8")
    assert model_evals.main(["--root", str(repo), "--check-release"]) == 1
    assert "'truncated'" in capsys.readouterr().out
    record["status"] = "ran"
    results.write_text(json.dumps(record), encoding="utf-8")
    assert model_evals.main(["--root", str(repo), "--check-release"]) == 0


def test_p5_ran_record_survives_a_pending_run(repo: Path, monkeypatch: pytest.MonkeyPatch,
                                              capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    results = _write_ran_record(repo)
    assert model_evals.main(["--root", str(repo), "--no-log"]) == 0
    assert json.loads(results.read_text(encoding="utf-8")) == {"status": "ran", "marker": "committed"}
    attempt = json.loads((repo / model_evals.LAST_ATTEMPT).read_text(encoding="utf-8"))
    assert attempt["status"] == "pending"
    assert model_evals.LAST_ATTEMPT.as_posix() in capsys.readouterr().out


def test_p5_ran_record_survives_an_error_run(repo: Path, monkeypatch: pytest.MonkeyPatch,
                                             capsys: pytest.CaptureFixture[str]) -> None:
    _use_fake_client(monkeypatch, raise_error=True)
    results = _write_ran_record(repo)
    assert model_evals.main(["--root", str(repo), "--budget", "1", "--no-log"]) == 1
    assert json.loads(results.read_text(encoding="utf-8")) == {"status": "ran", "marker": "committed"}
    assert json.loads((repo / model_evals.LAST_ATTEMPT).read_text(encoding="utf-8"))["status"] == "error"
    assert model_evals.LAST_ATTEMPT.as_posix() in capsys.readouterr().out
