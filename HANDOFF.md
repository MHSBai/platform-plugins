# Handoff

Items that need Richard Berman, or a later stage, after PP-1 (Stage 1: repository, marketplace, manifest and lint). The cloud session did not attempt any of the repository-administration commands below.

## 1. Protect main

Requires repository administration. Status check names match the job names in `.github/workflows/ci.yml`.

```bash
gh api -X PUT repos/MHSBai/platform-plugins/branches/main/protection -H "Accept: application/vnd.github+json" --input - <<'JSON'
{
  "required_status_checks": {"strict": true, "contexts": ["lint", "tests", "agent-scan"]},
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

The `agent-scan` job prints `SNYK_TOKEN: SET` or `SNYK_TOKEN: EMPTY` and skips the scan when the secret is empty. The command prompts for the value; it is not echoed.

```bash
gh secret set SNYK_TOKEN --repo MHSBai/platform-plugins
```

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

## PP-2 (Stage 2) items

1. Element checklists: compare each checklist in `catalog/element-checklists/` against the current edition of its form under the publisher's terms, and run the similarity review; confirm the five terms statuses marked "restricted or unstated".
2. Consent requests: drafts are in mhsb-firm-service `docs/consents/consent-requests.md`; decide per form whether any wording is wanted, and send only those. Not sent from the cloud session.
3. Adoption: the 32 adapted references and fragment sources are drafts in the repository's register; the skills point to them, but they carry no attorney adoption, and none is a template.
4. MHSB hygiene items and the appointment-comms v3 gate on Stage 10 are recorded in mhsb-firm-service `HANDOFF.md`; they need pop-os and the vault.
5. Stacking: `cloud/pp2-harvest` is based on `cloud/pp1-repository-marketplace`; merge that pull request first, then rebase this branch onto `main`.

## PP-9 (Stage 9) items

1. Held general availability (Stage 11): the personal injury and business and transactional packs are complete but held at `tier: pilot` with `catalog_tier: ga` in `catalog/manifest.yaml`, and their fragments, templates and `fragment/adoption.yaml` read `PENDING ADOPTION`. To release either pack: record the attorney adopter, date and version in `fragment/adoption.yaml`, in the fragment's `adoption` and in each statutory category's `adopter`; replace each `CITATION PENDING` text with the citation the attorney confirms; adopt each template; set `tier: ga` and remove `catalog_tier`; run `python tools/gen_manifest.py` and the lint. Decision 0004 records the design; it supersedes items 1 and 2 of decision 0002, which is no longer awaiting confirmation.
2. Stage 3 vocabulary gaps, for the service repository: report identifiers for speed-to-lead and conversion, deadline risk inventory, document readiness rate, cross-practice handoff leakage, and automation and integration health; an immigration-consequences attorney-review flag; sensitive tags for children and safety-screen content. The fragments use only the closed lists and omit the missing items (decision 0004, Section 5). After the schema changes, copy it to `tools/schemas/fragment.schema.json` and update the hash in decision 0004.
3. Per-platform date-field inventory: Catalog 7 lists it as a gate on Stage 9. No inventory exists. The fragments name date categories only; the eval cases use synthetic field names. The inventory is needed before `/dates` reads a live record.
4. Interpretation to confirm: civil litigation answer deadlines and appeal windows are marked statutory (rule-fixed, citation placeholder); criminal defense and real estate carry no statutory category (decision 0004, Section 4).
5. Canonical stage maps are drafts: several practice stages map to the same canonical stage because the canonical intake pipeline is coarser than the practice pipelines (for example PI "Records Requested" and "Triage Complete" both map to `stage_intake_04_consult_completed`). Confirm with the first adopting firm.
6. Hidden packs: each `CO-DESIGN.md` lists the questions an attorney in the practice must answer before any pilot. The family law draft sets a 90-day re-verification on the contact rule as a placeholder for that attorney's answer.
7. The service-side validator run needs a local checkout of mhsb-firm-service: `python tools/validate_fragments_service.py --service ../mhsb-firm-service`. CI in this public repository runs L15 against the vendored schema and the pack evals, not the private validator.
8. Stacking: `cloud/pp9-pack-fragments` is based on `cloud/pp2-harvest`; merge Stage 1 and Stage 2 first, then rebase this branch onto `main`.
