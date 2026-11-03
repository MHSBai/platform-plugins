#!/usr/bin/env python3
"""License gate for adapted and vendored third-party material (Design v2.1 Section 8).

Reads harvest/LEDGER.yaml and the Ledger table of PROVENANCE.md and fails when:

  G1 the ledger is malformed, or a repository is ADAPT or VENDOR without an allowed license;
  G2 a PROVENANCE row names a repository that has no ledger entry, or one that is not ADAPT
     or VENDOR, or whose commit or license differs from the ledger;
  G3 a PROVENANCE row names a file that does not exist, or whose header lacks the modification
     notice, or whose header names a different repository, commit or license;
  G4 a file under plugins/ carries a modification notice but has no PROVENANCE row;
  G5 no license text for a row's license is present in LICENSES/;
  G6 (only with --clones) a clone's LICENSE no longer matches the hash in the ledger.

Usage:
    python tools/license_gate.py [--root PATH] [--clones]
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lint import PROVENANCE_MARKERS, provenance_entries, split_frontmatter  # noqa: E402

ALLOWED = frozenset({"Apache-2.0", "MIT", "BSD-2-Clause", "BSD-3-Clause", "ISC", "CC0-1.0"})
COPYING_STATUSES = frozenset({"ADAPT", "VENDOR"})
STATUSES = COPYING_STATUSES | {"EVALUATED", "BENCHMARK", "TOOL"}
LICENSE_STATUSES = frozenset({"ALLOWED", "ABSENT", "EXCLUDED"})
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
HEADER_ORIGIN_RE = re.compile(r"Original:\s*([\w.\-]+/[\w.\-]+),.*?commit\s+([0-9a-f]{40})", re.S)
HEADER_LICENSE_RE = re.compile(r"Original license:\s*([A-Za-z0-9.\-]+)")
NOTICE_SCAN_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".py", ".txt"}
HEAD_LINES = 15


@dataclass(frozen=True)
class Failure:
    code: str
    path: str
    message: str

    def render(self) -> str:
        return f"FAIL {self.code} {self.path}: {self.message}"


def load_ledger(root: Path) -> tuple[dict[str, dict[str, Any]], list[Failure]]:
    path = root / "harvest" / "LEDGER.yaml"
    rel = "harvest/LEDGER.yaml"
    if not path.exists():
        return {}, [Failure("G1", rel, "ledger is missing")]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        return {}, [Failure("G1", rel, f"ledger does not parse: {exc}")]
    entries = data.get("repositories") if isinstance(data, dict) else None
    if not isinstance(entries, list) or not entries:
        return {}, [Failure("G1", rel, "ledger has no repositories")]
    ledger: dict[str, dict[str, Any]] = {}
    failures: list[Failure] = []
    for entry in entries:
        repo = str(entry.get("repository", "")) if isinstance(entry, dict) else ""
        where = f"{rel}:{repo or '?'}"
        if not repo or repo in ledger:
            failures.append(Failure("G1", where, "missing or duplicate repository name"))
            continue
        assert isinstance(entry, dict)
        ledger[repo] = entry
        if not SHA_RE.match(str(entry.get("commit", ""))):
            failures.append(Failure("G1", where, "commit must be a full 40-character SHA"))
        if entry.get("status") not in STATUSES:
            failures.append(Failure("G1", where, f"status must be one of {sorted(STATUSES)}"))
        lstatus = entry.get("license_status")
        if lstatus not in LICENSE_STATUSES:
            failures.append(Failure("G1", where, f"license_status must be one of {sorted(LICENSE_STATUSES)}"))
        if lstatus == "ALLOWED":
            if entry.get("spdx") not in ALLOWED:
                failures.append(Failure("G1", where, f"spdx '{entry.get('spdx')}' is not in the allowed set"))
            if not HASH_RE.match(str(entry.get("license_sha256", ""))):
                failures.append(Failure("G1", where, "license_sha256 must be a SHA-256 hex digest"))
        if entry.get("status") in COPYING_STATUSES and lstatus != "ALLOWED":
            failures.append(Failure("G1", where, "ADAPT or VENDOR requires an allowed LICENSE; "
                                                 "record the repository as BENCHMARK"))
    return ledger, failures


def header_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    _, body, err = split_frontmatter(text)
    lines = (text if err else body).lstrip("\n").splitlines()[:HEAD_LINES]
    return "\n".join(re.sub(r"^\s*#\s?", "", line) for line in lines)


def check_rows(root: Path, ledger: dict[str, dict[str, Any]]) -> tuple[list[Failure], set[str], set[str]]:
    failures: list[Failure] = []
    listed: set[str] = set()
    licenses: set[str] = set()
    for row in provenance_entries(root):
        rel = row["file"].strip("`")
        listed.add(rel)
        repo = row["source"].split(",", 1)[0].strip()
        lic = row["license"].strip()
        licenses.add(lic)
        entry = ledger.get(repo)
        if entry is None:
            failures.append(Failure("G2", rel, f"source repository '{repo}' has no ledger entry"))
        else:
            if entry.get("status") not in COPYING_STATUSES:
                failures.append(Failure("G2", rel, f"ledger status of '{repo}' is {entry.get('status')}; "
                                                   "nothing may be copied from it"))
            if row["commit"] != entry.get("commit"):
                failures.append(Failure("G2", rel, "commit differs from the ledger"))
            if lic != entry.get("spdx"):
                failures.append(Failure("G2", rel, f"license '{lic}' differs from the ledger "
                                                   f"'{entry.get('spdx')}'"))
        if lic not in ALLOWED:
            failures.append(Failure("G2", rel, f"license '{lic}' is not in the allowed set"))
        path = root / rel
        if not path.is_file():
            failures.append(Failure("G3", rel, "file does not exist"))
            continue
        head = header_text(path)
        missing = [m for m in PROVENANCE_MARKERS if m not in head]
        if missing:
            failures.append(Failure("G3", rel, f"modification notice missing: {missing}"))
            continue
        origin = HEADER_ORIGIN_RE.search(head)
        if not origin:
            failures.append(Failure("G3", rel, "header 'Original:' line lacks repository and commit"))
        elif (origin.group(1), origin.group(2)) != (repo, row["commit"]):
            failures.append(Failure("G3", rel, "header repository or commit differs from PROVENANCE.md"))
        hlic = HEADER_LICENSE_RE.search(head)
        if not hlic or hlic.group(1).rstrip(".") != lic:
            failures.append(Failure("G3", rel, "header 'Original license:' differs from PROVENANCE.md"))
    return failures, listed, licenses


def check_unlisted(root: Path, listed: set[str]) -> list[Failure]:
    failures = []
    plugins = root / "plugins"
    if not plugins.exists():
        return failures
    for path in sorted(plugins.rglob("*")):
        if not path.is_file() or path.suffix not in NOTICE_SCAN_SUFFIXES:
            continue
        rel = str(path.relative_to(root))
        if rel not in listed and PROVENANCE_MARKERS[0] in header_text(path):
            failures.append(Failure("G4", rel, "carries a modification notice but has no PROVENANCE row"))
    return failures


def check_license_texts(root: Path, licenses: set[str]) -> list[Failure]:
    present = {p.name for p in (root / "LICENSES").glob("*")} if (root / "LICENSES").exists() else set()
    return [Failure("G5", "LICENSES/", f"no license text for {lic}")
            for lic in sorted(licenses & ALLOWED) if not any(n.startswith(f"{lic}-") for n in present)]


def check_clones(root: Path, ledger: dict[str, dict[str, Any]]) -> list[Failure]:
    failures = []
    for repo, entry in ledger.items():
        lic = root / "harvest" / repo.replace("/", "_") / "repo" / "LICENSE"
        expected = entry.get("license_sha256")
        if not lic.exists():
            if expected not in (None, "null"):
                failures.append(Failure("G6", repo, "clone LICENSE not found"))
            continue
        if hashlib.sha256(lic.read_bytes()).hexdigest() != expected:
            failures.append(Failure("G6", repo, "clone LICENSE hash differs from the ledger"))
    return failures


def run(root: Path, clones: bool = False) -> tuple[list[Failure], int, int]:
    ledger, failures = load_ledger(root)
    row_failures, listed, licenses = check_rows(root, ledger)
    failures += row_failures
    failures += check_unlisted(root, listed)
    failures += check_license_texts(root, licenses)
    if clones:
        failures += check_clones(root, ledger)
    return failures, len(ledger), len(listed)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="License gate over LEDGER.yaml and PROVENANCE.md.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--clones", action="store_true",
                        help="also re-hash LICENSE files in local harvest clones")
    args = parser.parse_args(argv)
    failures, repos, rows = run(args.root.resolve(), clones=args.clones)
    for failure in failures:
        print(failure.render())
    print(f"license gate: {repos} ledger entries, {rows} PROVENANCE rows, {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
