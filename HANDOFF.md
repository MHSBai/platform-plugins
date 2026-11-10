# Handoff

Items that need Richard Berman, or a later stage, after PP-1 (Stage 1: repository, marketplace, manifest and lint). The cloud session did not attempt any of the repository-administration commands below.

## 1. Protect main

Requires repository administration. Status check names match the job names in `.github/workflows/ci.yml`. `agent-scan` is left out of the required contexts until the Snyk token exists (item 2), because on a pull request without the token the job succeeds without scanning. Item 2 adds it.

```bash
gh api -X PUT repos/MHSBai/platform-plugins/branches/main/protection -H "Accept: application/vnd.github+json" --input - <<'JSON'
{
  "required_status_checks": {"strict": true, "contexts": ["lint", "tests"]},
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

Once a pull request shows `SNYK_TOKEN: SET` and a completed "Scan skills" step, make `agent-scan` required:

```bash
gh api -X POST repos/MHSBai/platform-plugins/branches/main/protection/required_status_checks/contexts -H "Accept: application/vnd.github+json" --input - <<'JSON'
{"contexts": ["agent-scan"]}
JSON
```

Until then, a push to main or a `v*` tag with the token empty fails `agent-scan` by design.

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
3. Run the release check from any machine with network access:

   ```bash
   python tools/release_check.py
   ```

   Each connector must report `PASS`: the host resolves, the certificate is valid for the host, and the endpoint answers the MCP `initialize` request (an initialize result, or HTTP 401 with a Bearer challenge naming the protected resource metadata).
4. Only then set `tier: ga` for the plugins whose connector passed, run `python tools/gen_manifest.py`, and confirm `python tools/lint.py --release` (rule L16) before the release pull request.
