#!/usr/bin/env bash
# Re-runnable marketplace load check. Uses a throwaway Claude configuration
# directory so that the caller's own settings are not modified.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cfg="$(mktemp -d)"
trap 'rm -rf "$cfg"' EXIT
export CLAUDE_CONFIG_DIR="$cfg"
cd "$root"
echo "## claude --version"; claude --version
echo "## claude plugin validate . --strict"; claude plugin validate . --strict
echo "## claude plugin marketplace add ./"; claude plugin marketplace add ./
listed=$(python3 -c "import json;print(' '.join(p['name'] for p in json.load(open('.claude-plugin/marketplace.json'))['plugins']))")
for name in $listed; do
  claude plugin install "${name}@mhsb-platform-plugins"
done
echo "## claude plugin list"; claude plugin list
for name in $listed; do
  echo "## inventory ${name}"
  claude plugin details "$name" | grep -E 'Skills|MCP servers' || echo "no skills and no MCP servers"
done
echo "## unlisted plugins must not install"
unlisted=$(python3 -c "import sys; sys.path.insert(0, 'tools'); from manifest_lib import load_manifest; from pathlib import Path; print(' '.join(p.name for p in load_manifest(Path('.')).plugins if p.tier != 'ga'))")
for name in $unlisted; do
  if out=$(claude plugin install "${name}@mhsb-platform-plugins" 2>&1); then
    echo "FAIL: ${name} installed from the marketplace"; exit 1
  fi
  if ! grep -qF "\"${name}\" not found in marketplace \"mhsb-platform-plugins\"" <<<"$out"; then
    echo "FAIL: ${name} install failed for another reason: ${out}"; exit 1
  fi
  echo "OK: ${name} not found in marketplace"
done
