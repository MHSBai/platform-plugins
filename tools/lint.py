#!/usr/bin/env python3
"""Catalog and content lint for the MHSB platform plugin repository.

Rules (identifier, scope):

  L01 plugin-schema       every plugin.json against tools/schemas/plugin.schema.json
  L02 marketplace-schema  .claude-plugin/marketplace.json against its schema and the manifest
  L03 skill-frontmatter   every SKILL.md: allowed keys, required metadata, agreement with the manifest
  L04 dashes              U+2014, U+2013 and U+2012 in any text file
  L05 banned-phrases      marketing phrases, exclamation marks, emoji and listed words in user-facing text
  L06 reading-level       Flesch-Kincaid grade per SKILL.md body: 9 operational, 12 document
  L07 coverage            "coverage" and "not retrieved" in every connected skill body
  L08 command-cap         command count above the cap in any supported combination
  L09 duplicate-commands  duplicate command names within any supported combination
  L10 trigger-collision   two skills claiming the same or an overlapping trigger phrase
  L11 adoption            adoption record on every template file and fragment
  L12 provenance-header   Apache 4(b) modification notice on every file in PROVENANCE.md
  L13 structure           allowed components only; remote connectors only; pack layout; license files
  L14 generated-drift     outputs of tools/gen_manifest.py current with the manifest
  L16 connector-release   release only: each connector bundled by a general availability
                          plugin resolves inside the recorded edge, presents a certificate
                          valid for its host and answers an authenticated MCP initialize
                          with the recorded server name and version
                          (tools/release_check.py); the plugin declares privacyPolicyUrl
                          and termsOfServiceUrl. CI runs --release on every pull request
                          and every push to main.

Usage:
    python tools/lint.py [--root PATH] [--release]

--release turns warnings into errors. A synthetic adoption record is a warning
in development and an error at release.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

import yaml
from jsonschema import Draft202012Validator

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gen_manifest  # noqa: E402
import release_check  # noqa: E402
from manifest_lib import Manifest, ManifestError, load_manifest  # noqa: E402

SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"

DASHES = {"\u2014": "em dash (U+2014)", "\u2013": "en dash (U+2013)", "\u2012": "figure dash (U+2012)"}

BANNED_WORDS = ("tap", "simply", "just", "easy", "seamless", "seamlessly", "powerful")
MARKETING_PHRASES = (
    "best-in-class", "best in class", "cutting-edge", "cutting edge", "game-changer",
    "game changer", "game-changing", "revolutionary", "revolutionize", "world-class",
    "state-of-the-art", "next-generation", "next-gen", "supercharge", "unlock",
    "effortless", "effortlessly", "unparalleled", "industry-leading", "transformative",
    "elevate", "empower", "delight", "leverage", "robust", "magic", "magical",
    "hassle-free", "blazing", "turbocharge", "one-stop", "peace of mind",
)
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\U00002B00-\U00002BFF️]"
)

FK_LIMITS = {"operational": 9.0, "document": 12.0}

ALLOWED_SKILL_KEYS = {"name", "description", "metadata", "license", "compatibility", "allowed-tools"}
REQUIRED_SKILL_METADATA = ("register", "connector", "pack", "triggers")

FORBIDDEN_PLUGIN_PATHS = ("hooks", "agents", "bin", "commands", "monitors", "output-styles",
                          "themes", "workflows", ".lsp.json", "settings.json", "CLAUDE.md")

NOT_ADOPTED = "NOT ADOPTED"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")

PROVENANCE_MARKERS = ("MHSB modification notice", "Modified by MHSB Solutions", "Original license:")

TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".txt", ".toml", ".cfg", ".ini", ""}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules"}


@dataclass(frozen=True)
class Finding:
    rule: str
    path: str
    message: str
    severity: str = "error"

    def render(self) -> str:
        return f"{self.severity.upper()} {self.rule} {self.path}: {self.message}"


@dataclass
class Context:
    root: Path
    manifest: Manifest
    release: bool = False

    def rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root))
        except ValueError:
            return str(path)

    @property
    def plugins_dir(self) -> Path:
        return self.root / self.manifest.plugin_root


# ---------------------------------------------------------------------------
# Helpers


def iter_text_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file() and (path.suffix in TEXT_SUFFIXES or path.name in {"LICENSE", "NOTICE"}):
            yield path


def split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str, str | None]:
    """Return (frontmatter, body, error). Frontmatter must open on line one."""
    if not text.startswith("---\n"):
        return None, text, "frontmatter must open with '---' on the first line"
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text, "frontmatter is not closed"
    try:
        data = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError as exc:
        return None, text[end + 5:], f"frontmatter does not parse: {exc}"
    if not isinstance(data, dict):
        return None, text[end + 5:], "frontmatter must be a mapping"
    return data, text[end + 5:], None


def normalize_phrase(phrase: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9' ]+", " ", phrase.lower()).split())


def phrases_overlap(a: str, b: str) -> bool:
    """True when the phrases are equal or one is a contiguous word run of the other."""
    ta, tb = normalize_phrase(a).split(), normalize_phrase(b).split()
    if not ta or not tb:
        return False
    short, long_ = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    return any(long_[i:i + len(short)] == short for i in range(len(long_) - len(short) + 1))


_VOWEL_RUN = re.compile(r"[aeiouy]+")


def count_syllables(word: str) -> int:
    word = re.sub(r"[^a-z]", "", word.lower())
    if not word:
        return 0
    if len(word) <= 3:
        return 1
    stripped = re.sub(r"(?:[^laeiouy]es|[^laeiouy]ed|[^laeiouy]e)$", "", word)
    stripped = re.sub(r"^y", "", stripped)
    return max(1, len(_VOWEL_RUN.findall(stripped)))


def prose_for_reading(body: str) -> str:
    text = re.sub(r"```.*?```", " ", body, flags=re.S)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"`[^`]*`", " item ", text)
    text = re.sub(r"https?://\S+", " link ", text)
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("|"):
            continue
        stripped = re.sub(r"^(#+|[-*]|\d+\.)\s*", "", stripped)
        if stripped and stripped[-1] not in ".?:;":
            stripped += "."
        lines.append(stripped)
    return " ".join(lines)


def flesch_kincaid_grade(text: str) -> float:
    sentences = [s for s in re.split(r"[.?:;]+(?:\s|$)", text) if re.search(r"[A-Za-z]", s)]
    words = re.findall(r"[A-Za-z][A-Za-z'\-]*", text)
    if not sentences or not words:
        return 0.0
    syllables = sum(count_syllables(w) for part in words for w in part.split("-"))
    return 0.39 * (len(words) / len(sentences)) + 11.8 * (syllables / len(words)) - 15.59


def load_json(path: Path) -> tuple[Any, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)


def schema_errors(schema_name: str, data: Any) -> list[str]:
    schema = json.loads((SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    out = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        where = "/".join(str(p) for p in err.absolute_path) or "(root)"
        out.append(f"{where}: {err.message}")
    return out


RESERVED_PREFIXES = ("claude-", "anthropic-", "anthropics-", "cc-plugin-")
RESERVED_EXACT = {"claude", "anthropic", "anthropics", "claude-code", "claude-mods"}


def reserved_name_problem(name: str) -> str | None:
    folded = re.sub(r"[-_. ]+", "-", name.lower())
    if folded in RESERVED_EXACT or folded.startswith(RESERVED_PREFIXES):
        return f"name '{name}' is reserved for Anthropic plugins"
    words = folded.split("-")
    if "official" in words and ({"claude", "anthropic"} & set(words)):
        return f"name '{name}' places 'official' beside a reserved word"
    if {"claude", "anthropic", "anthropics"} & set(words):
        return f"name '{name}' reads as an Anthropic plugin"
    return None


def skill_files(ctx: Context) -> list[Path]:
    return sorted(ctx.plugins_dir.glob("*/skills/*/SKILL.md"))


def user_facing_files(ctx: Context) -> list[Path]:
    files: list[Path] = []
    for name in ("README.md", "CHANGELOG.md"):
        if (ctx.root / name).exists():
            files.append(ctx.root / name)
    if ctx.plugins_dir.exists():
        for path in sorted(ctx.plugins_dir.rglob("*")):
            if path.is_file() and path.suffix in {".md", ".yaml", ".yml"}:
                files.append(path)
    return files


# ---------------------------------------------------------------------------
# Rules


def rule_plugin_schema(ctx: Context) -> list[Finding]:
    findings = []
    for plugin in ctx.manifest.plugins:
        path = ctx.plugins_dir / plugin.name / ".claude-plugin" / "plugin.json"
        if not path.exists():
            findings.append(Finding("L01", ctx.rel(path), "plugin.json is missing"))
            continue
        data, err = load_json(path)
        if err:
            findings.append(Finding("L01", ctx.rel(path), f"invalid JSON: {err}"))
            continue
        for msg in schema_errors("plugin.schema.json", data):
            findings.append(Finding("L01", ctx.rel(path), msg))
        if isinstance(data, dict):
            problem = reserved_name_problem(str(data.get("name", "")))
            if problem:
                findings.append(Finding("L01", ctx.rel(path), problem))
            if data.get("name") != plugin.name:
                findings.append(Finding("L01", ctx.rel(path),
                                        f"name '{data.get('name')}' differs from directory and manifest"))
            if data.get("license") != plugin.license_id:
                findings.append(Finding("L01", ctx.rel(path),
                                        f"license '{data.get('license')}' differs from manifest "
                                        f"'{plugin.license_id}'"))
    return findings


def rule_marketplace_schema(ctx: Context) -> list[Finding]:
    path = ctx.root / ".claude-plugin" / "marketplace.json"
    rel = ctx.rel(path)
    if not path.exists():
        return [Finding("L02", rel, "marketplace.json is missing")]
    data, err = load_json(path)
    if err:
        return [Finding("L02", rel, f"invalid JSON: {err}")]
    findings = [Finding("L02", rel, msg) for msg in schema_errors("marketplace.schema.json", data)]
    if not isinstance(data, dict):
        return findings
    if ".." in str(data.get("name", "")):
        findings.append(Finding("L02", rel, "marketplace name contains '..'"))
    if data.get("name") != ctx.manifest.marketplace["name"]:
        findings.append(Finding("L02", rel, "marketplace name differs from the manifest"))
    listed = []
    for index, entry in enumerate(data.get("plugins") or []):
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        listed.append(name)
        source = entry.get("source")
        if isinstance(source, str):
            if ".." in source:
                findings.append(Finding("L02", rel, f"plugins[{index}] source contains '..'"))
            target = ctx.root / source
            if not (target / ".claude-plugin" / "plugin.json").exists():
                findings.append(Finding("L02", rel, f"plugins[{index}] source '{source}' has no plugin.json"))
            else:
                pdata, _ = load_json(target / ".claude-plugin" / "plugin.json")
                if isinstance(pdata, dict) and pdata.get("name") != name:
                    findings.append(Finding("L02", rel, f"plugins[{index}] entry name '{name}' differs "
                                                        f"from manifest name '{pdata.get('name')}'"))
                if "version" in entry and isinstance(pdata, dict) and "version" in pdata:
                    findings.append(Finding("L02", rel, f"plugins[{index}] sets version also set in "
                                                        "plugin.json"))
        try:
            tier = ctx.manifest.plugin(str(name)).tier
        except KeyError:
            findings.append(Finding("L02", rel, f"plugins[{index}] '{name}' is not in the manifest"))
            continue
        if tier != "ga":
            findings.append(Finding("L02", rel, f"plugins[{index}] '{name}' is {tier} and must not be listed"))
    expected = [p.name for p in ctx.manifest.plugins if p.tier == "ga"]
    for name in expected:
        if name not in listed:
            findings.append(Finding("L02", rel, f"general availability plugin '{name}' is not listed"))
    if len(listed) != len(set(listed)):
        findings.append(Finding("L02", rel, "duplicate plugin entry names"))
    return findings


def rule_skill_frontmatter(ctx: Context) -> list[Finding]:
    findings = []
    expected = {(c.plugin, c.name): c for c in ctx.manifest.all_commands()}
    found: set[tuple[str, str]] = set()
    for path in skill_files(ctx):
        rel = ctx.rel(path)
        plugin_name = path.parent.parent.parent.name
        skill_dir = path.parent.name
        found.add((plugin_name, skill_dir))
        data, _, err = split_frontmatter(path.read_text(encoding="utf-8"))
        if err or data is None:
            findings.append(Finding("L03", rel, err or "no frontmatter"))
            continue
        extra = set(data) - ALLOWED_SKILL_KEYS
        if extra:
            findings.append(Finding("L03", rel, f"keys outside the Agent Skills set: {sorted(extra)}"))
        name = data.get("name")
        if name != skill_dir:
            findings.append(Finding("L03", rel, f"name '{name}' differs from directory '{skill_dir}'"))
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name or "") \
                or len(name) > 64:
            findings.append(Finding("L03", rel, "name must be lowercase kebab-case, 64 characters at most"))
        desc = data.get("description")
        if not isinstance(desc, str) or not desc.strip():
            findings.append(Finding("L03", rel, "description is required"))
        elif len(desc) > 1024:
            findings.append(Finding("L03", rel, "description exceeds 1024 characters"))
        meta = data.get("metadata")
        if not isinstance(meta, dict):
            findings.append(Finding("L03", rel, "metadata mapping is required"))
            continue
        for key in REQUIRED_SKILL_METADATA:
            if key not in meta:
                findings.append(Finding("L03", rel, f"metadata.{key} is required"))
        if meta.get("register") not in FK_LIMITS:
            findings.append(Finding("L03", rel, "metadata.register must be operational or document"))
        if meta.get("connector") not in {"none", "firm", "platform"}:
            findings.append(Finding("L03", rel, "metadata.connector must be none, firm or platform"))
        if meta.get("pack") != plugin_name:
            findings.append(Finding("L03", rel, f"metadata.pack '{meta.get('pack')}' differs from plugin "
                                                f"'{plugin_name}'"))
        command = expected.get((plugin_name, skill_dir))
        if command is None:
            findings.append(Finding("L03", rel, "skill is not declared in the manifest"))
            continue
        if meta.get("register") != command.register:
            findings.append(Finding("L03", rel, "metadata.register differs from the manifest"))
        if meta.get("connector") != command.connector:
            findings.append(Finding("L03", rel, "metadata.connector differs from the manifest"))
        if list(meta.get("triggers") or []) != list(command.triggers):
            findings.append(Finding("L03", rel, "metadata.triggers differ from the manifest"))
    for plugin_name, name in sorted(set(expected) - found):
        findings.append(Finding("L03", f"{ctx.manifest.plugin_root}/{plugin_name}/skills/{name}/SKILL.md",
                                "manifest command has no SKILL.md"))
    return findings


def rule_dashes(ctx: Context) -> list[Finding]:
    findings = []
    for path in iter_text_files(ctx.root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for char, label in DASHES.items():
                if char in line:
                    findings.append(Finding("L04", f"{ctx.rel(path)}:{lineno}", label))
    return findings


def banned_in_text(text: str) -> list[str]:
    problems = []
    lowered = text.lower()
    for word in BANNED_WORDS:
        if re.search(rf"(?<![a-z\-]){re.escape(word)}(?![a-z\-])", lowered):
            problems.append(f"banned word '{word}'")
    for phrase in MARKETING_PHRASES:
        if re.search(rf"(?<![a-z]){re.escape(phrase)}(?![a-z])", lowered):
            problems.append(f"marketing phrase '{phrase}'")
    scrubbed = re.sub(r"<!--|!\[", "", text)
    if "!" in scrubbed:
        problems.append("exclamation mark")
    if EMOJI_RE.search(text):
        problems.append("emoji")
    return problems


def rule_banned_phrases(ctx: Context) -> list[Finding]:
    findings = []
    for path in user_facing_files(ctx):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for problem in banned_in_text(line):
                findings.append(Finding("L05", f"{ctx.rel(path)}:{lineno}", problem))
    for path in [ctx.root / ".claude-plugin" / "marketplace.json",
                 *sorted(ctx.plugins_dir.glob("*/.claude-plugin/plugin.json"))]:
        data, err = load_json(path) if path.exists() else (None, "missing")
        if err or not isinstance(data, dict):
            continue
        texts = [str(data.get("description", ""))]
        texts += [str(e.get("description", "")) for e in data.get("plugins") or [] if isinstance(e, dict)]
        for text in texts:
            for problem in banned_in_text(text):
                findings.append(Finding("L05", ctx.rel(path), f"description: {problem}"))
    return findings


def rule_reading_level(ctx: Context) -> list[Finding]:
    findings = []
    for path in skill_files(ctx):
        data, body, err = split_frontmatter(path.read_text(encoding="utf-8"))
        if err or data is None:
            continue
        register = (data.get("metadata") or {}).get("register")
        limit = FK_LIMITS.get(str(register))
        if limit is None:
            continue
        grade = flesch_kincaid_grade(prose_for_reading(body))
        if grade > limit:
            findings.append(Finding("L06", ctx.rel(path),
                                    f"Flesch-Kincaid grade {grade:.1f} exceeds {limit:.0f} for {register}"))
    return findings


def rule_coverage(ctx: Context) -> list[Finding]:
    findings = []
    for path in skill_files(ctx):
        data, body, err = split_frontmatter(path.read_text(encoding="utf-8"))
        if err or data is None:
            continue
        if (data.get("metadata") or {}).get("connector") in {"firm", "platform"}:
            lowered = body.lower()
            for needle in ("coverage", "not retrieved"):
                if needle not in lowered:
                    findings.append(Finding("L07", ctx.rel(path), f"connected skill body lacks '{needle}'"))
    return findings


def rule_command_cap(ctx: Context) -> list[Finding]:
    cap = int(ctx.manifest.limits["max_commands_per_combination"])
    findings = []
    for combo in ctx.manifest.combinations():
        count = len(ctx.manifest.commands_in(combo))
        if count > cap:
            findings.append(Finding("L08", "catalog/manifest.yaml",
                                    f"{combo.key}: {count} commands exceeds cap {cap}"))
    return findings


def rule_duplicate_commands(ctx: Context) -> list[Finding]:
    findings = []
    reported: set[tuple[str, ...]] = set()
    for combo in ctx.manifest.combinations():
        names: dict[str, str] = {}
        for command in ctx.manifest.commands_in(combo):
            if command.name in names:
                pair = tuple(sorted((names[command.name], command.plugin))) + (command.name,)
                if pair not in reported:
                    reported.add(pair)
                    findings.append(Finding("L09", "catalog/manifest.yaml",
                                            f"command '/{command.name}' appears in {pair[0]} and {pair[1]} "
                                            f"(combination {combo.key})"))
            else:
                names[command.name] = command.plugin
    return findings


def rule_trigger_collision(ctx: Context) -> list[Finding]:
    findings = []
    claims = [(f"{c.plugin}:{c.name}", t) for c in ctx.manifest.all_commands() for t in c.triggers]
    for i, (skill_a, phrase_a) in enumerate(claims):
        for skill_b, phrase_b in claims[i + 1:]:
            if skill_a != skill_b and phrases_overlap(phrase_a, phrase_b):
                findings.append(Finding("L10", "catalog/manifest.yaml",
                                        f"'{phrase_a}' ({skill_a}) overlaps '{phrase_b}' ({skill_b})"))
    return findings


def _adoption_problems(record: Any, tier: str, release: bool) -> list[tuple[str, str]]:
    if not isinstance(record, dict):
        return [("error", "adoption record (adopted_by, date, version) is missing")]
    problems: list[tuple[str, str]] = []
    values = {key: record.get(key) for key in ("adopted_by", "date", "version")}
    for key, value in values.items():
        if value is None or str(value).strip() == "":
            problems.append(("error", f"adoption.{key} is missing"))
    if problems:
        return problems
    placeholder = [key for key, value in values.items() if str(value).strip() == NOT_ADOPTED]
    if placeholder:
        if tier not in {"pilot", "hidden"}:
            problems.append(("error", f"'{NOT_ADOPTED}' is permitted only in pilot and hidden packs "
                                      f"(tier {tier})"))
        return problems
    if not DATE_RE.match(str(values["date"])):
        problems.append(("error", "adoption.date must be YYYY-MM-DD"))
    if not VERSION_RE.match(str(values["version"])):
        problems.append(("error", "adoption.version must be MAJOR.MINOR.PATCH"))
    if record.get("synthetic") is True:
        problems.append(("error" if release else "warning",
                         "synthetic adoption record; an attorney adoption is required before release"))
    return problems


def rule_adoption(ctx: Context) -> list[Finding]:
    findings = []
    for plugin in ctx.manifest.plugins:
        base = ctx.plugins_dir / plugin.name
        targets: list[tuple[Path, Any]] = []
        fragment = base / "fragment" / "fragment.yaml"
        if fragment.exists():
            try:
                data = yaml.safe_load(fragment.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError as exc:
                findings.append(Finding("L11", ctx.rel(fragment), f"does not parse: {exc}"))
                data = {}
            targets.append((fragment, data.get("adoption") if isinstance(data, dict) else None))
            if isinstance(data, dict) and data.get("release_tier") != plugin.tier:
                findings.append(Finding("L11", ctx.rel(fragment),
                                        f"release_tier '{data.get('release_tier')}' differs from manifest "
                                        f"'{plugin.tier}'"))
        templates_dir = base / "templates"
        if templates_dir.exists():
            for path in sorted(templates_dir.rglob("*")):
                if not path.is_file():
                    continue
                if path.suffix != ".md":
                    findings.append(Finding("L11", ctx.rel(path), "template files must be Markdown with "
                                                                  "an adoption frontmatter"))
                    continue
                front, _, err = split_frontmatter(path.read_text(encoding="utf-8"))
                targets.append((path, (front or {}).get("adoption") if not err else None))
        for path, record in targets:
            for severity, message in _adoption_problems(record, plugin.tier, ctx.release):
                findings.append(Finding("L11", ctx.rel(path), message, severity))
    return findings


def provenance_entries(root: Path) -> list[dict[str, str]]:
    path = root / "PROVENANCE.md"
    if not path.exists():
        return []
    entries = []
    in_ledger = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_ledger = line.strip().lower() == "## ledger"
            continue
        if not in_ledger or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6 or cells[0].lower() == "file" or set(cells[0]) <= {"-", ":"}:
            continue
        entries.append(dict(zip(("file", "source", "commit", "license", "date", "change"), cells)))
    return entries


def rule_provenance_header(ctx: Context) -> list[Finding]:
    findings = []
    if not (ctx.root / "PROVENANCE.md").exists():
        return [Finding("L12", "PROVENANCE.md", "PROVENANCE.md is missing")]
    for entry in provenance_entries(ctx.root):
        rel = entry["file"].strip("`")
        path = ctx.root / rel
        if not path.exists():
            findings.append(Finding("L12", rel, "file listed in PROVENANCE.md does not exist"))
            continue
        text = path.read_text(encoding="utf-8")
        front, body, err = split_frontmatter(text)
        head = "\n".join((body if not err else text).lstrip("\n").splitlines()[:15])
        missing = [m for m in PROVENANCE_MARKERS if m not in head]
        if missing:
            findings.append(Finding("L12", rel, f"Apache 4(b) modification notice missing at top: {missing}"))
        for key in ("source", "commit", "license", "date", "change"):
            if not entry.get(key):
                findings.append(Finding("L12", "PROVENANCE.md", f"{rel}: ledger field '{key}' is empty"))
    return findings


def rule_structure(ctx: Context) -> list[Finding]:
    findings = []
    connector_urls = set(ctx.manifest.connectors.values())
    for name in ("NOTICE.md", "PROVENANCE.md", "CHANGELOG.md"):
        if not (ctx.root / name).exists():
            findings.append(Finding("L13", name, "required root file is missing"))
    if ctx.plugins_dir.exists():
        declared = {p.name for p in ctx.manifest.plugins}
        for child in sorted(ctx.plugins_dir.iterdir()):
            if child.is_dir() and child.name not in declared:
                findings.append(Finding("L13", ctx.rel(child), "plugin directory is not in the manifest"))
    for plugin in ctx.manifest.plugins:
        base = ctx.plugins_dir / plugin.name
        rel = ctx.rel(base)
        if not base.is_dir():
            findings.append(Finding("L13", rel, "plugin directory is missing"))
            continue
        for forbidden in FORBIDDEN_PLUGIN_PATHS:
            if (base / forbidden).exists():
                findings.append(Finding("L13", f"{rel}/{forbidden}", "component not permitted in this line"))
        if not (base / "README.md").exists():
            findings.append(Finding("L13", rel, "README.md is missing"))
        if plugin.license_key == "apache":
            if not (base / "LICENSE").exists():
                findings.append(Finding("L13", rel, "LICENSE (Apache-2.0) is missing"))
        elif not (base / "LICENSE-SOURCE-AVAILABLE.md").exists():
            findings.append(Finding("L13", rel, "LICENSE-SOURCE-AVAILABLE.md is missing"))
        mcp = base / ".mcp.json"
        if mcp.exists():
            data, err = load_json(mcp)
            servers = (data or {}).get("mcpServers", data) if not err else None
            if not isinstance(servers, dict) or not servers:
                findings.append(Finding("L13", ctx.rel(mcp), "no MCP server map"))
            else:
                for sname, server in servers.items():
                    if not isinstance(server, dict) or server.get("type") != "http" \
                            or "command" in server or server.get("url") not in connector_urls:
                        findings.append(Finding("L13", ctx.rel(mcp), f"server '{sname}' must be a remote "
                                                                     "http connector from the manifest"))
        if plugin.kind == "practice":
            if (base / "skills").exists():
                findings.append(Finding("L13", f"{rel}/skills", "practice packs contain no skills"))
            if not (base / "fragment" / "fragment.yaml").exists():
                findings.append(Finding("L13", rel, "fragment/fragment.yaml is missing"))
            templates = base / "templates"
            if not templates.is_dir() or not any(p.is_file() for p in templates.rglob("*")):
                findings.append(Finding("L13", rel, "templates/ with adoption placeholders is missing"))
    return findings


def rule_generated_drift(ctx: Context) -> list[Finding]:
    return [Finding("L14", line.split(": ", 1)[-1], line.split(":", 1)[0] + "; run tools/gen_manifest.py")
            for line in gen_manifest.check(ctx.root, ctx.manifest)]


CONNECTOR_LISTING_FIELDS = ("privacyPolicyUrl", "termsOfServiceUrl")


def rule_connector_release(ctx: Context) -> list[Finding]:
    """Release only: a general availability connector plugin needs a live endpoint."""
    if not ctx.release:
        return []
    findings = []
    ga = [p for p in ctx.manifest.plugins if p.mcp is not None and p.tier == "ga"]
    for plugin in ga:
        path = ctx.plugins_dir / plugin.name / ".claude-plugin" / "plugin.json"
        data, _ = load_json(path)
        for key in CONNECTOR_LISTING_FIELDS:
            if not isinstance(data, dict) or not data.get(key):
                findings.append(Finding("L16", ctx.rel(path), f"connector plugin at tier ga lacks {key}"))
    results = release_check.run(ctx.manifest, keys={p.mcp for p in ga}) if ga else {}
    for plugin in ga:
        result = results[plugin.mcp]
        if not result.ok:
            findings.append(Finding("L16", f"{ctx.manifest.plugin_root}/{plugin.name}/.mcp.json",
                                    f"connector plugin at tier ga fails the release check: "
                                    f"{result.render()}"))
    return findings


RULES: list[tuple[str, Callable[[Context], list[Finding]]]] = [
    ("L01", rule_plugin_schema),
    ("L02", rule_marketplace_schema),
    ("L03", rule_skill_frontmatter),
    ("L04", rule_dashes),
    ("L05", rule_banned_phrases),
    ("L06", rule_reading_level),
    ("L07", rule_coverage),
    ("L08", rule_command_cap),
    ("L09", rule_duplicate_commands),
    ("L10", rule_trigger_collision),
    ("L11", rule_adoption),
    ("L12", rule_provenance_header),
    ("L13", rule_structure),
    ("L14", rule_generated_drift),
    ("L16", rule_connector_release),
]


def run(root: Path, release: bool = False) -> list[Finding]:
    try:
        manifest = load_manifest(root)
    except (OSError, ManifestError, yaml.YAMLError) as exc:
        return [Finding("L00", "catalog/manifest.yaml", f"manifest does not load: {exc}")]
    ctx = Context(root=root, manifest=manifest, release=release)
    findings: list[Finding] = []
    for _, rule in RULES:
        findings.extend(rule(ctx))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint the platform plugin repository.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--release", action="store_true", help="treat warnings as errors")
    args = parser.parse_args(argv)
    findings = run(args.root.resolve(), release=args.release)
    for finding in findings:
        print(finding.render())
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    print(f"lint: {len(RULES)} rules, {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
