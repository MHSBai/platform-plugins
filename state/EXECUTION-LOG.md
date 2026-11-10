# Execution log: platform-plugins

Each entry records a step, the command that verifies it, and the captured output. Entries are appended in order; a resumed session continues at the first step whose output is absent.

## PP-1, Stage 1: repository, marketplace, manifest and lint

### Step 0. Resume check (2026-11-03)

Command: `git log --oneline; ls state/`

Output: one prior commit (`080d165 docs: repository purpose`); no state directory existed. Stage 1 starts from the beginning on branch `cloud/pp1-repository-marketplace` created from `main`.

### Step 1. Specification read

Read in full from MHSBai/mhsb-firm-service, docs/spec/: Design v2.1 (Sections 4, 5, 7, 8, 9, 12, and the remainder for context) and Catalog v2.1 (Sections 1 and 3, and the remainder for context). The pilot firm identifiers that appear in those documents were collected for the zero-hit check in Step 9; they are not reproduced in this public repository.

### Step 2. Reference documentation fetch (gate: all fetches failed, stop)

Command: `curl -sSL -o <file> -w '%{http_code}' <url>` for each URL.

```
200 https://claude.com/docs/plugins/overview
200 https://code.claude.com/docs/en/plugins/create-marketplace
200 https://claude.com/docs/plugins/platform-support
200 https://claude.com/docs/plugins/submit
200 https://code.claude.com/docs/en/plugins/manifest-reference
```

Supplementary pages read because the five pages link to them for field rules: marketplace-reference, skills (frontmatter reference), plugins/components. Gate not triggered. Deltas between documentation and design are recorded in docs/decisions/0001-documentation-deltas.md.

### Step 3. Manifest and generator (checkpoint C1)

Command: `python tools/gen_manifest.py --check && python tools/gen_manifest.py --counts`

```
generated files current
exit=0
| Combination | Platform | Variants | Breakdown | Commands (min) | Commands (max) |
|---|---|---|---|---|---|
| core-only | none | 1 | 8 | 8 | 8 |
| connected | mhsb-lawmatics | 298 | 8 + 11 + 2 + 0 | 21 | 21 |
| connected | mhsb-clio | 298 | 8 + 11 + 3 + 0 | 22 | 22 |
| connected | mhsb-mycase | 298 | 8 + 11 + 0 + 0 | 19 | 19 |
Supported combinations enumerated: 895.
Maximum commands in any combination: 22.
Lint cap: 24. Design figure: 22.
```

Result: pass. At most 22 commands in any of 895 combinations. Commit 6649d37.

### Step 4. Lint and tests (checkpoint C2)

Commands: `python tools/lint.py; echo exit=$?`, `python tools/lint.py --release; echo exit=$?`, `python -m pytest -q`

```
lint: 14 rules, 0 error(s), 12 warning(s)
exit=0
lint: 14 rules, 12 error(s), 0 warning(s)
exit=1
56 passed in 33.19s
```

Result: pass. The twelve warnings are the synthetic adoption records on the two general availability packs (decision 0002); `--release` fails on them by design. Commit b5710c5.

Reading level per skill body (Flesch-Kincaid grade; limits 9 operational, 12 document):

```
mhsb-clio/budget-vs-actual operational 3.9
mhsb-clio/production operational 3.8
mhsb-clio/timekeeper-hours operational 4.1
mhsb-firm-core/ai-policy-draft document 5.2
mhsb-firm-core/ai-training operational 3.3
mhsb-firm-core/ask-mhsb operational 3.4
mhsb-firm-core/before-i-paste operational 4.1
mhsb-firm-core/explain-this operational 3.4
mhsb-firm-core/follow-up operational 3.0
mhsb-firm-core/meeting-notes operational 3.5
mhsb-firm-core/start operational 2.8
mhsb-lawmatics/form-protections operational 4.5
mhsb-lawmatics/pipeline-health operational 4.4
mhsb-operations/brief operational 3.7
mhsb-operations/check-setup operational 4.3
mhsb-operations/checklist operational 4.1
mhsb-operations/consult-prep document 4.1
mhsb-operations/dates operational 3.9
mhsb-operations/hygiene operational 4.5
mhsb-operations/intake-triage operational 4.4
mhsb-operations/letter document 4.7
mhsb-operations/matter-status document 4.8
mhsb-operations/on-brand operational 4.0
mhsb-operations/report document 4.7
```

### Step 5. Marketplace validation (checkpoint C3)

`claude` 2.1.317 (Claude Code) is present in the sandbox, so the documented command was used rather than a substitute script.

Command: `tools/verify_marketplace.sh` (throwaway `CLAUDE_CONFIG_DIR`; output filtered to result lines)

```
## claude plugin validate . --strict
√ Validation passed
## claude plugin marketplace add ./
Adding marketplace…√ Successfully added marketplace: mhsb-platform-plugins (declared in user settings)
## claude plugin list
    Version: 0.1.0   Status: √ enabled   (seven listed plugins)
## inventory mhsb-firm-core
  Skills (8)  ai-policy-draft, ai-training, ask-mhsb, before-i-paste, explain-this, follow-up, meeting-notes, start
## inventory mhsb-operations
  Skills (11)  brief, check-setup, checklist, consult-prep, dates, hygiene, intake-triage, letter, matter-status, on-brand, report
  MCP servers (1)  mhsb-firm
## inventory mhsb-lawmatics
  Skills (2)  form-protections, pipeline-health
  MCP servers (1)  mhsb-lawmatics
## inventory mhsb-clio
  Skills (3)  budget-vs-actual, production, timekeeper-hours
  MCP servers (1)  mhsb-clio
## unlisted pack must not install
OK: mhsb-pack-family-law is not installable from the marketplace
exit=0
```

Each of the seventeen plugin directories also passes `claude plugin validate plugins/<name> --strict`. Result: pass. Commit 4cb55e7.

### Step 6. CI present (checkpoint C4)

Command: `python -c "import yaml; print(sorted(yaml.safe_load(open('.github/workflows/ci.yml'))['jobs']))"`

```
['agent-scan', 'lint', 'tests']
```

Actions are pinned by commit (checkout v5.0.0 08c6903, setup-python v5.6.0 a26af69, setup-uv v6.4.3 e92bafb). The agent-scan job runs only when the repository is public and reports `SNYK_TOKEN: SET` or `EMPTY`; flags verified with `uvx snyk-agent-scan@0.5.17 scan --help`. The workflow has not yet run on GitHub; its first run is on the pull request. Result: pass (present). Commit bbbde2d.

### Step 7. Branch protection

Not attempted; requires repository administration. Exact commands are in HANDOFF.md items 1 to 3.

### Step 8. Documentation deltas

Recorded in docs/decisions/0001-documentation-deltas.md (13 deltas), 0002 (adoption records in general availability packs) and 0003 (lint semantics).

### Step 9. Pilot firm identifier check (checkpoint C5)

The identifiers read in the Design and Catalog (ten tokens: eight pilot firm codes, one brand name, one host name) were written to a list in the session scratchpad, outside the repository.

Command: `grep -rnIiwF -f <scratchpad list> --exclude-dir=.git --exclude-dir=__pycache__ . | wc -l`

```
identifiers: 10
hits: 0
```

A case-sensitive substring search without word boundaries, excluding the two-letter and three-letter common-word codes, also returned 0. Result: pass.

### Step 10. Push and pull request

Command: `git push -u origin cloud/pp1-repository-marketplace`

```
 * [new branch]      cloud/pp1-repository-marketplace -> cloud/pp1-repository-marketplace
```

Draft pull request opened: https://github.com/MHSBai/platform-plugins/pull/1 ("Stage 1: repository, marketplace, manifest and lint"). Not merged. Outcome: DONE PP-1.

### Step 11. Review response, 2026-11-10 (PP1-M1, PP1-L1, PP1-L3)

Changes: agent-scan fails on push (main and `v*` tags) when `SNYK_TOKEN` is empty and is removed from the required contexts in HANDOFF item 1 until item 2 is done (PP1-M1); `tools/verify_marketplace.sh` asserts the "not found in marketplace" message for every pilot and hidden pack (PP1-L1); the generator deduplicates keywords (PP1-L3). The other findings are owner decisions and are listed in the pull request reply.

```
generated files current
lint: 14 rules, 0 error(s), 12 warning(s)
57 passed
√ Validation passed
OK: <each of 10 pilot and hidden packs> not found in marketplace
verify exit=0
```

### Step 12. Fix session FIX-PP-STACK-A, 2026-11-10 (PP1-H1, PP1-M1, PP1-M3, PP1-L2, PP1-L5)

Each applied finding has a reproduction commit before its fix.

- PP1-H1: the connector host resolved, but the TLS handshake failed (`SSLEOFError`). `tools/release_check.py` and lint rule L16 were committed first; at that commit `lint.py --release` reported L16 for the three connector plugins. Fix: `mhsb-operations`, `mhsb-lawmatics` and `mhsb-clio` are held at tier pilot; HANDOFF item 8 records the DNS and hosting step as the condition for release.
- PP1-L2: L16 also requires `privacyPolicyUrl` and `termsOfServiceUrl` on any ga connector plugin; the generator emits them from `defaults.connector_listing` once the documents exist.
- PP1-M1: `tests/test_ci.py` failed on the previous workflow (the job concluded success with the scan skipped). Fix: an `agent-scan-token` job; `agent-scan` is skipped on pull requests without the token and fails on push.
- PP1-M3: `tests/test_licenses.py` failed (notices hand-copied, no buildout grant). Fix: notices generated from one template; buildout grant for `mhsb-mycase`; HANDOFF item 9 `[counsel review]`.
- PP1-L5: "repository owner" in HANDOFF.md and decision 0002.

```
gen_manifest --check     generated files current
gen_manifest --counts    895 combinations, maximum 22, catalog/counts.md identical
lint                     15 rules, 0 error(s), 12 warning(s)
lint --release           12 error(s), all L11 synthetic adoption (decision 0002; resolved by Stage 9, PP1-M2)
release_check            3 connector(s), 0 blocking failure(s) (no connector plugin at tier ga)
pytest                   85 passed
verify_marketplace.sh    4 listed plugins installed; 13 unlisted plugins refused with "not found in marketplace"
claude plugin validate . --strict   passed; 17 of 17 plugins pass --strict
```
