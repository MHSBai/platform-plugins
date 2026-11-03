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
