---
name: consult-prep
description: 'One page from the record with known facts, missing information, fragment questions, a conflict
  reminder and the fee and disclosure conversations; also used for hearing preparation. Use when a user
  asks, for example: "prepare me for the consultation"; "consult prep"; "get ready for the hearing"; "one
  page before the meeting with the prospect".'
metadata:
  register: document
  connector: firm
  pack: mhsb-operations
  triggers:
  - prepare me for the consultation
  - consult prep
  - get ready for the hearing
  - one page before the meeting with the prospect
---

# /consult-prep

## Promise

One page from the record with known facts, missing information, fragment questions, a conflict reminder and the fee and disclosure conversations; also used for hearing preparation.

## Inputs

- The lead or matter, and the date of the consultation or hearing.
- The practice pack fragment for the matter type.

A question about a client, matter or case goes to the firm connector. The user does not have to name the platform.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Settle which lead or matter and which meeting.
2. Read the record through the firm connector.
3. List what is known, each fact with the field it came from.
4. List what is missing, using the fragment's intake questions.
5. Add the conflict reminder and the fee and disclosure points.

## Output shape

1. Line 1: the coverage statement.
2. Section 1: known facts, each with its source field.
3. Section 2: missing information.
4. Section 3: questions from the fragment.
5. Section 4: conflict reminder.
6. Section 5: fee and disclosure conversations.
7. Section: not retrieved.

## Coverage statement

Every output opens with a coverage statement. It gives the scope searched, the record count, whether every page was read, and the time of the read. If the connector marks the read as incomplete, give the reason. List each item that could not be read under the heading "not retrieved". A failed or partial read is never shown as an empty result.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
- A view on the merits of the matter.
