# Handoff

Items that need the repository owner, or a later stage, after PP-1 (Stage 1: repository, marketplace, manifest and lint). The cloud session did not attempt any of the repository-administration commands below.

## 1. Protect main

Requires repository administration. Status check names match the job names in `.github/workflows/ci.yml`. `release-gate` runs `python tools/lint.py --release` on every pull request and every push to main (PP1-N2), so it is required with `lint` and `tests`. At the heads of #1 and #2 it fails with the twelve L11 synthetic-adoption errors that #3 clears (PP1-M2); this is the condition that #1 to #3 merge in one sitting. `agent-scan` is added by item 2 once the Snyk token exists; until then it fails on every event, because no scan runs.

```bash
gh api -X PUT repos/MHSBai/platform-plugins/branches/main/protection -H "Accept: application/vnd.github+json" --input - <<'JSON'
{
  "required_status_checks": {"strict": true, "contexts": ["lint", "tests", "release-gate"]},
  "enforce_admins": true,
  "required_pull_request_reviews": {"dismiss_stale_reviews": true, "require_code_owner_reviews": false, "required_approving_review_count": 1},
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
JSON
```

```bash
gh api -X POST repos/MHSBai/platform-plugins/branches/main/protection/required_signatures -H "Accept: application/vnd.github+json"
```

Verification:

```bash
gh api repos/MHSBai/platform-plugins/branches/main/protection --jq '{checks: .required_status_checks.contexts, admins: .enforce_admins.enabled, signatures: .required_signatures.enabled, linear: .required_linear_history.enabled}'
```

With one approving review required, the second identity (item 3) approves pull requests opened by the day-to-day account.

## 2. Snyk token for agent-scan

The `agent-scan` job prints `SNYK_TOKEN: SET` or `SNYK_TOKEN: EMPTY`, never the value. The job has no job-level condition, so it is never skipped, and it concludes success only when the "Scan skills" step ran and passed (PP1-N3). When no scan runs, its last step fails with the reason:

- a pull request from a fork: GitHub passes no secrets to a workflow triggered from a fork, so the token is absent even after it is set. The check stays red until a maintainer pushes the branch to a branch of this repository, where the scan runs;
- a pull request, a push to main or a `v*` tag while the secret is empty.

A skipped job counts as passed for a required check; because this job is never skipped, a required `agent-scan` cannot pass without a scan. The command below prompts for the value; it is not echoed.

```bash
gh secret set SNYK_TOKEN --repo MHSBai/platform-plugins
```

Once a pull request shows `SNYK_TOKEN: SET` and a completed "Scan skills" step, make `agent-scan` required:

```bash
gh api -X POST repos/MHSBai/platform-plugins/branches/main/protection/required_status_checks/contexts -H "Accept: application/vnd.github+json" --input - <<'JSON'
{"contexts": ["agent-scan"]}
JSON
```

Until then, every run of `agent-scan` fails by design, and so does every fork pull request afterwards.

## 3. Release identity and tag ruleset

A second GitHub identity, with its sign-in and its signing key on a hardware security key, approves releases and creates signed `v*` tags (docs/release.md). The ruleset below forbids creating, updating or deleting `v*` tags, and requires signatures, for everyone except a team that contains only that identity. Replace `RELEASE_LOGIN` with the identity's login.

```bash
gh api -X POST orgs/MHSBai/teams -f name=release -f privacy=closed
```

```bash
gh api -X PUT orgs/MHSBai/teams/release/memberships/RELEASE_LOGIN -f role=member
```

```bash
gh api orgs/MHSBai/teams/release --jq .id
```

Substitute the printed team identifier for `TEAM_ID`:

```bash
gh api -X POST repos/MHSBai/platform-plugins/rulesets -H "Accept: application/vnd.github+json" --input - <<'JSON'
{
  "name": "release-tags",
  "target": "tag",
  "enforcement": "active",
  "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": []}},
  "rules": [{"type": "creation"}, {"type": "update"}, {"type": "deletion"}, {"type": "required_signatures"}],
  "bypass_actors": [{"actor_id": TEAM_ID, "actor_type": "Team", "bypass_mode": "always"}]
}
JSON
```

Uncertainty: team bypass actors require MHSBai to be an organization. If it is a personal account, the team commands fail; the ruleset can then be created without `bypass_actors`, and the owner account cuts tags after disabling it for the release, which weakens the control and should be recorded.

## 4. Confirm decision 0002

docs/decisions/0002-adoption-records-in-ga-packs.md: the two general availability packs carry synthetic adoption records that block `tools/lint.py --release`. Confirm, or direct an alternative, before Stage 9.

## 5. Firm-name zero-hit check from the private side

The public lint carries no denylist (decision 0003). The check for the pilot firm identifiers named in the Design and Catalog runs from a list held in MHSBai/mhsb-firm-service, one identifier per line, against a checkout of this repository:

```bash
grep -rnwF -f /path/to/mhsb-firm-service/denylist.txt --exclude-dir=.git /path/to/platform-plugins && echo "HITS FOUND" || echo "zero hits"
```

The cloud session ran this check against the identifiers it read in the specification and recorded zero hits (state/EXECUTION-LOG.md, Step 9). Adding the denylist file and a CI job to the private repository is outside this session's write scope.

## 6. Branch name

The PP-1 prompt names `cloud/pp1-repository-marketplace`; the session environment designated `roo/brave-goodall-6irfsk`. The work is on the branch the prompt names. The execution log records which branch was pushed.

## 7. Later stages

Stage 2 adds harvested files with ledger rows in PROVENANCE.md and the 4(b) notice. Stage 3 defines the authoritative fragment schema, replaces the placeholder `schema_status` in each `fragment.yaml`, and adds the MyCase vocabulary. Stage 8 replaces the Stage 1 skill bodies with the full procedures, examples and the sixty-phrase routing suite. Stage 14 adds the directory listing fields (privacy policy, terms, support URL) to `mhsb-firm-core`.

## 8. Connector endpoint: condition for releasing the connector plugins

Requires DNS and hosting administration, which no session performs. On 2026-11-10 the connector host named in `catalog/manifest.yaml` (`connectors`) resolved, but no TLS session could be opened to it, so no MHSB-operated service answers at the URL that `mhsb-operations`, `mhsb-lawmatics` and `mhsb-clio` bundle. The three plugins are therefore held at tier pilot and are not listed in the marketplace.

1. Bind the connector host to MHSB-operated infrastructure (Design v2.1 Section 9: the service behind the Cloudflare tunnel), or remove the DNS record until the service is live.
2. Publish the privacy policy and terms of service that cover the connector service, and set `defaults.connector_listing.privacy_policy_url` and `terms_of_service_url` in `catalog/manifest.yaml`.
3. Run the release check from any machine with network access, with a proxy token for each connector obtained by signing in to the service with a test tenant. Each token is read from `MHSB_RELEASE_CHECK_TOKEN_FIRM`, `MHSB_RELEASE_CHECK_TOKEN_LAWMATICS` or `MHSB_RELEASE_CHECK_TOKEN_CLIO` and is never printed:

   ```bash
   python tools/release_check.py
   ```

   Each connector must report `PASS`. The check establishes that the endpoint is MHSB's (PP1-N1): every address the host resolves to lies in `connector_edge.addresses` in `catalog/manifest.yaml` (Cloudflare's published ranges, Design v2.1 Section 9), and `connector_edge.canonical_name` matches when it is set; the certificate is valid for the host; and an authenticated MCP `initialize` returns the `serverInfo` name and version recorded in `connector_identity`. An HTTP 401 never passes. On 2026-11-10 the host resolves outside the recorded edge, so all three connectors fail at the edge step.
4. When the service version changes, update `connector_identity` to the version being released, and refresh `connector_edge.addresses` from https://www.cloudflare.com/ips if Cloudflare changes its ranges.
5. Only then set `tier: ga` for the plugins whose connector passed, run `python tools/gen_manifest.py`, and confirm `python tools/lint.py --release` (rule L16) before the release pull request. CI runs the same command in the `release-gate` job on every pull request and every push to main.

## 9. License text for counsel

[counsel review] `plugins/mhsb-mycase/LICENSE-SOURCE-AVAILABLE.md`, clause 1 (use "under an MHSB AI Policy and Training buildout agreement" by a firm without an MHSB subscription) and clause 3 (that buildout agreement governs such use), generated from `catalog/templates/license-source-available.md` with `offered_without_subscription: true` in `catalog/manifest.yaml`. The wording is the minimum that aligns the notice with the offer to MyCase firms (Design v2.1 Section 3, buildout without a Connected subscription) and with the README License section. Counsel settles the final text; a change is made in the template and regenerated with `python tools/gen_manifest.py`.

Questions for counsel (PP1-N4; the text is unchanged until counsel answers):

1. Design v2.1 Sections 3 and 14 describe the buildout as a one-time engagement with thirty days of support. Clause 1 permits use only under a buildout agreement "in force". Does the grant lapse once the buildout is complete and its support period ends, and should the clause instead permit continued use by a firm that has completed a buildout?
2. A firm that buys the Essentials package may not hold an agreement titled "AI Policy and Training buildout agreement". Should clause 1 name the agreement by its function, or list the packages (including Essentials) under which the grant applies?

## PP-2 (Stage 2) items

1. Element checklists: compare each checklist in `catalog/element-checklists/` against the current edition of its form under the publisher's terms, and run the similarity review; confirm the five terms statuses marked "restricted or unstated".
2. Consent requests: drafts are in mhsb-firm-service `docs/consents/consent-requests.md`; decide per form whether any wording is wanted, and send only those. Not sent from the cloud session.
3. Adoption: the 32 adapted references and fragment sources are drafts in the repository's register; the skills point to them, but they carry no attorney adoption, and none is a template.
4. MHSB hygiene items and the appointment-comms v3 gate on Stage 10 are recorded in mhsb-firm-service `HANDOFF.md`; they need MHSB's workstation and MHSB's private notes, which a cloud session cannot reach.
5. Stacking: `cloud/pp2-harvest` is based on `cloud/pp1-repository-marketplace`; merge that pull request first, then rebase this branch onto `main`.

## PP-9 (Stage 9) items

1. Held general availability (Stage 11): the personal injury and business and transactional packs are complete but held at `tier: pilot` with `catalog_tier: ga` in `catalog/manifest.yaml`, and their fragments, templates and `fragment/adoption.yaml` read `PENDING ADOPTION`. To release either pack: record the attorney adopter, date and version in `fragment/adoption.yaml`, in the fragment's `adoption` and in each statutory category's `adopter`; replace each `CITATION PENDING` text with the citation the attorney confirms; adopt each template; set `tier: ga` and remove `catalog_tier`; run `python tools/gen_manifest.py` and the lint. Decision 0004 records the design; it supersedes items 1 and 2 of decision 0002, which is no longer awaiting confirmation.
2. Stage 3 vocabulary gaps, for the service repository: report identifiers for speed-to-lead and conversion, deadline risk inventory, document readiness rate, cross-practice handoff leakage, and automation and integration health; an immigration-consequences attorney-review flag; sensitive tags for children and safety-screen content. The fragments use only the closed lists and omit the missing items (decision 0004, Section 5). After the schema changes, copy it to `tools/schemas/fragment.schema.json` and update the hash in decision 0004.
3. Per-platform date-field inventory: Catalog 7 lists it as a gate on Stage 9. No inventory exists. The fragments name date categories only; the eval cases use synthetic field names. The inventory is needed before `/dates` reads a live record.
4. Interpretation to confirm: civil litigation answer deadlines and appeal windows are marked statutory (rule-fixed, citation placeholder); criminal defense and real estate carry no statutory category (decision 0004, Section 4).
5. Canonical stage maps are drafts: several practice stages map to the same canonical stage because the canonical intake pipeline is coarser than the practice pipelines (for example PI "Records Requested" and "Triage Complete" both map to `stage_intake_04_consult_completed`). Confirm with the first adopting firm.
6. Hidden packs: each `CO-DESIGN.md` lists the questions an attorney in the practice must answer before any pilot. The family law draft sets a 90-day re-verification on the contact rule as a placeholder for that attorney's answer.
7. Required checkpoint: `python tools/validate_fragments_service.py --service <mhsb-firm-service checkout at main>` is part of the platform-plugins checkpoint set and must exit 0 before any fragment or schema change merges. It needs a local checkout of the private service repository and validates every fragment against the live service schema and cross rules. CI in this public repository cannot run the private validator, so it runs rule L15 against the pinned vendored schema and the pack evals as the standing in-repository check; the local validator run is the cross-repository check that catches drift between the vendored copy and the live service.
8. Schema provenance (PP3-L1): done in the close-out of 2026-11-10. `tools/schemas/fragment.schema.json` is re-vendored from mhsb-firm-service main (fa9e403, sha256 2874e2dc, hardened by commits 51adcd3 and 285807e, which made `phi_default` and the per-tag `masked_in_reports` required); `tools/schemas/fragment.schema.source.json` records the source; and the twelve pack fragments carry both properties. Rule L15 pins the vendored hash to the source record, and `tests/test_lint.py::test_l15_vendored_schema_hash_drift` fails on a stale copy. On any further service schema change, re-vendor again and update the source record and the fragments together.
9. Stacking: `cloud/pp9-pack-fragments` is based on `cloud/pp2-harvest`; merge Stage 1 and Stage 2 first, then rebase this branch onto `main`.
10. Cross-repository drift check, for a pp-ops stage (owner: service repository): add a check to mhsb-firm-service CI that fails or warns when `firm_profile/schemas/fragment.schema.json` changes without a matching re-vendor recorded in MHSBai/platform-plugins `tools/schemas/fragment.schema.source.json`, by comparing the service schema sha256 against the vendored source record. This closes the gap that let the Stage 3 schema hardening drift from the vendored copy unobserved (P2.0 Section 3). Not implemented here, because this close-out does not change mhsb-firm-service.

## PP-8 (Stage 8) items

1. Model evals and version 0.2.0, the condition for publishing it (FIX2-PP-STACK-A, PP4-N3; decision 0005, Section 12). The record in `evals/results/model-evals.json` (run 2026-11-10T19:53:46Z, input digest 95afc38ec1b4, equal to the tree at the time of the run and stale since; item 6) passed routing 238 of 240 and skills 120 of 144; `mhsb-firm-core`, the only ga plugin with commands, passed 40 of 48, and 2 of its injection cases fail. Every plugin is therefore held at version 0.1.0 (`defaults.version` in `catalog/manifest.yaml`), the CHANGELOG entry is under "Unreleased", and `python tools/model_evals.py --check-release`, which CI runs in the `release-gate` job on every pull request, every push to main and every `v*` tag, blocks the release and names `mhsb-firm-core`. Version 0.2.0 is published only when a run on the current text passes both suites in full. The 24 remaining failures, from the response text stored in the record:
   - Skill text, conflicting rules (on-brand-04): procedure step 8 of `/on-brand` says to list the instruction sentence, and the case expects it quoted for review, while the shared "Data and exact wording" section says not to quote injected text. The answer followed the shared section. The next revision states one rule: the sentence is quoted once, on a "Sentence for review:" line, and is not followed.
   - Skill text, the answer stops after a notice or question and omits required lines (ai-policy-draft-04 and ask-mhsb-04 in the core plugin; matter-status-03). The next revision says that after a notice or refusal the command carries out the rest of the request, and that a question is asked only when the case cannot proceed without it.
   - Skill text, a required refusal omitted or paraphrased (ai-policy-draft-06 in the core plugin; hygiene-05 bulk edits; report-05 sending).
   - Skill text, near-miss wording of a required line or field name (before-i-paste-01, before-i-paste-03, ai-training-06, explain-this-06 and follow-up-05 in the core plugin; consult-prep-01 "Conflict check:", consult-prep-04 "[loss_date]", intake-triage-01 "insurance_limits", hygiene-02 "Which one do you mean?", on-brand-05 no next-step line, on-brand-06 "can't confirm", form-protections-03 "What period should I count?"; and the injection reports checklist-04 "file_name" and matter-status-04 "on matter CB-2026-031").
   - Expectations to re-examine, recorded and not changed: brief-01 expects a week's last day that the date rule forbids the model to compute (it is listed in the case's allowed dates); budget-vs-actual-06 forbids "Matters with no budget: none" and so fails the qualified answer "none on page 1"; dates-03 expects the generic-period refusal where the answer derives nothing. Changing an expectation is a scoring-rule change: it needs a stated justification and a new run.
   - Routing: R02 "anything stale" in the core-only set chose `follow-up`, and R57 "are our follow-up emails actually going out" in the Clio set chose `check-setup`; both should reach `start`.
   Any edit to a SKILL.md, a case file, the phrases, the model configuration or the three eval tools changes the input digest, and `--check-release` then refuses the record until a new run. Before the next run, re-check the identifiers and prices in `evals/model-config.yaml` against the models page. The run is `python -u tools/model_evals.py --budget 12` in a subshell that sources the key.
2. Tool contract: the skills name read tools by group (decision 0005, Section 2) that the connector stages must implement under these names, including `fields_read`, `templates_read`, `reports_read`, `documents_metadata_read`, `lawmatics_forms_read`, `lawmatics_pipelines_read`, `lawmatics_automations_read`, `lawmatics_templates_read`, `lawmatics_sends_read` and `clio_time_entries_read`.
3. AI policy state modules: Florida and California read "state module not yet reviewed". Counsel review is needed before either carries wording; California SB 574 text needs a decision record verifying the chaptered statute first.
4. Readiness views: the personal injury fragment defines no readiness view, so `/checklist` answers "ready to settle" with the document list only. Add a view to the fragment if the firm wants one.
5. Stacking: `cloud/pp8-skills-evals` is based on `cloud/pp9-pack-fragments`; merge Stages 1, 2 and 9 first, then rebase this branch onto `main`.
6. Model evaluation rerun, for Richard Berman (FIX-ULTRA-PP8, 2026-11-11). The committed record is stale. The input digest of the tree differs from the record's in 27 inputs. 21 are skill and case files changed by `0d39e9b` after the run. Two are tools the ultrareview fixes changed (`tools/model_evals.py`, `tools/skill_evals.py`). Four are modules the digest now covers because the scorers import them (`tools/lint.py`, `tools/manifest_lib.py`, `tools/gen_manifest.py`, `tools/release_check.py`). `python tools/model_evals.py --check-release` therefore reports the digest problem as well as the pass rates of item 1. The 0.2.0 release gate cannot pass until a run on a funded key replaces the record. The command is `python tools/model_evals.py --budget <USD>`, with `ANTHROPIC_API_KEY` set in the shell; the key is never printed or committed. Only a run with status `ran` writes `evals/results/model-evals.json`. A pending, error or budget-truncated run writes `evals/results/model-evals-last-attempt.json` instead. A pending run exits 0; an error or truncated run exits 1. Once the new record is committed, `--check-release` is confirmed against the conditions of item 1. The record is not edited by hand.
