"""Tests for the CI gates in .github/workflows/ci.yml (PP1-M1, PP1-N2, PP1-N3).

agent-scan: a missing SNYK_TOKEN must never be reported as a successful scan.
The job always runs; it concludes success only when the scan step succeeded,
and fails with the reason when no scan ran: a fork pull request (GitHub passes
no secrets to it), a pull request or a push without the token. A skipped job
counts as success for a required check, so the job is never skipped.

release-gate: lint --release runs on every pull request and every push to
main, not on tags alone, because main is the only installable ref.

Conditions are evaluated with a small translator for the operators the
workflow uses, and the gate scripts run under bash.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def jobs() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]


def evaluate(expression: str, context: dict[str, object]) -> bool:
    """Evaluate a GitHub Actions condition limited to ==, !=, ||, && and literals."""
    expr = expression.strip()
    if expr.startswith("${{") and expr.endswith("}}"):
        expr = expr[3:-2]
    for name in sorted(context, key=len, reverse=True):
        expr = expr.replace(name, repr(context[name]))
    expr = expr.replace("||", " or ").replace("&&", " and ")
    expr = re.sub(r"\bfalse\b", "False", re.sub(r"\btrue\b", "True", expr))
    if re.search(r"[A-Za-z_][A-Za-z_.-]*\.[A-Za-z_]", expr.replace("'", "").replace('"', "")):
        raise AssertionError(f"unresolved context in condition: {expression}")
    return bool(eval(expr, {"__builtins__": {}}, {}))  # noqa: S307 (test-only, fixed input)


def step(job: dict, name: str) -> dict:
    return next(s for s in job["steps"] if s.get("name") == name)


def run_script(script: str, event: str, token: str, tmp_path: Path,
               extra: dict[str, str] | None = None) -> tuple[int, str, str]:
    output = tmp_path / "github_output"
    output.write_text("", encoding="utf-8")
    env = {"PATH": os.environ.get("PATH", ""), "SNYK_TOKEN": token, "GITHUB_EVENT_NAME": event,
           "GITHUB_REF": "refs/heads/main" if event == "push" else "refs/pull/1/merge",
           "GITHUB_OUTPUT": str(output), **(extra or {})}
    proc = subprocess.run(["bash", "-e", "-c", script], env=env, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr, output.read_text(encoding="utf-8")


def workflow() -> dict:
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    return data.get("on", data.get(True))


def test_agent_scan_always_runs() -> None:
    """No job-level condition and no dependency that can be skipped (PP1-N3)."""
    job = jobs()["agent-scan"]
    assert "if" not in job and "needs" not in job
    assert "agent-scan-token" not in jobs()


def test_token_step_exposes_presence_without_value(tmp_path: Path) -> None:
    job = jobs()["agent-scan"]
    assert job["env"]["SNYK_TOKEN"] == "${{ secrets.SNYK_TOKEN }}"
    script = step(job, "Token presence")["run"]
    code, out, output = run_script(script, "pull_request", "sk-test-value-not-real", tmp_path)
    assert code == 0 and "present=true" in output and "SNYK_TOKEN: SET" in out
    assert "sk-test-value-not-real" not in out + output
    code, out, output = run_script(script, "pull_request", "", tmp_path)
    assert code == 0 and "present=false" in output and "SNYK_TOKEN: EMPTY" in out


def test_scan_runs_whenever_the_token_is_present() -> None:
    scan = step(jobs()["agent-scan"], "Scan skills")
    assert scan["id"] == "scan"
    assert evaluate(scan["if"], {"steps.token.outputs.present": "true"}) is True
    assert evaluate(scan["if"], {"steps.token.outputs.present": "false"}) is False


@pytest.mark.parametrize("event, head, fork", [
    ("pull_request", "someone/platform-plugins", True),
    ("pull_request", "MHSBai/platform-plugins", False),
    ("push", None, False),
])
def test_fork_expression(event: str, head: str | None, fork: bool) -> None:
    expr = step(jobs()["agent-scan"], "Require a completed scan")["env"]["FORK"]
    context = {"github.event_name": event, "github.repository": "MHSBai/platform-plugins",
               "github.event.pull_request.head.repo.full_name": head}
    assert evaluate(expr, context) is fork


def gate(outcome: str, event: str, fork: str, tmp_path: Path) -> tuple[int, str]:
    final = step(jobs()["agent-scan"], "Require a completed scan")
    assert final["if"] == "always()"
    assert final["env"]["SCAN_OUTCOME"] == "${{ steps.scan.outcome }}"
    code, out, _ = run_script(final["run"], event, "", tmp_path,
                              {"SCAN_OUTCOME": outcome, "FORK": fork})
    return code, out


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash not installed")
def test_fork_pull_request_fails_with_reason(tmp_path: Path) -> None:
    code, out = gate("skipped", "pull_request", "true", tmp_path)
    assert code != 0 and "::error" in out and "fork" in out and "No scan ran" in out


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash not installed")
def test_push_without_token_fails_with_reason(tmp_path: Path) -> None:
    code, out = gate("skipped", "push", "false", tmp_path)
    assert code != 0 and "::error" in out and "SNYK_TOKEN is not set" in out and "refs/heads/main" in out


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash not installed")
def test_repository_pull_request_without_token_fails(tmp_path: Path) -> None:
    code, out = gate("skipped", "pull_request", "false", tmp_path)
    assert code != 0 and "SNYK_TOKEN is not set" in out


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash not installed")
@pytest.mark.parametrize("outcome", ["failure", "cancelled"])
def test_failed_scan_fails(tmp_path: Path, outcome: str) -> None:
    code, out = gate(outcome, "pull_request", "false", tmp_path)
    assert code != 0 and outcome in out


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash not installed")
def test_completed_scan_passes(tmp_path: Path) -> None:
    code, _ = gate("success", "pull_request", "false", tmp_path)
    assert code == 0


def test_release_gate_runs_on_every_event() -> None:
    """lint --release on every pull request and push to main, not on tags alone (PP1-N2)."""
    triggers = workflow()
    assert "pull_request" in triggers and triggers["push"]["branches"] == ["main"]
    assert "v*" in triggers["push"]["tags"]
    job = jobs()["release-gate"]
    assert "if" not in job
    runs = [s for s in job["steps"] if "lint.py --release" in str(s.get("run", ""))]
    assert len(runs) == 1 and "if" not in runs[0]
    for name, other in jobs().items():
        for item in other["steps"]:
            if "--release" in str(item.get("run", "")):
                assert "if" not in item, f"{name}: a release step is conditional"
