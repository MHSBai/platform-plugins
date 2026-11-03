---
name: letter
description: 'Renders an adopted template with variables from the record and the firm''s periods; refuses
  an unadopted template; writes the approver into the draft. Use when a user asks, for example: "draft
  a decline letter"; "welcome letter for the new client"; "document request letter"; "prepare a closing
  letter".'
metadata:
  register: document
  connector: firm
  pack: mhsb-operations
  triggers:
  - draft a decline letter
  - welcome letter for the new client
  - document request letter
  - prepare a closing letter
---

# /letter

## Promise

Renders an adopted template with variables from the record and the firm's periods; refuses an unadopted template; writes the approver into the draft.

## Inputs

- The letter type: decline, welcome, status update, document request, no-show and reschedule, preservation instructions, scope, hold notice or closing.
- The matter or lead.
- The adopted template for that type, with its adoption record.

A question about a client, matter or case goes to the firm connector. The user does not have to name the platform.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Settle the letter type, the recipient and the matter.
2. Check that the template carries an adoption record. Stop if it does not.
3. Fill the template's variables from the record and the firm's periods.
4. For a decline, keep the limitation warning and the prospective-client handling the template contains.
5. Write the approver into the draft.

## Output shape

1. Line 1: the coverage statement.
2. Line 2: the approver line.
3. Line 3: the template identifier and its adoption record.
4. Lines 4 onward: the rendered letter.
5. Section: variables not filled, under not retrieved.

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
- A template without an adoption record.
- Wording that is not in the adopted template. Only variables are filled.
