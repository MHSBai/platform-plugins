#!/usr/bin/env python3
"""Release check for the remote MCP connectors bundled by connector plugins.

The check establishes that the endpoint is MHSB's, not only that a
certificate exists for the name. For every connector URL in
catalog/manifest.yaml it

1. resolves the host name and, where ``connector_edge`` in the manifest
   records the addresses (CIDR ranges) or the canonical name the connector
   must resolve to, requires every resolved address to lie in those ranges
   and the canonical name to match;
2. opens a TLS session and verifies that the presented certificate chains to a
   trusted root and matches the host name; and
3. sends an MCP ``initialize`` request and requires a JSON-RPC result (JSON or
   server-sent events) whose ``serverInfo`` carries the name and version
   recorded for the connector in ``connector_identity``.

An HTTP 401 is never accepted: a static 401 with a Bearer challenge proves
nothing about who operates the host. The MHSB service answers ``initialize``
only for a signed-in client, so the check sends a bearer token read from the
environment variable ``MHSB_RELEASE_CHECK_TOKEN_<KEY>`` (for example
``MHSB_RELEASE_CHECK_TOKEN_FIRM``). The token is never printed; the output
states only whether it is SET or EMPTY.

A connector plugin may be listed at tier ``ga`` only when its connector passes.
``tools/lint.py --release`` runs this check (rule L16) for the connectors of
general availability plugins. Standard library only.

Usage:
    python tools/release_check.py [--root PATH] [--timeout SECONDS]

Exit status 1 when a connector used by a general availability plugin fails;
failures of connectors used only by pilot or hidden plugins are reported and
do not change the exit status.
"""

from __future__ import annotations

import argparse
import http.client
import ipaddress
import json
import os
import socket
import ssl
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manifest_lib import Manifest, load_manifest  # noqa: E402

MCP_PROTOCOL_VERSION = "2025-06-18"
DEFAULT_TIMEOUT = 10.0

INITIALIZE = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": MCP_PROTOCOL_VERSION,
        "capabilities": {},
        "clientInfo": {"name": "mhsb-release-check", "version": "1"},
    },
}


TOKEN_ENV_PREFIX = "MHSB_RELEASE_CHECK_TOKEN_"


@dataclass(frozen=True)
class Expected:
    """What the endpoint must prove before a connector plugin is listed.

    ``server_name`` and ``server_version`` come from ``connector_identity`` in
    the manifest; ``networks`` and ``canonical_name`` from ``connector_edge``.
    An empty ``networks`` tuple or a None ``canonical_name`` means that the
    manifest records no such constraint.
    """

    server_name: str | None
    server_version: str | None
    networks: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...] = field(default_factory=tuple)
    canonical_name: str | None = None


@dataclass(frozen=True)
class CheckResult:
    url: str
    ok: bool
    step: str
    detail: str

    def render(self) -> str:
        return f"{'PASS' if self.ok else 'FAIL'} {self.url} [{self.step}] {self.detail}"


def expected_for(manifest: Manifest, key: str) -> Expected:
    """The expected identity and edge for one connector key, from the manifest."""
    identity = (manifest.raw.get("connector_identity") or {}).get(key) or {}
    edge = manifest.raw.get("connector_edge") or {}
    networks = tuple(ipaddress.ip_network(str(cidr)) for cidr in edge.get("addresses") or [])
    canonical = edge.get("canonical_name")
    return Expected(
        server_name=None if identity.get("server_name") is None else str(identity["server_name"]),
        server_version=None if identity.get("server_version") is None else str(identity["server_version"]),
        networks=networks,
        canonical_name=None if canonical is None else str(canonical).rstrip(".").lower(),
    )


def token_for(key: str) -> str | None:
    """The bearer token for an authenticated initialize, from the environment."""
    return os.environ.get(TOKEN_ENV_PREFIX + key.upper()) or None


def _parse_initialize_body(content_type: str, body: bytes) -> dict | None:
    """Return the JSON-RPC message from a JSON or server-sent events body."""
    text = body.decode("utf-8", errors="replace")
    candidates: list[str] = []
    if "text/event-stream" in content_type:
        for line in text.splitlines():
            if line.startswith("data:"):
                candidates.append(line[5:].strip())
    else:
        candidates.append(text)
    for candidate in candidates:
        try:
            message = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(message, dict):
            return message
    return None


def mcp_response_problem(status: int, headers: dict[str, str], body: bytes,
                         expected: Expected) -> str | None:
    """Return None when the response is the expected server's initialize result, else the reason."""
    if status == 401:
        return ("HTTP 401: an authentication challenge is not proof that MHSB operates the endpoint; "
                "an authenticated initialize returning the expected serverInfo is required")
    if status != 200:
        return f"HTTP {status} is not an MCP initialize result"
    message = _parse_initialize_body(headers.get("content-type", ""), body)
    if message is None:
        return "HTTP 200 without a JSON-RPC message"
    result = message.get("result")
    if message.get("jsonrpc") != "2.0" or message.get("id") != INITIALIZE["id"] \
            or not isinstance(result, dict) or "protocolVersion" not in result:
        return "HTTP 200 without an initialize result carrying protocolVersion"
    info = result.get("serverInfo")
    if not isinstance(info, dict):
        return "initialize result without serverInfo"
    if expected.server_name is None or expected.server_version is None:
        return "no expected server identity recorded in catalog/manifest.yaml (connector_identity)"
    name, version = info.get("name"), info.get("version")
    if name != expected.server_name or str(version) != expected.server_version:
        return (f"serverInfo {name!r} {version!r} differs from the expected identity "
                f"{expected.server_name!r} {expected.server_version!r}")
    return None


def resolution_problem(host: str, addresses: set[str], canonical: str | None,
                       expected: Expected) -> str | None:
    """Return None when the resolved addresses and canonical name match the recorded edge."""
    if expected.networks:
        outside = sorted(a for a in addresses
                         if not any(ipaddress.ip_address(a.split("%")[0]) in n for n in expected.networks))
        if outside:
            return (f"{host} resolves to {', '.join(outside)}, outside the recorded edge "
                    f"(connector_edge.addresses)")
    if expected.canonical_name is not None:
        got = (canonical or host).rstrip(".").lower()
        if got != expected.canonical_name:
            return (f"{host} has canonical name {got}, not the recorded "
                    f"{expected.canonical_name} (connector_edge.canonical_name)")
    return None


def _canonical_name(host: str) -> str | None:
    try:
        return socket.gethostbyname_ex(host)[0]
    except OSError:
        return None


def check_url(url: str, expected: Expected, timeout: float = DEFAULT_TIMEOUT,
              context: ssl.SSLContext | None = None, token: str | None = None) -> CheckResult:
    """Run the resolution, edge, TLS and identity checks against one connector URL."""
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.hostname:
        return CheckResult(url, False, "url", "connector URL must be https with a host")
    host, port = parts.hostname, parts.port or 443
    path = parts.path or "/"
    try:
        addresses = {info[4][0] for info in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)}
    except socket.gaierror as exc:
        return CheckResult(url, False, "resolve", f"host does not resolve: {exc}")
    if not addresses:
        return CheckResult(url, False, "resolve", "host resolves to no address")
    canonical = _canonical_name(host) if expected.canonical_name is not None else None
    problem = resolution_problem(host, addresses, canonical, expected)
    if problem:
        return CheckResult(url, False, "edge", problem)
    context = context or ssl.create_default_context()
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    try:
        with socket.create_connection((host, port), timeout=timeout) as raw:
            with context.wrap_socket(raw, server_hostname=host) as tls:
                cert = tls.getpeercert() or {}
    except ssl.SSLCertVerificationError as exc:
        return CheckResult(url, False, "tls", f"certificate does not verify for {host}: {exc.verify_message}")
    except (ssl.SSLError, OSError) as exc:
        return CheckResult(url, False, "tls", f"TLS session failed: {type(exc).__name__}: {exc}")
    expires = cert.get("notAfter", "unknown")
    headers_out = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": MCP_PROTOCOL_VERSION,
    }
    if token:
        headers_out["Authorization"] = f"Bearer {token}"
    connection = http.client.HTTPSConnection(host, port, timeout=timeout, context=context)
    try:
        connection.request("POST", path, body=json.dumps(INITIALIZE).encode("utf-8"), headers=headers_out)
        response = connection.getresponse()
        body = response.read(65536)
        headers = {k.lower(): v for k, v in response.getheaders()}
    except (ssl.SSLError, OSError, http.client.HTTPException) as exc:
        return CheckResult(url, False, "mcp", f"request failed: {type(exc).__name__}: {exc}")
    finally:
        connection.close()
    problem = mcp_response_problem(response.status, headers, body, expected)
    if problem:
        return CheckResult(url, False, "identity", f"{problem} (token {'SET' if token else 'EMPTY'})")
    return CheckResult(url, True, "identity",
                       f"initialize returned {expected.server_name} {expected.server_version}; "
                       f"addresses within the recorded edge; certificate valid for {host} until {expires}")


def ga_connector_keys(manifest: Manifest) -> set[str]:
    """Connector keys bundled by at least one general availability plugin."""
    return {p.mcp for p in manifest.plugins if p.mcp is not None and p.tier == "ga"}


def run(manifest: Manifest, timeout: float = DEFAULT_TIMEOUT,
        keys: set[str] | None = None) -> dict[str, CheckResult]:
    """Check every connector (or the named keys) and return results by key."""
    selected = sorted(manifest.connectors) if keys is None else sorted(keys)
    return {key: check_url(manifest.connectors[key], expected_for(manifest, key), timeout=timeout,
                           token=token_for(key))
            for key in selected}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check the connector endpoints before a release.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    args = parser.parse_args(argv)
    manifest = load_manifest(args.root)
    ga = ga_connector_keys(manifest)
    blocking = 0
    for key, result in run(manifest, timeout=args.timeout).items():
        users = [p.name for p in manifest.plugins if p.mcp == key]
        tiers = sorted({manifest.plugin(n).tier for n in users})
        print(f"{result.render()} (connector {key}; plugins {', '.join(users) or 'none'}; "
              f"tiers {', '.join(tiers) or 'none'})")
        if not result.ok and key in ga:
            blocking += 1
    print(f"release_check: {len(manifest.connectors)} connector(s), {blocking} blocking failure(s)")
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
