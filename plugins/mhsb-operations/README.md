# mhsb-operations

Read-only operations commands for subscribing firms: briefs, consultation preparation, matter status, intake triage, adopted letters, dates, document checklists, data hygiene, reports, register checks and setup verification. Bundles the MHSB firm connector.

Release tier: ga. License: `LicenseRef-MHSB-Source-Available`. Version: 0.2.0.

Bundles the MHSB firm connector (`https://mcp.mhsbsolutions.com/firm`) as a remote MCP server. Every command is read-only.

## Installation

/plugin install mhsb-operations --marketplace MHSBai/platform-plugins

From a shell, after `claude plugin marketplace add MHSBai/platform-plugins#<tag>`: `claude plugin install mhsb-operations@mhsb-platform-plugins`.

## Commands

| Command | Promise |
|---|---|
| /brief | Views for today, week, stale, missing, caseload and leaks, plus pack views; every view carries the coverage statement and a data-gaps section. |
| /consult-prep | One page from the record with known facts, missing information, fragment questions, a conflict reminder and the fee and disclosure conversations; also used for hearing preparation. |
| /matter-status | Internal status from the full record; client-facing status from the client_visible allowlist through an adopted template with the approver named. |
| /intake-triage | Scores leads against the fragment's structured criteria with sensitive fields excluded; records the conflict name-match; raises attorney-review flags rather than declines; proposes one action per lead. |
| /letter | Renders an adopted template with variables from the record and the firm's periods; refuses an unadopted template; writes the approver into the draft. |
| /dates | Dates from mapped fields only in the firm's time zone; the entered date governs; disagreements listed, never resolved; "date not established" with source and owner. |
| /checklist | Documents present versus the fragment's document list per matter; readiness views driven by the fragment. |
| /hygiene | Defined versus populated fields, duplicate and conflicting date fields, matters without practice area or responsible attorney, templates never used, retire lists. |
| /report | Lists the report catalog, runs one report now with the coverage statement, or prepares service delivery setup. |
| /on-brand | Checks a draft against the firm's voice, register and vocabulary; no tool or AI names in client copy except the adopted AI disclosure sentence. |
| /check-setup | Sign-in, plan attestation, enabled packs and role mode, profile version and hash, plugin and service versions, scheduled reports and their last run. |

## Scope

The plugin does no legal research, drafts no filings, produces no citations, takes no trust account action, sends nothing, deletes nothing and, in version 1, writes nothing to the firm's platform. Outputs require review by a licensed attorney.
