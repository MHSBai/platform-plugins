#!/usr/bin/env bash
# Release gate of MHSBai/platform-plugins (Design v2.1 Section 12; Prompts v2.0 Prompt 12 step 4).
# Documented in docs/release.md. It fails on any red: exit 0 only when every item passes.
#
# Usage:
#   tools/release-gate.sh             every item, including the firm service gate (P10)
#   tools/release-gate.sh --own-only  this repository's items only (the service gate calls this);
#                                     the result is PARTIAL and the exit status 3 even when all pass
#   tools/release-gate.sh --self-test the tests of this script
#
# PLATFORM_SERVICE_DIR (default ../mhsb-firm-service) names the firm service checkout, whose own
# gate runs the isolation suite, the log-leak test, the custody tests, the drill evidence and the
# controls.md freshness items. A missing checkout is a FAIL, never a skip. PYTHON names the
# interpreter (default .venv/bin/python when present, else python3) with requirements-dev.txt
# installed. P9 reads each upstream LICENSE from raw.githubusercontent.com; nothing else here uses
# the network, reads a credential or calls a model.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 2
ROOT="$(pwd)"
MODE="full"
if [ -x "$ROOT/.venv/bin/python" ]; then PY="${PYTHON:-$ROOT/.venv/bin/python}"; else PY="${PYTHON:-python3}"; fi
case "${1:-}" in
  "") ;;
  --own-only) MODE="own" ;;
  --self-test) exec "$PY" -m pytest -q tests/test_release_gate.py ;;
  *) echo "usage: tools/release-gate.sh [--own-only|--self-test]" >&2; exit 2 ;;
esac
SERVICE="${PLATFORM_SERVICE_DIR:-$ROOT/../mhsb-firm-service}"

declare -a RESULTS=()
status=0
mark() {  # name, exit code
  if [ "$2" -eq 0 ]; then RESULTS+=("PASS $1"); else RESULTS+=("FAIL $1"); status=1; fi
  echo "${RESULTS[-1]}"
}
step() {  # name, command...
  local name="$1"; shift
  echo "== $name"
  "$@"
  mark "$name" $?
}

echo "release gate: $(git rev-parse --short HEAD) on $(git rev-parse --abbrev-ref HEAD), $(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "== P0 committed tree (a release is a commit)"
dirty="$(git status --porcelain --untracked-files=no | wc -l)"
echo "  uncommitted tracked paths: $dirty"
[ "$dirty" -eq 0 ]; mark "P0 committed tree" $?

step "P1 generated files current" "$PY" tools/gen_manifest.py --check
step "P2 lint" "$PY" tools/lint.py
step "P3 release lint (adoption records, connector release check, listing URLs)" "$PY" tools/lint.py --release
step "P4 unit tests" "$PY" -m pytest -q
step "P5 pack evals" "$PY" tools/pack_evals.py
step "P6 routing suite (deterministic)" "$PY" tools/routing_check.py
step "P7 skill evals (deterministic reference transcripts)" "$PY" tools/skill_evals.py
step "P8 model eval release gate (every routing and skill case passes on the current text)" "$PY" tools/model_evals.py --check-release
step "P9 PROVENANCE and license gate (ledger, notices, upstream license hashes)" "$PY" tools/license_gate.py --upstream

echo "== P10 firm service items (isolation, log leak, custody, drills, controls.md, service provenance)"
if [ "$MODE" = "own" ]; then
  echo "  not run: --own-only"; RESULTS+=("PARTIAL P10 firm service items (not run: --own-only)")
elif [ -x "$SERVICE/tools/release-gate.sh" ]; then
  echo "  firm service head: $(git -C "$SERVICE" rev-parse --short HEAD) ($(git -C "$SERVICE" rev-parse --abbrev-ref HEAD))"
  PLATFORM_PLUGINS_DIR="$ROOT" "$SERVICE/tools/release-gate.sh" --own-only
  r=$?; [ "$r" -eq 3 ] && r=0
  mark "P10 firm service items" "$r"
else
  echo "  problem: no firm service checkout with tools/release-gate.sh at $SERVICE"
  mark "P10 firm service items" 1
fi

echo "== summary"
printf '%s\n' "${RESULTS[@]}"
if [ "$status" -ne 0 ]; then echo "RELEASE GATE: RED"; exit 1; fi
if [ "$MODE" = "own" ]; then echo "RELEASE GATE: PARTIAL (own items pass; the firm service items were not run)"; exit 3; fi
echo "RELEASE GATE: GREEN"
