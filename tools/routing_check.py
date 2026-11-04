#!/usr/bin/env python3
"""Deterministic routing check over evals/routing/phrases.yaml.

For every supported combination in catalog/manifest.yaml and every phrase in the routing
suite, the check finds the installed skills whose trigger set matches the phrase. A trigger
matches when its words appear as a contiguous run in the phrase after normalization
(lower case, contractions expanded, punctuation removed). The check fails when:

* a phrase matches the trigger sets of two or more installed skills (ambiguous routing);
* the resolved skill differs from the expected skill for that command set. A phrase that
  matches no installed trigger set resolves to /start, which names the plugin that
  provides the command (start/references/routing.md, Step 5);
* a phrase, command set or skill named in the suite does not exist, or the suite does not
  hold exactly sixty phrases.

The model eval (tools/model_evals.py --routing) tests the same phrases against the skill
descriptions with a model; this check tests the trigger sets alone and calls no model.

Usage:
    python tools/routing_check.py [--root PATH] [--verbose]

Exit status 0 when every combination routes every phrase as expected, 1 on any failure,
2 on a load error.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manifest_lib import Combination, Manifest, load_manifest  # noqa: E402

SUITE = Path("evals/routing/phrases.yaml")
SUITE_SIZE = 60
FALLBACK = "start"
COMMAND_SETS = ("core-only", "lawmatics", "clio", "mycase")

CONTRACTIONS = {
    "what's": "what is", "who's": "who is", "where's": "where is", "it's": "it is",
    "that's": "that is", "there's": "there is", "i'm": "i am", "we're": "we are",
    "they're": "they are", "you're": "you are", "can't": "cannot", "won't": "will not",
    "don't": "do not", "doesn't": "does not", "didn't": "did not", "isn't": "is not",
    "aren't": "are not", "haven't": "have not", "hasn't": "has not", "i've": "i have",
    "we've": "we have", "i'd": "i would", "we'd": "we would", "i'll": "i will",
    "we'll": "we will", "let's": "let us", "o'clock": "oclock",
}


def normalize(text: str) -> list[str]:
    """Lower case, expand contractions, drop possessive endings and punctuation."""
    lowered = text.lower().replace("’", "'")
    words = []
    for raw in lowered.split():
        word = raw.strip(".,;:?\"()")
        word = CONTRACTIONS.get(word, word)
        word = re.sub(r"'s$", "", word)
        words.append(word)
    joined = " ".join(words)
    return re.sub(r"[^a-z0-9 ]+", " ", joined).split()


def contains_run(phrase: list[str], trigger: list[str]) -> bool:
    if not trigger or len(trigger) > len(phrase):
        return False
    return any(phrase[i:i + len(trigger)] == trigger for i in range(len(phrase) - len(trigger) + 1))


@dataclass(frozen=True)
class Phrase:
    pid: str
    text: str
    intended: str
    expected: dict[str, str]


class SuiteError(Exception):
    """The routing suite cannot be loaded or names something that does not exist."""


def load_suite(root: Path, manifest: Manifest) -> list[Phrase]:
    path = root / SUITE
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise SuiteError(f"{SUITE}: {exc}") from exc
    names = {c.name for c in manifest.all_commands()}
    phrases = []
    for item in raw.get("phrases") or []:
        expected = dict(item.get("expected") or {})
        if set(expected) != set(COMMAND_SETS):
            raise SuiteError(f"{item.get('id')}: expected must name exactly {list(COMMAND_SETS)}")
        for skill in [item.get("intended"), *expected.values()]:
            if skill not in names:
                raise SuiteError(f"{item.get('id')}: unknown skill '{skill}'")
        phrases.append(Phrase(str(item["id"]), str(item["phrase"]), str(item["intended"]), expected))
    if len(phrases) != SUITE_SIZE:
        raise SuiteError(f"{SUITE}: {len(phrases)} phrases; the suite holds exactly {SUITE_SIZE}")
    ids = [p.pid for p in phrases]
    if len(ids) != len(set(ids)):
        raise SuiteError(f"{SUITE}: duplicate phrase identifiers")
    return phrases


def command_set(manifest: Manifest, combo: Combination) -> str:
    platforms = [n for n in combo.plugins if manifest.plugin(n).kind == "platform"]
    if not platforms:
        return "core-only"
    return platforms[0].removeprefix("mhsb-")


def route(manifest: Manifest, combo: Combination, phrase: str) -> list[str]:
    tokens = normalize(phrase)
    matched = []
    for command in manifest.commands_in(combo):
        if any(contains_run(tokens, normalize(t)) for t in command.triggers):
            matched.append(command.name)
    return matched


def run(root: Path, verbose: bool = False) -> int:
    manifest = load_manifest(root)
    try:
        phrases = load_suite(root, manifest)
    except SuiteError as exc:
        print(f"LOAD ERROR {exc}")
        return 2
    combos = manifest.combinations()
    failures: list[str] = []
    seen: set[tuple[str, str, str]] = set()
    checks = 0
    for combo in combos:
        cset = command_set(manifest, combo)
        if cset not in COMMAND_SETS:
            print(f"LOAD ERROR combination {combo.key}: command set '{cset}' is not in the suite")
            return 2
        for p in phrases:
            checks += 1
            matched = route(manifest, combo, p.text)
            resolved = matched[0] if len(matched) == 1 else (FALLBACK if not matched else None)
            key = (p.pid, cset, ",".join(matched))
            if len(matched) > 1:
                if key not in seen:
                    failures.append(f"AMBIGUOUS {p.pid} [{cset}] '{p.text}' matches {matched}")
            elif resolved != p.expected[cset]:
                if key not in seen:
                    failures.append(f"WRONG {p.pid} [{cset}] '{p.text}' routes to {resolved}, "
                                    f"expected {p.expected[cset]}")
            elif verbose and key not in seen:
                print(f"ok {p.pid} [{cset}] {resolved}")
            seen.add(key)
    for line in failures:
        print(line)
    sets = sorted({command_set(manifest, c) for c in combos})
    print(f"routing check: {len(phrases)} phrases, {len(combos)} combinations, {len(sets)} command sets, "
          f"{checks} checks, {len(failures)} failure(s)")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)
    return run(args.root, args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
