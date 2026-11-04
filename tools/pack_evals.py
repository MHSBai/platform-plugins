#!/usr/bin/env python3
"""Pack evals: fragment-contract cases for /dates, /intake-triage, /checklist and /brief.

Each case in ``evals/packs/<pack>/*.yaml`` names a pack, a skill and an input, and states
the expected result. A reference evaluator below implements the parts of each skill's
promise (Design v2.1 Section 5) that the fragment drives, so that a case fails when the
fragment cannot support the promise: a statutory category without a citation placeholder,
a sensitive field that reaches scoring, a decline in place of a flag, a document list that
cannot answer readiness, a pack view the fragment does not declare. The evaluator is a
deterministic oracle over fragment data; it is not the skill and calls no model.

Usage:
    python tools/pack_evals.py [--root PATH] [--pack NAME]

Exit status 0 when every case passes, 1 when any case fails, 2 on a load error.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable

import yaml

ROOT = Path(__file__).resolve().parent.parent
CITATION_PLACEHOLDER = "CITATION PENDING"
ACTIONS = ("attorney_review", "request_missing_information", "schedule_consult")

# Signal to flag, in order of preference: the first flag the fragment declares is raised.
CONFLICT_FLAGS = ("conflict_match", "possible_conflict")
AREA_FLAGS = ("outside_service_area", "outside_jurisdiction")
DATE_FLAGS = ("possible_limitation_issue", "agency_deadline_question",
              "notice_or_claim_deadline_question", "answer_deadline_question")
PRIOR_COUNSEL_QUESTIONS = ("prior_counsel", "prior_attorneys")


class EvalError(Exception):
    """A case or fragment could not be loaded or names something that does not exist."""


Doc = dict[str, Any]


# --------------------------------------------------------------------------- evaluators


def _as_date(value: Any) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def eval_dates(fragment: Doc, given: Doc) -> Doc:
    """Dates from mapped fields only; the entered date governs; disagreements listed, never resolved."""
    mapping: dict[str, str] = given.get("mapping") or {}
    if not mapping:
        return {"refused": "date-field mapping is absent; no date is derived"}
    record: dict[str, Doc] = given.get("record") or {}
    computed: dict[str, Any] = given.get("computed") or {}
    rows: dict[str, Doc] = {}
    for cat in fragment["deadline_categories"]:
        cid = cat["id"]
        row: Doc = {"kind": cat["kind"], "entered_date_governs": cat["entered_date_governs"]}
        if cat["kind"] == "statutory":
            adopted = bool((cat.get("adopter") or {}).get("adopted_by"))
            pending = str(cat.get("citation") or "").startswith(CITATION_PLACEHOLDER)
            row["citation_status"] = "confirmed" if adopted and not pending else "pending adopter confirmation"
            row["counsel_review"] = True
        else:
            row["citation_status"] = "not applicable"
            row["counsel_review"] = False
        fieldname = mapping.get(cid)
        if fieldname is None:
            row.update(status="unmapped", governing_date=None)
            rows[cid] = row
            continue
        entry = record.get(fieldname) or {}
        entered = _as_date(entry.get("value"))
        cross = _as_date(computed.get(cid))
        row["governing_date"] = entered.isoformat() if entered else None
        row["status"] = "established" if entered else "not_established"
        if not entered:
            row["not_established"] = {"source": entry.get("source", "unknown"),
                                      "owner": entry.get("owner", "unknown")}
        row["cross_check"] = cross.isoformat() if cross else None
        row["disagreement"] = bool(entered and cross and entered != cross)
        rows[cid] = row
    statutory = [c["id"] for c in fragment["deadline_categories"] if c["kind"] == "statutory"]
    return {"rows": rows, "statutory_categories": statutory, "computed_markers": []}


def _sensitive_ids(fragment: Doc) -> set[str]:
    ids = {q["id"] for q in fragment["intake_questions"] if q["sensitive_tag"]}
    ids |= {t["field"].split(".", 1)[1] for t in fragment["sensitive_field_tags"]
            if t["field"].startswith("intake.")}
    return ids


def _answered(value: Any) -> bool:
    return value not in (None, "", [], "unknown")


def eval_intake_triage(fragment: Doc, given: Doc) -> Doc:
    """Score over required, non-sensitive questions; raise flags in place of declines."""
    answers: Doc = given.get("answers") or {}
    signals: Doc = given.get("signals") or {}
    declared = set(fragment["attorney_review_flags"])
    questions = {q["id"]: q for q in fragment["intake_questions"]}
    unknown = sorted(set(answers) - set(questions))
    if unknown:
        raise EvalError(f"answers name questions not in the fragment: {unknown}")
    sensitive = _sensitive_ids(fragment)
    scoring = sorted(qid for qid, q in questions.items() if q["required"] and qid not in sensitive)
    answered = [qid for qid in scoring if _answered(answers.get(qid))]
    score = round(len(answered) / len(scoring), 4) if scoring else 0.0

    def first(candidates: tuple[str, ...]) -> str | None:
        return next((flag for flag in candidates if flag in declared), None)

    flags: list[str] = []
    unraised: list[str] = []

    def raise_flag(flag: str | None, signal: str) -> None:
        if flag is None:
            unraised.append(signal)
        elif flag not in flags:
            flags.append(flag)

    matches = int(signals.get("conflict_name_matches", 0))
    if matches > 0:
        raise_flag(first(CONFLICT_FLAGS), "conflict_name_matches")
    if signals.get("out_of_area"):
        raise_flag(first(AREA_FLAGS), "out_of_area")
    if signals.get("dates_not_established"):
        raise_flag(first(DATE_FLAGS), "dates_not_established")
    if any(_answered(answers.get(q)) for q in PRIOR_COUNSEL_QUESTIONS) and "prior_counsel_of_record" in declared:
        raise_flag("prior_counsel_of_record", "prior_counsel")
    for flag in signals.get("attorney_signals") or []:
        if flag not in declared:
            raise EvalError(f"attorney signal '{flag}' is not a flag this fragment declares")
        raise_flag(flag, flag)
    if flags:
        action = "attorney_review"
    elif score < 1:
        action = "request_missing_information"
    else:
        action = "schedule_consult"
    return {
        "score": score,
        "scoring_inputs": scoring,
        "excluded_sensitive": sorted(sensitive & set(questions)),
        "flags": flags,
        "unraised_signals": unraised,
        "action": action,
        "decline": False,
        "conflict_record": {"name_matches": matches},
    }


def eval_checklist(fragment: Doc, given: Doc) -> Doc:
    """Documents present versus the fragment's document list."""
    present = set(given.get("documents_present") or [])
    listed = {d["id"]: d for d in fragment["document_list"]}
    return {
        "present": sorted(present & set(listed)),
        "missing_required": sorted(i for i, d in listed.items() if d["required"] and i not in present),
        "missing_optional": sorted(i for i, d in listed.items() if not d["required"] and i not in present),
        "not_in_list": sorted(present - set(listed)),
        "ready": all(i in present for i, d in listed.items() if d["required"]),
    }


def eval_brief_view(fragment: Doc, given: Doc) -> Doc:
    """One pack view: rows where the anchoring field is populated, gaps where it is not."""
    view = given["view"]
    views = {v["id"]: v for v in fragment["brief_views"]}
    if view not in views:
        return {"refused": f"view '{view}' is not declared by this pack"}
    anchor = given.get("anchor_field")
    if not anchor:
        return {"refused": f"view '{view}' has no mapped anchoring field"}
    as_of = _as_date(given.get("as_of"))
    rows: list[Doc] = []
    gaps: list[str] = []
    matters: list[Doc] = given.get("matters") or []
    for matter in matters:
        value = (matter.get("fields") or {}).get(anchor)
        if value in (None, ""):
            gaps.append(matter["id"])
            continue
        row: Doc = {"matter": matter["id"], anchor: value}
        anchor_date = None
        try:
            anchor_date = _as_date(value)
        except ValueError:
            anchor_date = None
        if anchor_date and as_of:
            row["days"] = (as_of - anchor_date).days
        rows.append(row)
    retrieved = len(rows)
    coverage = (f"coverage: {retrieved} of {len(matters)} matters retrieved for {views[view]['name']}; "
                f"{len(gaps)} not retrieved because {anchor} is empty")
    return {"view": view, "rows": rows, "data_gaps": gaps, "coverage": coverage}


def eval_outreach(fragment: Doc, given: Doc) -> Doc:
    """Outreach draft gate: refused unless a verified contact rule with verifier and date permits it."""
    flags = {f["id"]: f for f in fragment["consent_flags"]}
    rule_id = given.get("rule", "verified_contact_rule")
    if rule_id not in flags:
        return {"draft": "refused", "reason": f"fragment declares no '{rule_id}' flag"}
    spec = flags[rule_id]
    record = (given.get("record") or {}).get(rule_id)
    if not record:
        return {"draft": "refused", "reason": "contact rule unknown"}
    verifier = record.get("verified_by")
    verified_on = _as_date(record.get("verified_on"))
    if spec["verifier_required"] and (not verifier or not verified_on):
        return {"draft": "refused", "reason": "contact rule unknown: verifier or date missing"}
    as_of = _as_date(given.get("as_of"))
    if spec["expiry_days"] and verified_on and as_of and as_of > verified_on + timedelta(days=spec["expiry_days"]):
        return {"draft": "refused", "reason": "contact rule expired"}
    channel = given.get("channel")
    if channel not in (record.get("channels") or []):
        return {"draft": "refused", "reason": f"channel '{channel}' not permitted by the verified rule"}
    return {"draft": "permitted", "reason": f"verified by {verifier} on {verified_on.isoformat()}"}


EVALUATORS: dict[str, Callable[[Doc, Doc], Doc]] = {
    "dates": eval_dates,
    "intake-triage": eval_intake_triage,
    "checklist": eval_checklist,
    "brief": eval_brief_view,
    "outreach-gate": eval_outreach,
}


# --------------------------------------------------------------------------- comparison


def compare(expected: Any, actual: Any, where: str = "") -> list[str]:
    """Expected is a subset: every stated key and value must appear in the actual result."""
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [f"{where or '(root)'}: expected a mapping, got {actual!r}"]
        problems: list[str] = []
        for key, value in expected.items():
            if key not in actual:
                problems.append(f"{where}.{key}: missing")
                continue
            problems.extend(compare(value, actual[key], f"{where}.{key}"))
        return problems
    if isinstance(expected, list) and isinstance(actual, list):
        return [] if expected == actual else [f"{where}: expected {expected!r}, got {actual!r}"]
    return [] if expected == actual else [f"{where}: expected {expected!r}, got {actual!r}"]


@dataclass
class CaseResult:
    path: str
    case_id: str
    problems: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems


def _load(path: Path) -> Doc:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise EvalError(f"{path}: {exc}") from exc
    if not isinstance(data, dict):
        raise EvalError(f"{path}: not a mapping")
    return data


def run_case(root: Path, path: Path) -> CaseResult:
    case = _load(path)
    result = CaseResult(str(path.relative_to(root)), str(case.get("id", path.stem)))
    fragment_path = root / "plugins" / case["pack"] / "fragment" / "fragment.yaml"
    fragment = _load(fragment_path)
    skill = case["skill"]
    if skill not in EVALUATORS:
        result.problems.append(f"unknown skill '{skill}'")
        return result
    evaluator = EVALUATORS[skill]
    try:
        actual = evaluator(fragment, case["input"])
    except (EvalError, KeyError, ValueError) as exc:
        result.problems.append(f"evaluator error: {exc}")
        return result
    result.problems.extend(compare(case["expect"], actual))
    if skill == "intake-triage":
        for problem in _triage_invariants(fragment, case, actual, evaluator):
            result.problems.append(problem)
    return result


def _triage_invariants(fragment: Doc, case: Doc, actual: Doc,
                       evaluator: Callable[[Doc, Doc], Doc]) -> list[str]:
    """Sensitive answers never move the score; no lead is declined; one action per lead."""
    problems: list[str] = []
    sensitive = _sensitive_ids(fragment)
    leaked = sorted(set(actual["scoring_inputs"]) & sensitive)
    if leaked:
        problems.append(f"sensitive fields reached scoring: {leaked}")
    if actual["decline"] is not False or actual["action"] not in ACTIONS:
        problems.append("a lead was declined or given an action outside the closed list")
    for i, variant in enumerate(case.get("sensitive_variants") or []):
        if set(variant) - sensitive:
            problems.append(f"sensitive_variants[{i}] changes non-sensitive fields: {sorted(set(variant) - sensitive)}")
            continue
        changed = {**case["input"], "answers": {**case["input"].get("answers", {}), **variant}}
        other = evaluator(fragment, changed)
        if other["score"] != actual["score"] or other["action"] != actual["action"]:
            problems.append(f"sensitive_variants[{i}] changed the score or action")
    return problems


def collect(root: Path, pack: str | None = None) -> list[Path]:
    base = root / "evals" / "packs"
    pattern = f"{pack}/*.yaml" if pack else "*/*.yaml"
    return sorted(base.glob(pattern))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--pack", default=None)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        results = [run_case(root, path) for path in collect(root, args.pack)]
    except EvalError as exc:
        print(f"load error: {exc}")
        return 2
    for res in results:
        print(f"{'PASS' if res.ok else 'FAIL'} {res.case_id} ({res.path})")
        for problem in res.problems:
            print(f"    {problem}")
    failed = [r for r in results if not r.ok]
    print(f"pack evals: {len(results)} cases, {len(results) - len(failed)} passed, {len(failed)} failed")
    return 1 if failed or not results else 0


if __name__ == "__main__":
    raise SystemExit(main())
