---
name: hygiene
description: 'Defined versus populated fields, duplicate and conflicting date fields, matters without
  practice area or responsible attorney, templates never used, retire lists. Use when a user asks, for
  example: "audit our fields"; "clean up the platform data"; "duplicate date fields"; "matters without
  a responsible attorney".'
metadata:
  register: operational
  connector: firm
  pack: mhsb-operations
  triggers:
  - audit our fields
  - clean up the platform data
  - duplicate date fields
  - matters without a responsible attorney
---

# /hygiene

## Promise

Defined versus populated fields, duplicate and conflicting date fields, matters without practice area or responsible attorney, templates never used, retire lists.

## Inputs

- The scope: all matters, or a practice area.
- The platform map and the firm's chosen fields.

A question about a client, matter or case goes to the firm connector. The user does not have to name the platform.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Read field definitions and their use through the firm connector.
2. List fields that are defined but rarely filled.
3. List duplicate or conflicting date fields.
4. List matters with no practice area or no responsible attorney.
5. List templates never used and fields to retire.

## Output shape

1. Line 1: the coverage statement.
2. Section 1: defined versus populated fields, with counts.
3. Section 2: duplicate and conflicting date fields.
4. Section 3: matters missing a practice area or responsible attorney.
5. Section 4: templates never used.
6. Section 5: retire list for the firm to review.
7. Section: not retrieved.

## Coverage statement

Every output opens with a coverage statement. It gives the scope searched, the record count, whether every page was read, and the time of the read. If the connector marks the read as incomplete, give the reason. List each item that could not be read under the heading "not retrieved". A failed or partial read is never shown as an empty result.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
- Changing or retiring any field. The list goes to the firm.
