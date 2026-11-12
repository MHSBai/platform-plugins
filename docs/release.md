# Release procedure

Applies to every tag of MHSBai/platform-plugins from 0.1.0 onward.

## Controls

1. Protected main. No direct pushes. Changes arrive by pull request with the `lint`, `tests` and `release-gate` checks green, linear history, signed commits, no force pushes and no deletion. Administrators are included. Until a signed tag exists, main is the only installable ref, so `release-gate` runs `python tools/lint.py --release` on every pull request and every push to main as well as on `v*` tags. `agent-scan` becomes a required check once the `SNYK_TOKEN` secret is set. The job is never skipped: it concludes success only when the scan ran and passed, and fails with the reason when no scan ran, including on a pull request from a fork, which GitHub runs without secrets. A fork pull request therefore stays red until a maintainer pushes its branch to this repository. The commands that set this are in HANDOFF.md.
2. Signed tags. Every release tag is an annotated tag signed with the release key: `git tag -s vX.Y.Z -m "Release X.Y.Z"`. Unsigned tags are not releases. A tag ruleset forbids updating or deleting `v*` tags.
3. Tag-pinned sources. Firms and the directory consume a tag, never a branch. Users add the marketplace as `MHSBai/platform-plugins#vX.Y.Z`; the directory submission tracks the release tag. Within a tag, relative-path plugin sources resolve to the same commit.
4. Second identity with a hardware key. A release requires a second GitHub identity, distinct from the day-to-day account, whose sign-in and signing key sit on a hardware security key. That identity approves the release pull request and creates the signed tag. The day-to-day account cannot create `v*` tags.

## Steps

1. Bump `defaults.version` in `catalog/manifest.yaml`, run `python tools/gen_manifest.py`, and add a CHANGELOG entry written for staff at a firm.
2. Run the release gate locally, with the firm service checkout beside this one, and paste its output into the pull request: `tools/release-gate.sh` (see "Release gate" below). It must print `RELEASE GATE: GREEN`. The model eval item fails unless `evals/results/model-evals.json` records a model eval run on the current text (its input digest equals the tree) that covered every routing and skill task and passed all of them, and it names any general availability plugin whose cases failed (Design v2.1 Section 12; decision 0005, Sections 9 and 11). CI runs the same release checks in the `release-gate` job on every pull request, every push to main and every `v*` tag. `--release` turns warnings into errors. A synthetic adoption record (decision 0002) fails it, and so does a general availability connector plugin whose endpoint fails `tools/release_check.py` (host outside the recorded edge, or no authenticated `initialize` returning the recorded server name and version) or which lacks a privacy policy or terms of service URL (rule L16, HANDOFF item 8). A pack held at pilot with `PENDING ADOPTION` (decision 0004) is unlisted and does not block a release.
3. Run the firm-name check from outside this repository (HANDOFF item 5) and record zero hits.
4. Merge with the second identity's approval.
5. With the second identity, on the merge commit: `git tag -s vX.Y.Z -m "Release X.Y.Z"` and `git push origin vX.Y.Z`.
6. Verify: `git tag -v vX.Y.Z`, then `claude plugin validate .` on a fresh clone at the tag.
7. `/start` shows the delta from the CHANGELOG once the release is installed; `/check-setup` warns users who remain behind.

## Release gate

`tools/release-gate.sh` (Prompts v2.0, Prompt 12 step 4) runs every release check of this repository and, through the firm service checkout (`PLATFORM_SERVICE_DIR`, default `../mhsb-firm-service`), the service's own items, so that one run covers the whole list: lint, unit tests, the isolation suite, the log-leak test, the custody tests, the routing and skill evals, the restore and failover drill evidence (at most ninety days old), the freshness of the service's `docs/controls.md`, and the provenance and license gate. It fails on any red item, and a missing service checkout is a failure, never a skip. The service runs this gate with `--own-only` in its own gate, and this gate runs the service gate with `--own-only`; a `--own-only` run reports PARTIAL and exits 3 even when every item passes.

| Item | Command | Passes when |
|---|---|---|
| P0 committed tree | `git status` over tracked files | nothing uncommitted |
| P1 generated files current | `tools/gen_manifest.py --check` | the generated files match the manifest |
| P2 lint | `tools/lint.py` | no error |
| P3 release lint | `tools/lint.py --release` | no error or warning |
| P4 unit tests | `python -m pytest -q` | every test passes |
| P5 pack evals | `tools/pack_evals.py` | every pack case passes |
| P6 routing suite | `tools/routing_check.py` | every supported combination resolves each phrase to one skill |
| P7 skill evals | `tools/skill_evals.py` | every reference transcript passes its scoring rules |
| P8 model eval release gate | `tools/model_evals.py --check-release` | the latest model eval record is on the current text and every case passed |
| P9 PROVENANCE and license gate | `tools/license_gate.py --upstream` | rules G1 to G6 hold, upstream LICENSE hashes included |
| P10 firm service items | the service's `tools/release-gate.sh --own-only` | its own items pass |

`tools/release-gate.sh --self-test` runs `tests/test_release_gate.py`. The `agent-scan` CI job is not part of the gate: it needs the `SNYK_TOKEN` secret (decision D8) and fails until that secret is set.

State on 2026-11-11: P8 fails (the latest model eval record predates the current text, routing passed 238 of 240 cases and skills 120 of 144, and mhsb-firm-core is listed at general availability although decision D10 holds it at pilot until every case passes); P10 fails on the service's drill evidence item, because hosting is not yet built. The recorded output is in `state/EXECUTION-LOG.md`.
