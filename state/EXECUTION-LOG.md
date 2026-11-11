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

### Step 13. Fix session FIX2-PP-STACK-A, 2026-11-10 (PP1-N1 to PP1-N4)

- PP1-N1: reproduced by `tests/test_release_check.py::test_live_mcp_endpoint_passes[auth]`, which passed for a static 401 on 127.0.0.1, and by `check_url` collecting the resolved addresses without comparing them. Fix: `connector_identity` and `connector_edge` in `catalog/manifest.yaml`; the check compares every resolved address with the edge, rejects any 401 and requires an authenticated `initialize` returning the recorded `serverInfo`. Against the live host, all three connectors now fail at the edge step.
- PP1-N2: `ci.yml` ran `lint.py --release` on `v*` tags only. Fix: a `release-gate` job on every event.
- PP1-N3: a fork pull request skipped `agent-scan`, which a required check counts as success. Fix: the job always runs and fails with the reason whenever no scan ran.
- PP1-N4: two questions for counsel in HANDOFF item 9; no license text changed.

```
gen_manifest --check     generated files current
gen_manifest --counts    895 combinations, maximum 22
lint                     15 rules, 0 error(s), 12 warning(s)
lint --release           12 error(s), all L11 synthetic adoption (cleared by #3, PP1-M2)
pytest                   97 passed
release_check            3 connector(s), 3 edge failures, 0 blocking (all pilot)
verify_marketplace.sh    13 unlisted plugins refused with "not found in marketplace"
claude plugin validate . --strict   passed
```

## PP-2, Stage 2: harvest, provenance and adapted sources

### Step 0. Resume check and stacking (2026-11-03)

Command: `git ls-remote --heads origin; git log --oneline origin/main`

Output: `main` holds only `080d165 docs: repository purpose`; the Stage 1 branch `cloud/pp1-repository-marketplace` (head 48bc51a) holds the skeleton and its pull request is open, not merged. No PP-2 entry existed in this log. Branch `cloud/pp2-harvest` was created from `cloud/pp1-repository-marketplace`. The session harness named a different branch (`roo/wizardly-mendel-c744jl`); the task's branch name was used, as in Stage 1 and Stage 3.

### Step 1. Clone the seventeen repositories

Command: `git -c core.hooksPath=/dev/null clone --no-checkout https://github.com/OWNER/REPO harvest/OWNER_REPO/repo`, then `checkout` with hooks disabled; one empty directory per repository.

Output: all seventeen cloned; none unreachable. Heads recorded in `harvest/LEDGER.yaml`. No build tool, install script or package manager was run in any clone; license files were hashed and classified with a scratchpad script run under `python3 -I`.

### Step 2. Incident: pytest collection imported clone modules

The first `python -m pytest -q` after the clones existed had no `testpaths` setting, so pytest discovery walked into `harvest/` and imported test modules and three `conftest.py` files from the clones (RosenAdvertising clio-mcp and lawmatics-mcp, snyk agent-scan) before stopping with 34 collection errors. Module-level code of those files and of the packages they import therefore ran once inside this container's pytest process. No fixture or test body ran (collection was interrupted); the module-level code inspected sets environment variables for its own process and defines fixtures; the process exited. No secret is held in the repository or was set for the session. Remedy: `pytest.ini` pins discovery to `tests/` with `norecursedirs = harvest`; the `__pycache__` directories produced in the clones were deleted; `git status --ignored` in each clone is clean. This breached the instruction never to run code from a clone and is recorded here for that reason.

### Step 3. Ledger, license gate, adapted files (checkpoints: ledger complete, license gate green, headers)

Commit 6735a61. 32 adapted files (14 from claude-for-legal, 13 from knowledge-work-plugins, 2 from frblaw/ai-policy-templates, 3 from AssemblyLine), each with the modification notice and a PROVENANCE row. `tools/license_gate.py` (G1 to G6) with negative tests in `tests/test_license_gate.py`; CI step added to the lint job. The dash rule now skips the git-ignored clones and still lints `harvest/LEDGER.yaml`.

### Step 4. Element checklists (checkpoint: one per restricted form)

Commit 6ac3d62. Seven checklists in `catalog/element-checklists/`, written without any form open; comparison against each current edition and the similarity review are pending. Consent request drafts and the terms record are in the private repository (mhsb-firm-service `docs/consents/`), not sent.

### Step 5. Checkpoint run

```
$ ledger completeness
entries: 17 incomplete: []
status: {'ADAPT': 4, 'BENCHMARK': 6, 'VENDOR': 5, 'EVALUATED': 1, 'TOOL': 1}
license_status: {'ALLOWED': 16, 'ABSENT': 1}
$ python tools/license_gate.py --clones
license gate: 17 ledger entries, 32 PROVENANCE rows, 0 failure(s)
$ python tools/license_gate.py
license gate: 17 ledger entries, 32 PROVENANCE rows, 0 failure(s)
$ adapted files with notice
32
$ PROVENANCE rows by license
Apache-2.0: 27
CC0-1.0: 2
MIT: 3
$ element checklists
7
$ python tools/gen_manifest.py --check
generated files current
exit 0
$ python tools/lint.py
lint: 14 rules, 0 error(s), 12 warning(s)
$ python -m pytest -q
70 passed in 44.85s
$ denylist grep
identifiers: 15
hits: 0
$ tracked files under harvest
harvest/LEDGER.yaml
```

agent-scan: wired by Stage 1 in `.github/workflows/ci.yml` (job `agent-scan`, public repository only, SNYK_TOKEN reported as SET or EMPTY); unchanged in this stage. Its first GitHub run is on the pull request.

### Step 6. Incident record completed (review PP2-L2, 2026-11-10)

What was captured at the time of the Step 2 incident is limited to the tail of the pytest output; the full collection list was not saved and the collection is not reproduced, because reproducing it would run harvested code again. Captured lines:

```
ERROR harvest/lasso-security_mcp-gateway/repo/tests/test_security_scanner.py
ERROR harvest/lasso-security_mcp-gateway/repo/tests/xetrack_tracing_test.py
ERROR harvest/snyk_agent-scan/repo/tests - ModuleNotFoundError: No module nam...
!!!!!!!!!!!!!!!!!!! Interrupted: 34 errors during collection !!!!!!!!!!!!!!!!!!!
34 errors in 1.53s
```

Directories that held bytecode caches newer than the ledger before the caches were deleted (`find harvest -name __pycache__ -newer harvest/LEDGER.yaml`): each marks Python code that was compiled for import, and therefore at least partly executed:

```
harvest/RosenAdvertising_clio-mcp/repo/tests/__pycache__
harvest/LegalMate_hyacinth/repo/test/__pycache__
harvest/SuffolkLITLab_docassemble-AssemblyLine/repo/docassemble/AssemblyLine/__pycache__
harvest/RosenAdvertising_mycase-mcp/repo/tests/__pycache__
harvest/lasso-security_mcp-gateway/repo/mcp_gateway/security_scanner/__pycache__
harvest/lasso-security_mcp-gateway/repo/mcp_gateway/__pycache__
harvest/lasso-security_mcp-gateway/repo/mcp_gateway/plugins/tracing/__pycache__
harvest/lasso-security_mcp-gateway/repo/mcp_gateway/plugins/guardrails/__pycache__
harvest/lasso-security_mcp-gateway/repo/mcp_gateway/plugins/__pycache__
harvest/lasso-security_mcp-gateway/repo/tests/__pycache__
```

Packages installed in the virtual environment that ran pytest (`.venv/bin/pip freeze`, unchanged since): attrs 26.1.0, iniconfig 2.3.1, jsonschema 4.26.0, jsonschema-specifications 2025.9.1, packaging 26.3, pluggy 1.7.0, pytest 8.3.4, PyYAML 6.0.3, referencing 0.37.0, rpds-py 2026.9.1, typing_extensions 4.16.0. No harvested package was installed; imports of the clones' own packages resolved only through pytest's rootdir insertion into `sys.path`.

Correction to Step 2: besides module-level code, pytest hooks defined in any `conftest.py` that imported successfully (for example `pytest_addoption` and `pytest_collection_modifyitems` in snyk/agent-scan's) run during collection. The snyk/agent-scan error line shows a `ModuleNotFoundError` for that test directory, which indicates its conftest failed to import, but whether any of its hooks registered before the error cannot be established from the captured output. RosenAdvertising/clio-mcp's conftest rewrites `HOME` for its own process and imports its package; its `tests/live_smoke_test.py` and `tests/smoke_test.py` match the default pattern and put the clone root on `sys.path`. The bytecode caches for that test directory show its modules were compiled. None of the conftest files read as data contains module-level network or credential access. No secret was present in the session. The remediation (Step 2) stands.

### Step 7. Fix session FIX-PP-STACK-A, 2026-11-10 (PP2-M1 completed; PP2-L1 to PP2-L6 verified)

`cloud/pp1-repository-marketplace` (PP1 fixes) merged into this branch. Commit 8c351e7 had already added the per-plugin `LICENSES/` copies and gate rule G7. Under the fix contract, two parts of PP2-M1 remained: a NOTICE excerpt inside each plugin, and a rule in `tools/lint.py`. Lint rule L17 was committed first and reported five errors (no plugin shipped a NOTICE excerpt); the five `plugins/<name>/NOTICE.md` excerpts followed. A throwaway marketplace install showed `NOTICE.md` and `LICENSES/` in the plugin cache.

```
license_gate.py            17 ledger entries, 32 PROVENANCE rows, 0 failure(s)
license_gate.py --clones   clones present and re-hashed: 0 of 17; 0 failure(s) (clean checkout)
license_gate.py --upstream upstream LICENSE files compared: 17; 0 failure(s)
lint.py                    16 rules, 0 error(s), 12 warning(s)
```

## PP-9, Stage 9: twelve pack fragments and pack evals

### Step 0. Resume check and base (2026-11-03)

Command: `git fetch origin --prune; git branch -r`; pull requests listed through the GitHub tools.

Output: platform-plugins `main` holds only `080d165`; Stage 1 (MHSBai/platform-plugins#1, `cloud/pp1-repository-marketplace`) and Stage 2 (MHSBai/platform-plugins#2, `cloud/pp2-harvest`) are open and unmerged. No PP-9 entry existed in this log. Branch `cloud/pp9-pack-fragments` was created from `cloud/pp2-harvest` (head b6832e9), the most recent open `cloud/pp*` branch. The session harness named `roo/inspiring-cannon-bz57zy`; the task's branch name was used, as in Stages 1 to 3.

Stage 3 gate: mhsb-firm-service `main` has no schema; the open Stage 3 branch `cloud/pp3-firm-profile-v2` (head bfcddee, MHSBai/mhsb-firm-service#1) holds `firm_profile/schemas/fragment.schema.json`. The prompt names `schemas/fragment.schema.json`; the file exists under `firm_profile/schemas/`, so the gate "Stage 3 missing" did not trigger. Recorded in decision 0004.

### Step 1. Reading

Design v2.1 Sections 4, 5, 7; Catalog v2.1 Sections 2, 3 and 7; the fragment schema; the Stage 3 report registry and cross rules (`firm_profile/catalog.py`, `rules.py`); the seven element checklists; the canonical dictionary (stage identifiers); the Lawmatics Product Catalog (PI, EP, CRIM, IMM and BK pipeline stage names). Catalog 7 lists "the per-platform date-field inventory (a gate on Stage 9)"; no inventory exists in either repository. The fragments name date categories only and map no platform field; the eval cases supply a synthetic mapping. Recorded in HANDOFF.md as an open item, not treated as a stop because the prompt sets no gate on it.

### Step 2. Fragments (checkpoint: twelve fragments validate)

Twelve `fragment/fragment.yaml` files rewritten to the Stage 3 schema; twelve `fragment/adoption.yaml` records; template identifiers renamed to the schema pattern; PI and business templates moved from synthetic records to `PENDING ADOPTION`; AssemblyLine intake blocks (PI, civil, business) keep their 4(b) headers and map one-to-one onto the fragment question ids. Six `CO-DESIGN.md` files on the hidden packs. Manifest: PI and business at `tier: pilot`, `catalog_tier: ga` (decision 0004). Schema vendored as `tools/schemas/fragment.schema.json` (SHA-256 9d537e09...ff2ac, identical to the service copy).

Command: `python tools/validate_fragments_service.py --service ../mhsb-firm-service` (service at bfcddee)

```
PASS schema, rules PASS: plugins/mhsb-pack-bankruptcy-consumer/fragment/fragment.yaml
PASS schema, rules HELD (XR-GA-ADOPTION, XR-STATUTORY): plugins/mhsb-pack-business-transactional/fragment/fragment.yaml
PASS schema, rules PASS: plugins/mhsb-pack-civil-litigation/fragment/fragment.yaml
PASS schema, rules PASS: plugins/mhsb-pack-criminal-defense/fragment/fragment.yaml
PASS schema, rules PASS: plugins/mhsb-pack-employment-plaintiff/fragment/fragment.yaml
PASS schema, rules PASS: plugins/mhsb-pack-estate-probate/fragment/fragment.yaml
PASS schema, rules PASS: plugins/mhsb-pack-family-law/fragment/fragment.yaml
PASS schema, rules PASS: plugins/mhsb-pack-immigration/fragment/fragment.yaml
PASS schema, rules PASS: plugins/mhsb-pack-landlord-tenant-consumer/fragment/fragment.yaml
PASS schema, rules HELD (XR-GA-ADOPTION, XR-STATUTORY): plugins/mhsb-pack-personal-injury/fragment/fragment.yaml
PASS schema, rules PASS: plugins/mhsb-pack-real-estate/fragment/fragment.yaml
PASS schema, rules PASS: plugins/mhsb-pack-workers-compensation/fragment/fragment.yaml
fragments: 12, schema and rule failures: 0
```

HELD: the two GA fragments carry no adopter, so the Stage 3 cross rules `XR-GA-ADOPTION` and `XR-STATUTORY` fire as designed until Stage 11 records an adoption. Schema validation passes for all twelve.

### Step 3. Pack evals (checkpoint: GA and pilot evals green)

`evals/packs/`: 4 cases for each of the 6 GA and pilot fragments (dates with a statutory and a firm-set category, intake-triage with sensitive-variant re-scoring, checklist, brief pack view), one extra PI dates case, and 3 family law outreach-gate cases. Criminal defense and real estate have no statutory category in the Catalog; their dates cases assert its absence (decision 0004).

Command: `python tools/pack_evals.py`

```
pack evals: 28 cases, 28 passed, 0 failed
```

### Step 4. Checkpoint run

```
$ python tools/validate_fragments_service.py --service ../mhsb-firm-service
fragments: 12, schema and rule failures: 0
exit 0
$ python tools/pack_evals.py | tail -1
pack evals: 28 cases, 28 passed, 0 failed
exit 0
$ ls plugins/mhsb-pack-*/CO-DESIGN.md | wc -l
6
$ python tools/gen_manifest.py --check
generated files current
exit 0
$ diff <(git show HEAD:catalog/counts.md | sed -n 1,17p) <(sed -n 1,17p catalog/counts.md)
combination counts table unchanged
$ python tools/gen_manifest.py --counts | sed -n 7,16p
| Combination | Platform | Variants | Breakdown | Commands (min) | Commands (max) |
|---|---|---|---|---|---|
| core-only | none | 1 | 8 | 8 | 8 |
| connected | mhsb-lawmatics | 298 | 8 + 11 + 2 + 0 | 21 | 21 |
| connected | mhsb-clio | 298 | 8 + 11 + 3 + 0 | 22 | 22 |
| connected | mhsb-mycase | 298 | 8 + 11 + 0 + 0 | 19 | 19 |

Supported combinations enumerated: 895.
Maximum commands in any combination: 22.
Lint cap: 24. Design figure: 22.
$ python tools/lint.py | tail -1
lint: 15 rules, 0 error(s), 0 warning(s)
exit 0
$ python tools/lint.py --release | tail -1
lint: 15 rules, 0 error(s), 0 warning(s)
$ python tools/license_gate.py
license gate: 17 ledger entries, 32 PROVENANCE rows, 0 failure(s)
$ python -m pytest -q | tail -1
97 passed in 64.77s (0:01:04)
$ grep -rnIiwF -f <private denylist> --exclude-dir=.git --exclude-dir=harvest --exclude-dir=.venv . | wc -l
identifiers: 17
hits (case-insensitive, word): 0
hits (two short codes, case-sensitive, word): 0
$ dash check U+2014 U+2013 U+2012 in changed and new files
0
```

Marketplace load check, rerun because the listing lost the two held packs: `bash tools/verify_marketplace.sh` passed `claude plugin validate . --strict`, installed the five listed plugins in a throwaway configuration, and refused the hidden family law pack.

The plugin tier rows of `catalog/counts.md` changed for the two held packs (ga to pilot); the combination counts table above it is unchanged.

### Step 5. Review XREVIEW-PP-STACK-A findings PP3-L1 and PP3-L2 (2026-11-10)

PP3-L1: `tools/schemas/fragment.schema.source.json` records the source commit and sha256 of the vendored schema; L15 now fails on a hash difference (test `test_l15_vendored_schema_hash_drift`). Re-vendoring from the merged Stage 3 commit waits for that pull request; HANDOFF.md PP-9 item 8.

PP3-L2: `tools/verify_marketplace.sh` now attempts to install every manifest plugin whose tier is not ga and fails if any installs.

```
$ bash tools/verify_marketplace.sh
Validation passed
OK: 12 of 12 non-ga packs are not installable from the marketplace (personal injury, business and transactional, estate planning and probate, criminal defense, civil litigation, real estate, family law, immigration, employment plaintiff, bankruptcy consumer, workers' compensation, landlord-tenant and consumer)
exit 0
$ python -m pytest -q
98 passed
$ python tools/lint.py
lint: 15 rules, 0 error(s), 0 warning(s)
$ python tools/pack_evals.py
pack evals: 28 cases, 28 passed, 0 failed
$ python tools/validate_fragments_service.py --service ../mhsb-firm-service
fragments: 12, schema and rule failures: 0
```

### Step 6. Fix session FIX-PP-STACK-A, 2026-11-10 (PP3-L1 and PP3-L2 verified; fixes from Stages 1 and 2 merged)

`cloud/pp2-harvest`, carrying the PP1 and PP2 fixes, was merged into this branch. In the `tools/verify_marketplace.sh` conflict the Stage 1 loop was kept: it covers every plugin whose tier is not ga (the three connector plugins, the two held packs, the four pilot packs and the six hidden packs) and requires the exact "not found in marketplace" refusal (PP3-L2). The 919c3a9 loop required only a failed install. PP3-L1: the vendored schema hash `9d537e09...` equals the file at service commit `bfcddee`; L15 compares it with `tools/schemas/fragment.schema.source.json`. The Stage 3 pull request in the service repository is still open on 2026-11-10, so re-vendoring stays in HANDOFF (PP-9 item 8).

## PP-8, Stage 8: skills to final text, routing suite and evals

### Step 0. Resume check and base (2026-11-04)

Command: `git ls-remote origin; git log --oneline origin/main`

Output: `main` holds only `080d165`; `cloud/pp1-repository-marketplace`, `cloud/pp2-harvest` and `cloud/pp9-pack-fragments` are open and unmerged, each stacked on the previous one. No PP-8 entry existed in this log. Branch `cloud/pp8-skills-evals` was created from `cloud/pp9-pack-fragments` (head adfce89), the most recent open `cloud/pp*` branch. Stage 1 skeleton present; Stage 2 adapted sources present (32 files), so the skills were written against them. The session harness named `roo/sleepy-hopper-sgigzr`; the task's branch name was used, as in earlier stages.

### Step 1. Reading

Design v2.1 Sections 4, 5, 6, 12 (and the remainder for context); Catalog v2.1 Section 1 (and Sections 2, 3 for report identifiers and fragment content); the 24 skill skeletons and their adapted references; capability-forge `skills/mhsb-brand/SKILL.md` (voice, punctuation, banned phrases). No skill-creator skill exists under capability-forge `skills/` or `plugins/`; recorded, not a stop. The PI sample firm in mhsb-firm-service (`firm_profile/samples/pi_lawmatics.json`, synthetic) supplies the example firm. No docs/decisions record verifies California SB 574 against the chaptered statute, so no SB 574 text was written.

### Step 2. Model identifiers and key

`ANTHROPIC_API_KEY`: EMPTY. `curl -sSL https://platform.claude.com/docs/en/about-claude/models` returned 200 (redirect to /docs/en/models/overview) and lists `claude-sonnet-5-5` and `claude-opus-5-5` as the current Sonnet and Opus; recorded in `evals/model-config.yaml` with prices of 2/10 and 4/20 US dollars per million input/output tokens.

### Step 3. Build

Triggers extended in `catalog/manifest.yaml`; `evals/routing/phrases.yaml` (60 phrases, expected skill per command set); `tools/routing_check.py`; `evals/skills/refusals.yaml` (exact sentences); `tools/skill_evals.py` (pass bar of Design Section 12); `tools/model_evals.py` and `evals/model-config.yaml`; 24 SKILL.md files to final text; 24 eval files of six cases each; Florida and California state modules marked "state module not yet reviewed"; decision 0005; tests; CI steps; version 0.2.0; CHANGELOG. Commits 228ebc2, 04f3b7d, 5cd6b6f, fbedfd5, 763679b, 358736d, 2314558.

### Step 4. Checkpoint run

```
$ python tools/lint.py
lint: 15 rules, 0 error(s), 0 warning(s)
exit 0
$ python tools/lint.py --release
lint: 15 rules, 0 error(s), 0 warning(s)
$ python tools/routing_check.py
routing check: 60 phrases, 895 combinations, 4 command sets, 53700 checks, 0 failure(s)
exit 0
$ python tools/skill_evals.py
skill evals (deterministic): 24 skills, 144 cases, 144 passed, 0 failure(s)
exit 0
$ python tools/gen_manifest.py --check
generated files current
$ diff counts table vs Stage 9 base
combination counts table unchanged
$ python tools/gen_manifest.py --counts | sed -n 7,16p
| Combination | Platform | Variants | Breakdown | Commands (min) | Commands (max) |
|---|---|---|---|---|---|
| core-only | none | 1 | 8 | 8 | 8 |
| connected | mhsb-lawmatics | 298 | 8 + 11 + 2 + 0 | 21 | 21 |
| connected | mhsb-clio | 298 | 8 + 11 + 3 + 0 | 22 | 22 |
| connected | mhsb-mycase | 298 | 8 + 11 + 0 + 0 | 19 | 19 |

Supported combinations enumerated: 895.
Maximum commands in any combination: 22.
Lint cap: 24. Design figure: 22.
$ python tools/pack_evals.py | tail -1
pack evals: 28 cases, 28 passed, 0 failed
$ python tools/license_gate.py
license gate: 17 ledger entries, 32 PROVENANCE rows, 0 failure(s)
$ denylist grep
identifiers: 17
hits (case-insensitive, word): 0
hits (short codes, case-sensitive, word): 0
$ dash check in files changed since adfce89
0
$ reading level per skill (Flesch-Kincaid; limits 9 operational, 12 document)
mhsb-clio/budget-vs-actual operational 3.6
mhsb-clio/production operational 3.6
mhsb-clio/timekeeper-hours operational 3.8
mhsb-firm-core/ai-policy-draft document 4.9
mhsb-firm-core/ai-training operational 3.9
mhsb-firm-core/ask-mhsb operational 3.7
mhsb-firm-core/before-i-paste operational 4.6
mhsb-firm-core/explain-this operational 3.5
mhsb-firm-core/follow-up operational 3.1
mhsb-firm-core/meeting-notes operational 3.2
mhsb-firm-core/start operational 3.5
mhsb-lawmatics/form-protections operational 3.8
mhsb-lawmatics/pipeline-health operational 3.9
mhsb-operations/brief operational 3.5
mhsb-operations/check-setup operational 4.1
mhsb-operations/checklist operational 4.3
mhsb-operations/consult-prep document 3.9
mhsb-operations/dates operational 4.2
mhsb-operations/hygiene operational 4.2
mhsb-operations/intake-triage operational 4.2
mhsb-operations/letter document 4.4
mhsb-operations/matter-status document 4.3
mhsb-operations/on-brand operational 3.9
mhsb-operations/report document 4.7
$ python -m pytest -q | tail -1
118 passed in 253.16s (0:04:13)
$ bash tools/verify_marketplace.sh (filtered)
Validation passed; five listed plugins installed; skills 8, 11, 2, 3; mhsb-pack-family-law not installable
```

### Step 5. Model evals

Command: `python tools/model_evals.py`


Model eval run 2026-11-04T00:55:00Z: key EMPTY; status pending.
Reason: ANTHROPIC_API_KEY is EMPTY in this environment; deterministic checks ran (tools/routing_check.py, tools/skill_evals.py).
Tokens: input 0, output 0; requests 0; estimated cost USD 0.00 (no request sent).
Planned run when a key is SET (`python tools/model_evals.py --dry-run`): routing tasks: 240; skill tasks: 144; cap USD 40.00. At the configured estimates the full run is about USD 11 (240 routing requests on claude-sonnet-5-5, 144 skill requests on claude-opus-5-5), under the USD 40 cap.

### Step 6. Firm identifier check

The private identifier list (17 identifiers: pilot firm codes, full firm names, one brand name) is held in the session scratchpad, outside the repository; the counts are in Step 4 (0 hits). The Stage 9 log line that named two short codes was rewritten (decision 0005, Section 8).

### Step 7. Push and pull request

Command: `git push -u origin cloud/pp8-skills-evals`. Draft pull request opened: https://github.com/MHSBai/platform-plugins/pull/4 ("Stage 8: skills to final text, routing suite and evals"), base `cloud/pp9-pack-fragments`. Not merged. Outcome: DONE PP-8, with model evals pending (no key).

### Step 8. Model evals run 2026-11-10 (run API-1, MHSB workstation, Console API credit)

Preflight: `GET /v1/models` lists claude-sonnet-5-5 and claude-opus-5-5 with lifecycle active; the prices in `evals/model-config.yaml` equal the standard first-party rates on https://platform.claude.com/docs/en/about-claude/pricing (fetched 2026-11-10); no configuration change. Environment: Python 3.12.3, anthropic 2.7.0, PyYAML 6.0.3.

Command: `python -u tools/model_evals.py --budget 20`, with the key sourced from the local environment file in a subshell. A first attempt (`python tools/model_evals.py`) was stopped by the session's 10-minute command timeout before it wrote any record; its requests are unrecorded and form a prefix of the same task list, so its spend is below that of the full run below. The cap of the second attempt was lowered from USD 40 to USD 20 so that the two attempts together remain under USD 40.

Model eval run 2026-11-10T16:20:52Z: key SET; status ran.
routing: model claude-sonnet-5-5; 223 of 240 passed.
skills: model claude-opus-5-5; 46 of 144 passed.
Tokens: input 1019126, output 125426; requests 384; estimated cost USD 5.46 of cap 20.00.

Decoy write tool calls: 0 of 144 skill cases. Routing failures: 12 of 17 are in the core-only command set, where the expected answer is `start`. Skill failures are mostly exact-text rules (required phrases, exact refusal and injection notices); per-case detail is in `evals/results/model-evals.json`. Estimated spend for both attempts: at most about USD 10.91 (USD 5.46 measured, plus an unrecorded first attempt below USD 5.46).

### Step 9. Review XREVIEW-PP-STACK-A (2026-11-10)

Findings PP4-M1, PP4-L1, PP4-L2 and PP4-L3 fixed on this branch (decision 0005, Section 9). The inherited findings PP1-H1, PP1-M1, PP1-M3 and PP2-M1 belong to the Stage 1 and Stage 2 pull requests.

```
$ python tools/lint.py | tail -1
lint: 15 rules, 0 error(s), 0 warning(s)
$ python tools/routing_check.py
routing check (trigger-list disjointness): 60 phrases, 895 combinations, 4 command sets, 53700 checks, 0 failure(s)
$ python tools/skill_evals.py | tail -1
skill evals (reference-transcript conformance): 24 skills, 144 cases, 144 passed, 0 failure(s)
$ python tools/gen_manifest.py --check
generated files current
$ python tools/model_evals.py --check-release; echo $?
RELEASE BLOCKED routing: 223 of 240 passed; a release needs 100 percent
RELEASE BLOCKED skills: 46 of 144 passed; a release needs 100 percent
model eval release gate: 2 problem(s)
1
$ python -m pytest -q | tail -1
121 passed in 173.09s (0:02:53)
```

Run against the Step 8 record (merged from the remote branch before this push). The gate blocks a 0.2.0 tag on both pass rates; it does not run on pull requests.

### Step 10. Fix session FIX-PP-STACK-A, 2026-11-10 (PP4-M1 per the fix contract; PP4-L1 to PP4-L3 verified; fixes from Stages 1, 2 and 9 merged)

`cloud/pp9-pack-fragments` was merged into this branch after the evals commit (ce15397) and the review response (3eaad32, merged in 0faf5a0). PP4-M1: the routing check and lint L03 were first changed to read the SKILL.md description (139 routing failures, 111 L03 errors at d6b1b93). The 87 missing trigger phrases were then quoted in the descriptions and `metadata.triggers` removed (decision 0005, Section 10). PP4-L1 (per-request worst case from `max_tokens` and the configured prices; `--budget` clamped at 40), PP4-L2 and PP4-L3 were applied by 3eaad32 and verified here. `tools/model_evals.py` was not run in this session. The recorded run (status `ran`; routing 223 of 240; skills 46 of 144) predates the description change, so the 0.2.0 tag stays blocked (HANDOFF PP-8 item 1).

```
routing_check.py   description-phrase disjointness: 60 phrases, 895 combinations, 4 command sets, 53700 checks, 0 failure(s)
skill_evals.py     reference-transcript conformance: 24 skills, 144 cases, 144 passed, 0 failure(s)
lint.py            17 rules, 0 error(s), 0 warning(s)
```

### Step 10. Review XREVIEW2-PP-STACK-A (2026-11-10)

PP4-N1 and PP4-N2 fixed (decision 0005, Section 11). PP4-N3 waits for an owner decision.

```
$ python tools/lint.py | tail -1; python tools/lint.py --release | tail -1
lint: 17 rules, 0 error(s), 0 warning(s)
lint: 17 rules, 0 error(s), 0 warning(s)
$ python tools/routing_check.py | tail -1
routing check (description-phrase disjointness): 60 phrases, 895 combinations, 4 command sets, 53700 checks, 0 failure(s)
$ python tools/skill_evals.py | tail -1
skill evals (reference-transcript conformance): 24 skills, 144 cases, 144 passed, 0 failure(s)
$ python tools/model_evals.py --check-release | tail -1
model eval release gate: 3 problem(s)   (digest absent; routing 223 of 240; skills 46 of 144)
$ python -m pytest -q | tail -1
165 passed (164 plus the repaired helper test; tests/test_routing_and_skill_evals.py 29 passed)
```

Model eval run 2026-11-10T19:53:46Z: key SET; status ran.
routing: model claude-sonnet-5-5; 238 of 240 passed.
skills: model claude-opus-5-5; 120 of 144 passed.
Tokens: input 1323237, output 125259; requests 384; estimated cost USD 6.36 of cap 12.00.

### Step 11. Fix session FIX2-PP-STACK-A, 2026-11-10 (PP4-N1, PP4-N2 and PP4-N3; two runs)

First run: `cloud/pp9-pack-fragments` merged (39c77dc); PP4-N2 (26817e8), PP4-N1 and the gate over every ga plugin (93accdf), skill revision (27ac41e), case contexts (f96b313), then one model eval run (record 7fa11af). Second run: the first run's uncommitted edits finished to the decision of decision 0005, Section 12 (92bfe1c): Design v2.1 Section 12 is not met (routing 238 of 240; skills 120 of 144; `mhsb-firm-core` 40 of 48 with 2 injection cases failing), so every plugin is held at 0.1.0 and the 0.2.0 entry is unreleased. The L06 operational test fixture, which the longer `/production` body had diluted below the bound, now replaces the body (186a47a). `tools/model_evals.py` was not run in the second run; the record's input digest equals the digest of the tree. No rule in `tools/skill_evals.py` changed in either run.

```
$ python tools/gen_manifest.py --check | tail -1; python tools/gen_manifest.py --counts > /dev/null; echo $?
generated files current
0
$ python tools/lint.py | tail -1; python tools/lint.py --release | tail -1
lint: 17 rules, 0 error(s), 0 warning(s); reading grade: textstat
lint: 17 rules, 0 error(s), 0 warning(s); reading grade: textstat
$ python -m pytest -q | tail -1
189 passed
$ python tools/routing_check.py | tail -1
routing check (description-phrase disjointness): 60 phrases, 895 combinations, 4 command sets, 53700 checks, 0 failure(s)
$ python tools/skill_evals.py | tail -1
skill evals (reference-transcript conformance): 24 skills, 144 cases, 144 passed, 0 failure(s)
$ python tools/pack_evals.py | tail -1
pack evals: 28 cases, 28 passed, 0 failed
$ python tools/license_gate.py --upstream | tail -1
license gate: 17 ledger entries, 32 PROVENANCE rows, 0 failure(s)
$ python -m pytest -q tests/test_release_check.py | tail -1
23 passed
$ bash tools/verify_marketplace.sh > /dev/null; echo $?
0
$ claude plugin validate . --strict | tail -1
Validation passed
$ python tools/model_evals.py --check-release
RELEASE BLOCKED routing: 238 of 240 passed; a release needs 100 percent
RELEASE BLOCKED skills: 120 of 144 passed; a release needs 100 percent
RELEASE BLOCKED mhsb-firm-core is tier ga and its latest eval record fails: 8 of 48 skill cases failed, 2 routing failures involve its skills (ai-policy-draft-04, ai-policy-draft-06, ai-training-06, ask-mhsb-04, before-i-paste-01, before-i-paste-03, explain-this-06, follow-up-05)
model eval release gate: 3 problem(s)
```

The gate blocks the release as intended; no digest problem is reported (record and tree: 95afc38ec1b4).

### Step 11. Ultrareview of the tooling subset (2026-11-11)

Six findings fixed (decision 0005, Section 13); four do not reproduce on the full branch.

```
$ python tools/lint.py | tail -1
lint: 17 rules, 0 error(s), 0 warning(s); reading grade: standard formula, fallback syllable count
$ python tools/skill_evals.py | tail -1
skill evals (reference-transcript conformance): 24 skills, 144 cases, 144 passed, 0 failure(s)
$ python tools/routing_check.py | tail -1
routing check (description-phrase disjointness): 60 phrases, 895 combinations, 4 command sets, 53700 checks, 0 failure(s)
$ python -m pytest -q | tail -1
205 passed, 1 skipped
```
