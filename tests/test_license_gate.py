"""Tests for tools/license_gate.py. The baseline copy passes; each fixture breaks one condition."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))

import license_gate  # noqa: E402
from test_lint import copy_ignore  # noqa: E402

FIRST_ROW_FILE = "plugins/mhsb-operations/skills/dates/references/deadline-rules.md"


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    shutil.copytree(ROOT, target, ignore=copy_ignore)
    return target


def codes(root: Path, clones: bool = False) -> set[str]:
    failures, _, _ = license_gate.run(root, clones=clones)
    return {f.code for f in failures}


def edit_ledger(root: Path, repo_name: str, **changes: object) -> None:
    path = root / "harvest" / "LEDGER.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    for entry in data["repositories"]:
        if entry["repository"] == repo_name:
            entry.update(changes)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def test_baseline_passes(repo: Path) -> None:
    failures, repos, rows = license_gate.run(repo)
    assert [f.render() for f in failures] == []
    assert repos >= 17
    assert rows >= 32


def test_g1_missing_ledger(repo: Path) -> None:
    (repo / "harvest" / "LEDGER.yaml").unlink()
    assert "G1" in codes(repo)


def test_g1_copying_from_unlicensed_repository(repo: Path) -> None:
    edit_ledger(repo, "anthropics/skills", status="ADAPT")
    assert "G1" in codes(repo)


def test_g1_disallowed_spdx(repo: Path) -> None:
    edit_ledger(repo, "frblaw/ai-policy-templates", spdx="GPL-3.0")
    assert {"G1", "G2"} <= codes(repo)


def test_g2_row_without_ledger_entry(repo: Path) -> None:
    path = repo / "harvest" / "LEDGER.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["repositories"] = [
        e for e in data["repositories"] if e["repository"] != "anthropics/claude-for-legal"
    ]
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    assert "G2" in codes(repo)


def test_g2_row_from_benchmark_repository(repo: Path) -> None:
    edit_ledger(repo, "anthropics/claude-for-legal", status="BENCHMARK")
    assert "G2" in codes(repo)


def test_g2_commit_mismatch(repo: Path) -> None:
    edit_ledger(repo, "anthropics/claude-for-legal", commit="0" * 40)
    assert "G2" in codes(repo)


def test_g3_header_removed(repo: Path) -> None:
    path = repo / FIRST_ROW_FILE
    text = path.read_text(encoding="utf-8")
    path.write_text(text.split("-->", 1)[1], encoding="utf-8")
    assert "G3" in codes(repo)


def test_g3_header_commit_differs(repo: Path) -> None:
    path = repo / FIRST_ROW_FILE
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("commit 4a6c", "commit 5a6c", 1), encoding="utf-8")
    assert "G3" in codes(repo)


def test_g4_notice_without_row(repo: Path) -> None:
    src = repo / FIRST_ROW_FILE
    dst = src.with_name("unlisted-copy.md")
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    assert "G4" in codes(repo)


def test_g5_license_text_missing(repo: Path) -> None:
    for p in (repo / "LICENSES").glob("CC0-1.0-*"):
        p.unlink()
    assert "G5" in codes(repo)


def test_g6_clone_hash_mismatch(repo: Path) -> None:
    clone = repo / "harvest" / "anthropics_claude-for-legal" / "repo"
    clone.mkdir(parents=True)
    (clone / "LICENSE").write_text("altered\n", encoding="utf-8")
    assert "G6" in codes(repo, clones=True)
    assert "G6" not in codes(repo, clones=False)


def test_main_exit_codes(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert license_gate.main(["--root", str(repo)]) == 0
    (repo / "harvest" / "LEDGER.yaml").unlink()
    assert license_gate.main(["--root", str(repo)]) == 1
    assert "FAIL G1" in capsys.readouterr().out
