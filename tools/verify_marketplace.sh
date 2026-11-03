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
echo "## unlisted pack must not install"
if claude plugin install mhsb-pack-family-law@mhsb-platform-plugins >/dev/null 2>&1; then
  echo "FAIL: hidden pack installed from the marketplace"; exit 1
else
  echo "OK: mhsb-pack-family-law is not installable from the marketplace"
fi
