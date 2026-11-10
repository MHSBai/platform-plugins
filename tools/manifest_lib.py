"""Shared loading and enumeration for catalog/manifest.yaml.

The manifest is the single authority for plugins, commands, release tiers,
trigger phrases and supported installation combinations. Both the generator
and the lint import this module so that they read the manifest identically.
"""

from __future__ import annotations

import ipaddress
import itertools
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

MANIFEST_RELPATH = Path("catalog") / "manifest.yaml"

PLUGIN_KINDS = ("core", "operations", "platform", "practice")
REGISTERS = ("operational", "document")
CONNECTORS = ("none", "firm", "platform")
TIERS = ("ga", "pilot", "hidden")


class ManifestError(ValueError):
    """Raised when the manifest is structurally invalid."""


@dataclass(frozen=True)
class Command:
    name: str
    plugin: str
    register: str
    connector: str
    promise: str
    triggers: tuple[str, ...]


@dataclass(frozen=True)
class Plugin:
    name: str
    kind: str
    tier: str
    license_key: str
    license_id: str
    category: str
    mcp: str | None
    description: str
    commands: tuple[Command, ...]
    practice: str | None = None
    offered_without_subscription: bool = False


@dataclass(frozen=True)
class Combination:
    family: str
    plugins: tuple[str, ...]

    @property
    def key(self) -> str:
        return "+".join(self.plugins)


@dataclass
class Manifest:
    raw: dict[str, Any]
    plugins: list[Plugin] = field(default_factory=list)

    @property
    def marketplace(self) -> dict[str, Any]:
        return self.raw["marketplace"]

    @property
    def defaults(self) -> dict[str, Any]:
        return self.raw["defaults"]

    @property
    def connectors(self) -> dict[str, str]:
        return self.raw["connectors"]

    @property
    def limits(self) -> dict[str, int]:
        return self.raw["limits"]

    @property
    def plugin_root(self) -> str:
        return str(self.defaults.get("plugin_root", "plugins"))

    def plugin(self, name: str) -> Plugin:
        for plugin in self.plugins:
            if plugin.name == name:
                return plugin
        raise KeyError(name)

    def by_kind(self, kind: str) -> list[Plugin]:
        return [p for p in self.plugins if p.kind == kind]

    def all_commands(self) -> list[Command]:
        return [c for p in self.plugins for c in p.commands]

    def combinations(self) -> list[Combination]:
        """Enumerate every supported installation combination."""
        result: list[Combination] = []
        for rule in self.raw["combinations"]:
            fixed: list[str] = []
            for kind in rule.get("include", []):
                fixed.extend(p.name for p in self.by_kind(kind))
            choice_sets: list[list[tuple[str, ...]]] = []
            for choose in rule.get("choose", []):
                pool = [p.name for p in self.by_kind(choose["kind"])]
                options: list[tuple[str, ...]] = []
                for size in range(int(choose["min"]), int(choose["max"]) + 1):
                    options.extend(itertools.combinations(pool, size))
                choice_sets.append(options)
            if not choice_sets:
                result.append(Combination(rule["id"], tuple(fixed)))
                continue
            for picks in itertools.product(*choice_sets):
                names = list(fixed)
                for pick in picks:
                    names.extend(pick)
                result.append(Combination(rule["id"], tuple(names)))
        return result

    def commands_in(self, combination: Combination) -> list[Command]:
        return [c for name in combination.plugins for c in self.plugin(name).commands]


def _require(mapping: dict[str, Any], key: str, where: str) -> Any:
    if key not in mapping:
        raise ManifestError(f"{where}: missing key '{key}'")
    return mapping[key]


def _flag(mapping: dict[str, Any], key: str, where: str) -> bool:
    value = mapping.get(key, False)
    if not isinstance(value, bool):
        raise ManifestError(f"{where}: '{key}' must be true or false")
    return value


def _check_connector_expectations(raw: dict[str, Any]) -> None:
    """connector_identity and connector_edge: declared keys and well-formed values."""
    identity = raw.get("connector_identity") or {}
    if not isinstance(identity, dict):
        raise ManifestError("connector_identity must be a mapping")
    for key, entry in identity.items():
        if key not in raw["connectors"]:
            raise ManifestError(f"connector_identity: connector '{key}' not declared")
        if not isinstance(entry, dict) or not entry.get("server_name") or not entry.get("server_version"):
            raise ManifestError(f"connector_identity {key}: server_name and server_version are required")
    for key in raw["connectors"]:
        if key not in identity:
            raise ManifestError(f"connector_identity: connector '{key}' has no expected identity")
    edge = raw.get("connector_edge") or {}
    if not isinstance(edge, dict):
        raise ManifestError("connector_edge must be a mapping")
    for cidr in edge.get("addresses") or []:
        try:
            ipaddress.ip_network(str(cidr))
        except ValueError as exc:
            raise ManifestError(f"connector_edge.addresses: {exc}") from exc


def parse_manifest(raw: dict[str, Any]) -> Manifest:
    """Validate the manifest structure and return a typed view of it."""
    for key in ("schema_version", "marketplace", "defaults", "licenses", "connectors",
                "combinations", "limits", "plugins"):
        _require(raw, key, "manifest")
    licenses: dict[str, str] = raw["licenses"]
    _check_connector_expectations(raw)
    manifest = Manifest(raw=raw)
    seen: set[str] = set()
    for entry in raw["plugins"]:
        name = _require(entry, "name", "plugin")
        where = f"plugin {name}"
        if name in seen:
            raise ManifestError(f"{where}: declared twice")
        seen.add(name)
        kind = _require(entry, "kind", where)
        tier = _require(entry, "tier", where)
        license_key = _require(entry, "license", where)
        mcp = entry.get("mcp")
        if kind not in PLUGIN_KINDS:
            raise ManifestError(f"{where}: kind '{kind}' not in {PLUGIN_KINDS}")
        if tier not in TIERS:
            raise ManifestError(f"{where}: tier '{tier}' not in {TIERS}")
        if license_key not in licenses:
            raise ManifestError(f"{where}: license '{license_key}' not declared")
        if mcp is not None and mcp not in raw["connectors"]:
            raise ManifestError(f"{where}: connector '{mcp}' not declared")
        commands: list[Command] = []
        for cmd in entry.get("commands") or []:
            cname = _require(cmd, "name", where)
            cwhere = f"{where} command {cname}"
            register = _require(cmd, "register", cwhere)
            connector = _require(cmd, "connector", cwhere)
            if register not in REGISTERS:
                raise ManifestError(f"{cwhere}: register '{register}' not in {REGISTERS}")
            if connector not in CONNECTORS:
                raise ManifestError(f"{cwhere}: connector '{connector}' not in {CONNECTORS}")
            triggers = tuple(_require(cmd, "triggers", cwhere))
            if not triggers:
                raise ManifestError(f"{cwhere}: at least one trigger phrase is required")
            commands.append(Command(cname, name, register, connector,
                                    str(_require(cmd, "promise", cwhere)), triggers))
        if kind == "practice" and commands:
            raise ManifestError(f"{where}: practice packs add no commands")
        manifest.plugins.append(Plugin(
            name=name, kind=kind, tier=tier, license_key=license_key,
            license_id=licenses[license_key], category=str(entry.get("category", "")),
            mcp=mcp, description=" ".join(str(_require(entry, "description", where)).split()),
            commands=tuple(commands), practice=entry.get("practice"),
            offered_without_subscription=_flag(entry, "offered_without_subscription", where),
        ))
    return manifest


def load_manifest(root: Path) -> Manifest:
    path = root / MANIFEST_RELPATH
    with path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    if not isinstance(raw, dict):
        raise ManifestError(f"{path}: top level must be a mapping")
    return parse_manifest(raw)
