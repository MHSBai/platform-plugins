#!/usr/bin/env python3
"""Release check for the remote MCP connectors bundled by connector plugins.

For every connector URL in catalog/manifest.yaml the check

1. resolves the host name,
2. opens a TLS session and verifies that the presented certificate chains to a
   trusted root and matches the host name, and
3. sends an MCP ``initialize`` request and requires an MCP response: either a
   JSON-RPC result carrying ``protocolVersion`` (JSON or server-sent events),
   or HTTP 401 with a ``WWW-Authenticate: Bearer`` challenge that names the
   protected resource metadata (MCP authorization, RFC 9728).

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
import json
import socket
import ssl
import sys
from dataclasses import dataclass
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


@dataclass(frozen=True)
class CheckResult:
    url: str
    ok: bool
    step: str
    detail: str

    def render(self) -> str:
        return f"{'PASS' if self.ok else 'FAIL'} {self.url} [{self.step}] {self.detail}"


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


def mcp_response_problem(status: int, headers: dict[str, str], body: bytes) -> str | None:
    """Return None when the HTTP response is an MCP response, else the reason."""
    if status == 401:
        challenge = headers.get("www-authenticate", "")
        if challenge.lower().startswith("bearer") and "resource_metadata" in challenge:
            return None
        return "HTTP 401 without a Bearer challenge naming resource_metadata"
    if status == 200:
        message = _parse_initialize_body(headers.get("content-type", ""), body)
        if message is None:
            return "HTTP 200 without a JSON-RPC message"
        result = message.get("result")
        if message.get("jsonrpc") == "2.0" and isinstance(result, dict) and "protocolVersion" in result:
            return None
        return "HTTP 200 without an initialize result carrying protocolVersion"
    return f"HTTP {status} is not an MCP response"


def check_url(url: str, timeout: float = DEFAULT_TIMEOUT,
              context: ssl.SSLContext | None = None) -> CheckResult:
    """Run the resolution, TLS and MCP checks against one connector URL."""
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
    connection = http.client.HTTPSConnection(host, port, timeout=timeout, context=context)
    try:
        connection.request("POST", path, body=json.dumps(INITIALIZE).encode("utf-8"), headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": MCP_PROTOCOL_VERSION,
        })
        response = connection.getresponse()
        body = response.read(65536)
        headers = {k.lower(): v for k, v in response.getheaders()}
    except (ssl.SSLError, OSError, http.client.HTTPException) as exc:
        return CheckResult(url, False, "mcp", f"request failed: {type(exc).__name__}: {exc}")
    finally:
        connection.close()
    problem = mcp_response_problem(response.status, headers, body)
    if problem:
        return CheckResult(url, False, "mcp", problem)
    return CheckResult(url, True, "mcp", f"HTTP {response.status} MCP response; certificate valid "
                                         f"for {host} until {expires}")


def ga_connector_keys(manifest: Manifest) -> set[str]:
    """Connector keys bundled by at least one general availability plugin."""
    return {p.mcp for p in manifest.plugins if p.mcp is not None and p.tier == "ga"}


def run(manifest: Manifest, timeout: float = DEFAULT_TIMEOUT,
        keys: set[str] | None = None) -> dict[str, CheckResult]:
    """Check every connector (or the named keys) and return results by key."""
    selected = sorted(manifest.connectors) if keys is None else sorted(keys)
    return {key: check_url(manifest.connectors[key], timeout=timeout) for key in selected}


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
