"""Tests for the agent-scan gating in .github/workflows/ci.yml (PP1-M1).

A missing SNYK_TOKEN must never be reported as a successful scan: on a push
(main or a v* tag) the agent-scan job runs and fails with a clear message; on
a pull request the job is skipped, and the token job states the reason. The
job-level conditions are evaluated with a small translator for the operators
the workflow uses, and the gate scripts run under bash.
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


def run_script(script: str, event: str, token: str, tmp_path: Path) -> tuple[int, str, str]:
    output = tmp_path / "github_output"
    output.write_text("", encoding="utf-8")
    env = {"PATH": os.environ.get("PATH", ""), "SNYK_TOKEN": token, "GITHUB_EVENT_NAME": event,
           "GITHUB_REF": "refs/heads/main" if event == "push" else "refs/pull/1/merge",
           "GITHUB_OUTPUT": str(output)}
    proc = subprocess.run(["bash", "-e", "-c", script], env=env, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr, output.read_text(encoding="utf-8")


def test_token_job_exposes_presence_without_value() -> None:
    token_job = jobs()["agent-scan-token"]
    assert token_job["outputs"]["present"] == "${{ steps.token.outputs.present }}"
    assert token_job["env"]["SNYK_TOKEN"] == "${{ secrets.SNYK_TOKEN }}"


@pytest.mark.parametrize("event, present, runs", [
    ("pull_request", "false", False),
    ("pull_request", "true", True),
    ("push", "false", True),
    ("push", "true", True),
])
def test_agent_scan_job_condition(event: str, present: str, runs: bool) -> None:
    job = jobs()["agent-scan"]
    assert "agent-scan-token" in (job["needs"] if isinstance(job["needs"], list) else [job["needs"]])
    context = {"needs.agent-scan-token.outputs.present": present, "github.event_name": event,
               "github.event.repository.private": False}
    assert evaluate(job["if"], context) is runs


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash not installed")
def test_pull_request_without_token_states_skip_reason(tmp_path: Path) -> None:
    script = step(jobs()["agent-scan-token"], "Token presence")["run"]
    code, out, output = run_script(script, "pull_request", "", tmp_path)
    assert code == 0
    assert "present=false" in output
    assert "SNYK_TOKEN: EMPTY" in out and "::notice" in out and "skipped" in out


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash not installed")
def test_token_value_is_never_printed(tmp_path: Path) -> None:
    script = step(jobs()["agent-scan-token"], "Token presence")["run"]
    code, out, output = run_script(script, "pull_request", "sk-test-value-not-real", tmp_path)
    assert code == 0 and "present=true" in output
    assert "sk-test-value-not-real" not in out + output


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash not installed")
def test_push_without_token_fails_agent_scan_with_message(tmp_path: Path) -> None:
    script = step(jobs()["agent-scan"], "Require SNYK_TOKEN")["run"]
    code, out, _ = run_script(script, "push", "", tmp_path)
    assert code != 0
    assert "::error" in out and "SNYK_TOKEN" in out


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash not installed")
def test_push_with_token_passes_gate(tmp_path: Path) -> None:
    script = step(jobs()["agent-scan"], "Require SNYK_TOKEN")["run"]
    code, _, _ = run_script(script, "push", "x", tmp_path)
    assert code == 0


def test_scan_step_is_unconditional_inside_the_job() -> None:
    """When the job runs, the scan runs; a green agent-scan always means a scan ran."""
    scan = step(jobs()["agent-scan"], "Scan skills")
    assert "if" not in scan
