#!/usr/bin/env python3
"""Deterministic routing check over evals/routing/phrases.yaml.

Claude Code selects a skill from its name and description; it does not read
metadata. This check therefore routes against the description text in each
SKILL.md: the phrases a description quotes (its "for example" requests, which
include every trigger phrase the manifest declares for that command) are the
skill's trigger set. A quoted phrase matches when its words appear as a
contiguous run in the routing phrase after normalization (lower case,
contractions expanded, punctuation removed). For every supported combination in
catalog/manifest.yaml and every phrase in the routing suite, the check fails when:

* a manifest trigger phrase is not quoted in that skill's description;
* a phrase matches the descriptions of two or more installed skills (ambiguous routing);
* the resolved skill differs from the expected skill for that command set. A phrase that
  matches no installed description resolves to /start, which names the plugin that
  provides the command (start/SKILL.md, Procedure step 8);
* a phrase, command set or skill named in the suite does not exist, or the suite does not
  hold exactly sixty phrases.

The model eval (tools/model_evals.py --routing) tests the same phrases against the same
descriptions with a model; this check calls no model and shows description-phrase
disjointness, not model behaviour.

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

DEFAULT_ROOT = Path(__file__).resolve().parent.parent
SUITE = Path("evals/routing/phrases.yaml")
QUOTED = re.compile(r'"([^"]+)"')
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


def skill_description(root: Path, manifest: Manifest, plugin: str, name: str) -> str:
    """The description Claude Code reads from a skill's SKILL.md frontmatter."""
    path = root / manifest.plugin_root / plugin / "skills" / name / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or end == -1:
        raise SuiteError(f"{path.relative_to(root)}: no frontmatter")
    front = yaml.safe_load(text[4:end]) or {}
    return " ".join(str(front.get("description", "")).split())


def description_phrases(root: Path, manifest: Manifest) -> dict[str, tuple[str, ...]]:
    """Quoted request phrases per skill, keyed '<plugin>:<command>'."""
    return {f"{c.plugin}:{c.name}": tuple(QUOTED.findall(skill_description(root, manifest, c.plugin, c.name)))
            for c in manifest.all_commands()}


def route(manifest: Manifest, combo: Combination, phrase: str,
          phrases: dict[str, tuple[str, ...]] | None = None) -> list[str]:
    """Installed skills whose description quotes a phrase contained in the request."""
    if phrases is None:
        phrases = description_phrases(DEFAULT_ROOT, manifest)
    tokens = normalize(phrase)
    matched = []
    for command in manifest.commands_in(combo):
        if any(contains_run(tokens, normalize(t)) for t in phrases[f"{command.plugin}:{command.name}"]):
            matched.append(command.name)
    return matched


def missing_triggers(manifest: Manifest, phrases: dict[str, tuple[str, ...]]) -> list[str]:
    """Manifest trigger phrases that the skill's description does not quote."""
    out = []
    for command in manifest.all_commands():
        quoted = {tuple(normalize(q)) for q in phrases[f"{command.plugin}:{command.name}"]}
        for trigger in command.triggers:
            if tuple(normalize(trigger)) not in quoted:
                out.append(f"MISSING {command.plugin}:{command.name} trigger '{trigger}' is not quoted "
                           "in the description")
    return out


def run(root: Path, verbose: bool = False) -> int:
    manifest = load_manifest(root)
    try:
        phrases = load_suite(root, manifest)
        described = description_phrases(root, manifest)
    except (SuiteError, OSError, yaml.YAMLError) as exc:
        print(f"LOAD ERROR {exc}")
        return 2
    combos = manifest.combinations()
    failures: list[str] = missing_triggers(manifest, described)
    seen: set[tuple[str, str, str]] = set()
    checks = 0
    for combo in combos:
        cset = command_set(manifest, combo)
        if cset not in COMMAND_SETS:
            print(f"LOAD ERROR combination {combo.key}: command set '{cset}' is not in the suite")
            return 2
        for p in phrases:
            checks += 1
            matched = route(manifest, combo, p.text, described)
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
    print(f"routing check (description-phrase disjointness): {len(phrases)} phrases, {len(combos)} combinations, {len(sets)} command sets, "
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
