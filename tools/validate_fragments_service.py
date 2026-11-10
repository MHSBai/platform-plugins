#!/usr/bin/env python3
"""Validate every pack fragment with the Stage 3 validator in a mhsb-firm-service checkout.

The service repository is private; this script imports its ``firm_profile`` package
from a local checkout and runs, for each ``plugins/mhsb-pack-*/fragment/fragment.yaml``:

  schema   firm_profile.loader.validate_fragment_schema (fragment.schema.json, 2020-12)
  rules    firm_profile.rules.check_fragment (XR-* cross rules: tier, GA adoption,
           statutory adopter, report ownership)

A general-availability fragment held at pilot (adoption.yaml record PENDING ADOPTION)
is expected to fail XR-GA-ADOPTION and XR-STATUTORY until an attorney adoption is
recorded; those findings are reported as HELD, not as failures. Any other finding fails.

Usage:
    python tools/validate_fragments_service.py --service ../mhsb-firm-service
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
HELD_CODES = frozenset({"XR-GA-ADOPTION", "XR-STATUTORY"})
PENDING = "PENDING ADOPTION"


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--service", type=Path, required=True, help="mhsb-firm-service checkout")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    service = args.service.resolve()
    if not (service / "firm_profile" / "schemas" / "fragment.schema.json").exists():
        print(f"STOP: no Stage 3 fragment schema under {service}")
        return 2
    sys.path.insert(0, str(service))
    from firm_profile.loader import validate_fragment_schema  # type: ignore[import-not-found]
    from firm_profile.rules import check_fragment  # type: ignore[import-not-found]

    paths = sorted(args.root.glob("plugins/mhsb-pack-*/fragment/fragment.yaml"))
    failures = 0
    for path in paths:
        rel = path.relative_to(args.root)
        fragment = load_yaml(path)
        record = load_yaml(path.parent / "adoption.yaml") or {}
        pending = str(record.get("adopted_by", "")).strip() == PENDING
        schema = validate_fragment_schema(fragment)
        if not schema.ok:
            failures += 1
            for finding in schema.findings:
                print(f"  {finding.render()}")
            print(f"FAIL schema {rel}")
            continue
        rules = check_fragment(fragment, str(rel))
        held = [f for f in rules.errors if pending and f.code in HELD_CODES]
        other = [f for f in rules.findings if f not in held]
        for finding in other:
            print(f"  {finding.render()}")
        blocking = [f for f in other if f.severity == "error"]
        if blocking:
            failures += 1
            print(f"FAIL rules {rel}")
            continue
        status = f"HELD ({', '.join(sorted({f.code for f in held}))})" if held else "PASS"
        print(f"PASS schema, rules {status}: {rel}")
    print(f"fragments: {len(paths)}, schema and rule failures: {failures}")
    return 1 if failures or len(paths) != 12 else 0


if __name__ == "__main__":
    raise SystemExit(main())
