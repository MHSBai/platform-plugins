---
name: intake-triage
description: 'Scores leads against the fragment''s structured criteria with sensitive fields excluded;
  records the conflict name-match; raises attorney-review flags rather than declines; proposes one action
  per lead. Use when a user asks, for example: "triage new leads"; "which leads should we call first";
  "score the intake queue"; "check new inquiries for conflicts".'
metadata:
  register: operational
  connector: firm
  pack: mhsb-operations
  triggers:
  - triage new leads
  - which leads should we call first
  - score the intake queue
  - check new inquiries for conflicts
---

# /intake-triage

## Promise

Scores leads against the fragment's structured criteria with sensitive fields excluded; records the conflict name-match; raises attorney-review flags rather than declines; proposes one action per lead.

## Inputs

- The leads in scope: new, or a date range.
- The practice pack fragment's structured criteria.

A question about a client, matter or case goes to the firm connector. The user does not have to name the platform.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Read the leads through the firm connector.
2. Leave out every field tagged sensitive before scoring.
3. Score each lead against the fragment's criteria.
4. Run the conflict name check. Record counts and identifiers only.
5. Raise attorney-review flags where they apply: possible limitation issue, possible conflict, outside practice.
6. Propose one action per lead.

## Output shape

1. Line 1: the coverage statement.
2. Lines 2 onward: one numbered line per lead, with score, flags and the one proposed action.
3. Section: flags for attorney review.
4. Section: not retrieved.

## Coverage statement

Every output opens with a coverage statement. It gives the scope searched, the record count, whether every page was read, and the time of the read. If the connector marks the read as incomplete, give the reason. List each item that could not be read under the heading "not retrieved". A failed or partial read is never shown as an empty result.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
- Declining a lead. A flag goes to the attorney, who decides.
- Scoring on a field tagged sensitive.
