"""Tests for the source-available license notices (PP1-M3).

All notices are generated from one template, so they cannot drift apart, and
a plugin that the offer provides without a Connected subscription (the MyCase
vocabulary plugin) carries a grant for firms under a buildout agreement.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import gen_manifest  # noqa: E402
from manifest_lib import load_manifest  # noqa: E402

NOTICE = "LICENSE-SOURCE-AVAILABLE.md"
BUILDOUT_GRANT = "AI Policy and Training buildout agreement"


def test_every_source_available_notice_is_generated() -> None:
    manifest = load_manifest(ROOT)
    outputs = gen_manifest.outputs(manifest)
    for plugin in manifest.plugins:
        rel = Path(manifest.plugin_root) / plugin.name / NOTICE
        if plugin.license_key == "source_available":
            assert rel in outputs, f"{rel} is not generated from the template"
            assert (ROOT / rel).read_text(encoding="utf-8") == outputs[rel]
        else:
            assert rel not in outputs


def test_mycase_offered_without_subscription() -> None:
    plugin = load_manifest(ROOT).plugin("mhsb-mycase")
    assert plugin.offered_without_subscription


def test_buildout_grant_only_where_offered_without_subscription() -> None:
    manifest = load_manifest(ROOT)
    for plugin in manifest.plugins:
        if plugin.license_key != "source_available":
            continue
        text = (ROOT / manifest.plugin_root / plugin.name / NOTICE).read_text(encoding="utf-8")
        assert (BUILDOUT_GRANT in text) is plugin.offered_without_subscription, plugin.name


def test_readme_license_section_names_the_buildout_grant() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    section = readme.split("## License", 1)[1]
    assert "mhsb-mycase" in section and BUILDOUT_GRANT in section
