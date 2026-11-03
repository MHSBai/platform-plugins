---
name: matter-status
description: 'Internal status from the full record; client-facing status from the client_visible allowlist
  through an adopted template with the approver named. Use when a user asks, for example: "where does
  this matter stand"; "status of the matter"; "client update on the case".'
metadata:
  register: document
  connector: firm
  pack: mhsb-operations
  triggers:
  - where does this matter stand
  - status of the matter
  - client update on the case
---

# /matter-status

## Promise

Internal status from the full record; client-facing status from the client_visible allowlist through an adopted template with the approver named.

## Inputs

- The matter.
- The variant: internal, or client-facing.
- For the client-facing variant, the adopted status template and the approver.

A question about a client, matter or case goes to the firm connector. The user does not have to name the platform.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Settle the matter and the variant.
2. For the internal variant, read the full record.
3. For the client-facing variant, read only fields on the client_visible allowlist.
4. Render the client-facing variant through the adopted template only.

## Output shape

1. Line 1: the coverage statement.
2. Internal variant: stage, last activity, next step with its date, open tasks, data gaps.
3. Client-facing variant: the approver line, then the rendered template.
4. Section: not retrieved.

Every client-facing draft carries an approver line: "Approver: <name from the Firm Profile>". The approver is written at the top of the draft, above the first paragraph.

Every draft for a client ends with one next step and its date. If the date is not in the record, the draft says "date not established" and does not invent one.

## Coverage statement

Every output opens with a coverage statement. It gives the scope searched, the record count, whether every page was read, and the time of the read. If the connector marks the read as incomplete, give the reason. List each item that could not be read under the heading "not retrieved". A failed or partial read is never shown as an empty result.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
- A client-facing status without an adopted template.
- Any field outside the client_visible allowlist in client copy.
