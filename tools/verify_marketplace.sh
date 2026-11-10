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
for name in $(python3 -c "import json;print(' '.join(p['name'] for p in json.load(open('.claude-plugin/marketplace.json'))['plugins']))"); do
  claude plugin install "${name}@mhsb-platform-plugins"
done
echo "## claude plugin list"; claude plugin list
for name in mhsb-firm-core mhsb-operations mhsb-lawmatics mhsb-clio; do
  echo "## inventory ${name}"; claude plugin details "$name" | grep -E 'Skills|MCP servers'
done
echo "## unlisted packs must not install"
for name in $(python3 -c "
import sys; sys.path.insert(0, 'tools')
from pathlib import Path
from manifest_lib import load_manifest
print(' '.join(p.name for p in load_manifest(Path('.')).plugins if p.tier != 'ga'))"); do
  if claude plugin install "${name}@mhsb-platform-plugins" >/dev/null 2>&1; then
    echo "FAIL: ${name} is not ga but installed from the marketplace"; exit 1
  fi
  echo "OK: ${name} is not installable from the marketplace"
done
