---
name: check-setup
description: 'Sign-in, plan attestation, enabled packs and role mode, profile version and hash, plugin
  and service versions, scheduled reports and their last run. Use when a user asks, for example: "check
  my setup"; "am i signed in"; "which version am i running"; "is the connector working".'
metadata:
  register: operational
  connector: firm
  pack: mhsb-operations
  triggers:
  - check my setup
  - am i signed in
  - which version am i running
  - is the connector working
---

# /check-setup

## Promise

Sign-in, plan attestation, enabled packs and role mode, profile version and hash, plugin and service versions, scheduled reports and their last run.

## Inputs

- None. The command reads the session and the firm connector.

A question about a client, matter or case goes to the firm connector. The user does not have to name the platform.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Check sign-in to the firm connector.
2. Read the plan attestation, the enabled packs and the role mode.
3. Read the profile version and hash.
4. Read the plugin and service versions. Warn when the plugin is behind.
5. List the scheduled reports and the time of each last run.

## Output shape

1. Line 1: the coverage statement.
2. Lines 2 to 7: sign-in, plan attestation, packs, role mode, profile version and hash, versions.
3. Section: scheduled reports with last run.
4. Section: not retrieved.

## Coverage statement

Every output opens with a coverage statement. It gives the scope searched, the record count, whether every page was read, and the time of the read. If the connector marks the read as incomplete, give the reason. List each item that could not be read under the heading "not retrieved". A failed or partial read is never shown as an empty result.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.

## References

Read these files in this skill's `references/` folder when the step needs them. Each one names its source and license at its top.

- `references/runbook.md`: Runbook shape for setup checks.
