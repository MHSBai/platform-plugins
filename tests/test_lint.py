"""Tests for tools/lint.py and tools/gen_manifest.py.

Each rule has at least one fixture that must fail it. A fixture is a copy of
the repository in a temporary directory with one deliberate defect; the
baseline copy must pass with no errors.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import gen_manifest  # noqa: E402
import lint  # noqa: E402
from manifest_lib import load_manifest  # noqa: E402

EM, EN, FIG = "\u2014", "\u2013", "\u2012"


_BASE_IGNORE = shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache")


def copy_ignore(directory: str, names: list[str]) -> set[str]:
    """Skip caches, and the git-ignored harvest clones; keep harvest/LEDGER.yaml."""
    ignored = set(_BASE_IGNORE(directory, names))
    if Path(directory).resolve() == (ROOT / "harvest").resolve():
        ignored |= {n for n in names if n != "LEDGER.yaml"}
    return ignored


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    shutil.copytree(ROOT, target, ignore=copy_ignore)
    return target


def errors(root: Path, release: bool = False) -> list[lint.Finding]:
    return [f for f in lint.run(root, release=release) if f.severity == "error"]


def rules_failed(root: Path, release: bool = False) -> set[str]:
    return {f.rule for f in errors(root, release)}


def edit_json(path: Path, mutate) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def edit_manifest(root: Path, mutate) -> None:
    path = root / "catalog" / "manifest.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def plugin_entry(data: dict, name: str) -> dict:
    return next(p for p in data["plugins"] if p["name"] == name)


def skill(root: Path, plugin: str, name: str) -> Path:
    return root / "plugins" / plugin / "skills" / name / "SKILL.md"


# --------------------------------------------------------------------- baseline


def test_repository_passes_without_errors() -> None:
    found = errors(ROOT)
    assert found == [], "\n".join(f.render() for f in found)


def test_baseline_fixture_passes(repo: Path) -> None:
    assert errors(repo) == []


def test_generated_files_are_current() -> None:
    assert gen_manifest.check(ROOT, load_manifest(ROOT)) == []


def test_counts_at_most_22_and_cap_24() -> None:
    manifest = load_manifest(ROOT)
    counts = [len(manifest.commands_in(c)) for c in manifest.combinations()]
    assert max(counts) == 22
    assert manifest.limits["max_commands_per_combination"] == 24
    assert len(counts) == 1 + 3 * (12 + 66 + 220)


def test_marketplace_lists_only_ga() -> None:
    data = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    manifest = load_manifest(ROOT)
    listed = {p["name"] for p in data["plugins"]}
    assert listed == {p.name for p in manifest.plugins if p.tier == "ga"}
    assert "mhsb-pack-family-law" not in listed and "mhsb-pack-estate-probate" not in listed


# --------------------------------------------------------------------- L01


def test_l01_unknown_plugin_field(repo: Path) -> None:
    edit_json(repo / "plugins/mhsb-clio/.claude-plugin/plugin.json", lambda d: d.update(bogus=1))
    assert "L01" in rules_failed(repo)


def test_l01_missing_version(repo: Path) -> None:
    edit_json(repo / "plugins/mhsb-clio/.claude-plugin/plugin.json", lambda d: d.pop("version"))
    assert "L01" in rules_failed(repo)


def test_l01_reserved_name() -> None:
    assert lint.reserved_name_problem("claude-tools")
    assert lint.reserved_name_problem("official-anthropic-kit")
    assert lint.reserved_name_problem("mhsb-firm-core") is None


# --------------------------------------------------------------------- L02


def test_l02_missing_owner(repo: Path) -> None:
    edit_json(repo / ".claude-plugin/marketplace.json", lambda d: d.pop("owner"))
    assert "L02" in rules_failed(repo)


def test_l02_hidden_pack_listed(repo: Path) -> None:
    def add(d: dict) -> None:
        d["plugins"].append({"name": "mhsb-pack-family-law", "source": "./plugins/mhsb-pack-family-law",
                             "description": "Family law fragment."})
    edit_json(repo / ".claude-plugin/marketplace.json", add)
    assert "L02" in rules_failed(repo)


def test_l02_parent_path_source(repo: Path) -> None:
    edit_json(repo / ".claude-plugin/marketplace.json",
              lambda d: d["plugins"][0].update(source="./../plugins/mhsb-firm-core"))
    assert "L02" in rules_failed(repo)


# --------------------------------------------------------------------- L03


def test_l03_top_level_custom_key(repo: Path) -> None:
    path = skill(repo, "mhsb-operations", "brief")
    path.write_text(path.read_text(encoding="utf-8").replace("name: brief\n", "name: brief\nregister: operational\n", 1),
                    encoding="utf-8")
    assert "L03" in rules_failed(repo)


def test_l03_missing_metadata_register(repo: Path) -> None:
    path = skill(repo, "mhsb-operations", "brief")
    path.write_text(path.read_text(encoding="utf-8").replace("  register: operational\n", "", 1), encoding="utf-8")
    assert "L03" in rules_failed(repo)


def test_l03_skill_missing_for_command(repo: Path) -> None:
    shutil.rmtree(repo / "plugins/mhsb-clio/skills/production")
    assert "L03" in rules_failed(repo)


def test_l03_frontmatter_not_on_first_line(repo: Path) -> None:
    path = skill(repo, "mhsb-clio", "production")
    path.write_text("\n" + path.read_text(encoding="utf-8"), encoding="utf-8")
    assert "L03" in rules_failed(repo)


# --------------------------------------------------------------------- L04


@pytest.mark.parametrize("char", [EM, EN, FIG])
def test_l04_each_dash(repo: Path, char: str) -> None:
    path = repo / "docs" / "release.md"
    path.write_text(path.read_text(encoding="utf-8") + f"\nA {char} B\n", encoding="utf-8")
    assert "L04" in rules_failed(repo)


# --------------------------------------------------------------------- L05


@pytest.mark.parametrize("text", [
    "Staff can simply run the brief.",
    "This is just a check.",
    "An easy way to start.",
    "A seamless handoff.",
    "A powerful view.",
    "Tap the button.",
    "The report is ready!",
    "Best-in-class reporting.",
    "Ready \U0001F680",
])
def test_l05_banned_text(repo: Path, text: str) -> None:
    path = repo / "plugins" / "mhsb-clio" / "README.md"
    path.write_text(path.read_text(encoding="utf-8") + f"\n{text}\n", encoding="utf-8")
    assert "L05" in rules_failed(repo)


def test_l05_word_boundary() -> None:
    assert lint.banned_in_text("Adjust the tapestry of justice.") == []


def test_l05_plugin_description(repo: Path) -> None:
    edit_json(repo / "plugins/mhsb-clio/.claude-plugin/plugin.json",
              lambda d: d.update(description="A seamless Clio plugin."))
    assert "L05" in rules_failed(repo)


# --------------------------------------------------------------------- L06


def test_l06_reading_level_operational(repo: Path) -> None:
    path = skill(repo, "mhsb-clio", "production")
    dense = ("Notwithstanding organizational considerations, the comprehensive administrative "
             "reconciliation methodology necessitates extraordinarily meticulous documentation, "
             "particularly regarding jurisdictional interpretations and institutional responsibilities.\n")
    path.write_text(path.read_text(encoding="utf-8") + "\n" + dense * 6, encoding="utf-8")
    assert "L06" in rules_failed(repo)


def test_fk_grade_orders_texts() -> None:
    simple = lint.flesch_kincaid_grade("The cat sat. The dog ran. We read the list.")
    dense = lint.flesch_kincaid_grade("Institutional administrative documentation necessitates "
                                      "comprehensive organizational reconciliation methodologies.")
    assert simple < 3 < 12 < dense


# --------------------------------------------------------------------- L07


@pytest.mark.parametrize("needle", ["not retrieved", "coverage"])
def test_l07_connected_skill_needs_phrase(repo: Path, needle: str) -> None:
    path = skill(repo, "mhsb-operations", "dates")
    text = path.read_text(encoding="utf-8")
    front_end = text.index("\n---\n", 4) + 5
    body = text[front_end:]
    for variant in (needle, needle.capitalize(), needle.title()):
        body = body.replace(variant, "omitted")
    path.write_text(text[:front_end] + body, encoding="utf-8")
    assert "L07" in rules_failed(repo)


# --------------------------------------------------------------------- L08


def test_l08_command_cap(repo: Path) -> None:
    edit_manifest(repo, lambda d: d["limits"].update(max_commands_per_combination=21))
    found = [f for f in errors(repo) if f.rule == "L08"]
    assert found and all("mhsb-clio" in f.message for f in found)


# --------------------------------------------------------------------- L09


def test_l09_duplicate_command(repo: Path) -> None:
    def dup(d: dict) -> None:
        plugin_entry(d, "mhsb-clio")["commands"].append(
            {"name": "brief", "register": "operational", "connector": "platform",
             "promise": "Duplicate.", "triggers": ["clio duplicate phrase"]})
    edit_manifest(repo, dup)
    assert "L09" in rules_failed(repo)


# --------------------------------------------------------------------- L10


def test_l10_same_phrase(repo: Path) -> None:
    edit_manifest(repo, lambda d: plugin_entry(d, "mhsb-clio")["commands"][1]["triggers"].append("anything stale"))
    assert "L10" in rules_failed(repo)


def test_l10_contained_phrase(repo: Path) -> None:
    edit_manifest(repo, lambda d: plugin_entry(d, "mhsb-clio")["commands"][1]["triggers"]
                  .append("is anything stale this week"))
    assert "L10" in rules_failed(repo)


def test_phrase_overlap_semantics() -> None:
    assert lint.phrases_overlap("Anything stale?", "anything stale")
    assert lint.phrases_overlap("anything stale", "is anything stale this week")
    assert not lint.phrases_overlap("duplicate sends", "duplicate date fields")


# --------------------------------------------------------------------- L11


def test_l11_not_adopted_in_ga(repo: Path) -> None:
    path = repo / "plugins/mhsb-pack-personal-injury/templates/welcome.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace("adopted_by: Synthetic Adopter (fixture, not an attorney adoption)", "adopted_by: NOT ADOPTED")
    path.write_text(text, encoding="utf-8")
    assert "L11" in rules_failed(repo)


def test_l11_missing_record_in_pilot(repo: Path) -> None:
    path = repo / "plugins/mhsb-pack-real-estate/templates/milestone-update.md"
    front, body, _ = lint.split_frontmatter(path.read_text(encoding="utf-8"))
    assert front is not None
    front.pop("adoption")
    path.write_text("---\n" + yaml.safe_dump(front) + "---\n" + body, encoding="utf-8")
    assert "L11" in rules_failed(repo)


def test_l11_fragment_without_adoption(repo: Path) -> None:
    path = repo / "plugins/mhsb-pack-immigration/fragment/fragment.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data.pop("adoption")
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    assert "L11" in rules_failed(repo)


def test_l11_synthetic_fails_release(repo: Path) -> None:
    assert "L11" not in rules_failed(repo)
    assert "L11" in rules_failed(repo, release=True)


def test_l11_non_markdown_template(repo: Path) -> None:
    (repo / "plugins/mhsb-pack-real-estate/templates/stray.txt").write_text("no record\n", encoding="utf-8")
    assert "L11" in rules_failed(repo)


# --------------------------------------------------------------------- L12


def add_ledger_row(root: Path, rel: str) -> None:
    path = root / "PROVENANCE.md"
    row = f"| {rel} | anthropics/example, skills/x/SKILL.md | 0123456789abcdef0123456789abcdef01234567 | Apache-2.0 | 2026-11-03 | Rewritten for law firms. |"
    text = path.read_text(encoding="utf-8").replace("|---|---|---|---|---|---|\n", "|---|---|---|---|---|---|\n" + row + "\n", 1)
    path.write_text(text, encoding="utf-8")


def test_l12_listed_file_without_header(repo: Path) -> None:
    add_ledger_row(repo, "plugins/mhsb-clio/skills/production/SKILL.md")
    assert "L12" in rules_failed(repo)


def test_l12_listed_file_with_header_passes(repo: Path) -> None:
    rel = "plugins/mhsb-clio/skills/production/SKILL.md"
    add_ledger_row(repo, rel)
    path = repo / rel
    text = path.read_text(encoding="utf-8")
    end = text.index("\n---\n", 4) + 5
    notice = ("<!--\nMHSB modification notice (Apache License, Version 2.0, Section 4(b)).\n"
              "Modified by MHSB Solutions on 2026-11-03.\nOriginal: anthropics/example, skills/x/SKILL.md, "
              "commit 0123456789abcdef0123456789abcdef01234567.\nOriginal license: Apache-2.0.\n"
              "Change note: Rewritten for law firms.\n-->\n")
    path.write_text(text[:end] + notice + text[end:], encoding="utf-8")
    assert "L12" not in rules_failed(repo)


def test_l12_listed_file_missing(repo: Path) -> None:
    add_ledger_row(repo, "plugins/does-not-exist.md")
    assert "L12" in rules_failed(repo)


# --------------------------------------------------------------------- L13


@pytest.mark.parametrize("component", ["hooks", "agents", "bin"])
def test_l13_forbidden_component(repo: Path, component: str) -> None:
    (repo / "plugins/mhsb-operations" / component).mkdir()
    (repo / "plugins/mhsb-operations" / component / "placeholder.md").write_text("x\n", encoding="utf-8")
    assert "L13" in rules_failed(repo)


def test_l13_local_mcp_server(repo: Path) -> None:
    edit_json(repo / "plugins/mhsb-operations/.mcp.json",
              lambda d: d["mcpServers"].update(local={"command": "node", "args": ["server.js"]}))
    assert "L13" in rules_failed(repo)


def test_l13_practice_pack_with_skills(repo: Path) -> None:
    target = repo / "plugins/mhsb-pack-real-estate/skills/closing"
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text("---\nname: closing\ndescription: x\n---\nx\n", encoding="utf-8")
    assert "L13" in rules_failed(repo)


def test_l13_missing_license_file(repo: Path) -> None:
    (repo / "plugins/mhsb-clio/LICENSE-SOURCE-AVAILABLE.md").unlink()
    assert "L13" in rules_failed(repo)


def test_l13_missing_core_license(repo: Path) -> None:
    (repo / "plugins/mhsb-firm-core/LICENSE").unlink()
    assert "L13" in rules_failed(repo)


# --------------------------------------------------------------------- L14


def test_l14_hand_edited_generated_file(repo: Path) -> None:
    edit_json(repo / ".claude-plugin/marketplace.json", lambda d: d.update(description="Edited by hand."))
    assert "L14" in rules_failed(repo)


def test_l14_counts_table_stale(repo: Path) -> None:
    path = repo / "catalog/counts.md"
    path.write_text(path.read_text(encoding="utf-8").replace("| 22 | 22 |", "| 20 | 20 |"), encoding="utf-8")
    assert "L14" in rules_failed(repo)


# --------------------------------------------------------------------- CLI


def test_cli_exit_codes(repo: Path) -> None:
    assert lint.main(["--root", str(repo)]) == 0
    assert lint.main(["--root", str(repo), "--release"]) == 1
    assert gen_manifest.main(["--root", str(repo), "--check"]) == 0


def test_l04_skips_harvest_clones_but_lints_ledger(repo: Path) -> None:
    clone = repo / "harvest" / "owner_repo" / "repo"
    clone.mkdir(parents=True)
    (clone / "README.md").write_text(f"third-party text {EM} untouched\n", encoding="utf-8")
    assert "L04" not in rules_failed(repo)
    ledger = repo / "harvest" / "LEDGER.yaml"
    ledger.write_text(ledger.read_text(encoding="utf-8") + f"# note {EN}\n", encoding="utf-8")
    assert "L04" in rules_failed(repo)


def test_generated_keywords_unique() -> None:
    for path in sorted((ROOT / "plugins").glob("*/.claude-plugin/plugin.json")):
        keywords = json.loads(path.read_text(encoding="utf-8"))["keywords"]
        assert len(keywords) == len(set(keywords)), path
