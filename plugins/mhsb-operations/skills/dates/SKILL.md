---
name: dates
description: 'Dates from mapped fields only in the firm''s time zone; the entered date governs; disagreements
  listed, never resolved; "date not established" with source and owner. Use when a user asks, for example:
  "what deadlines are coming up"; "statute of limitations date"; "how many days since the accident"; "list
  the court dates".'
metadata:
  register: operational
  connector: firm
  pack: mhsb-operations
  triggers:
  - what deadlines are coming up
  - statute of limitations date
  - how many days since the accident
  - list the court dates
---

# /dates

## Promise

Dates from mapped fields only in the firm's time zone; the entered date governs; disagreements listed, never resolved; "date not established" with source and owner.

## Inputs

- The matter, or all matters in a scope.
- The date categories from the practice pack fragment.
- The platform map of date fields.

A question about a client, matter or case goes to the firm connector. The user does not have to name the platform.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Check the date fields are mapped. Stop if the mapping is absent.
2. Read the mapped dates only, in the firm's time zone.
3. Treat the entered date as the date that governs.
4. Use any computed date only as a cross-check. List each disagreement. Do not resolve it.
5. Mark each category as statutory, with its citation and adopter, or as firm-set.

## Output shape

1. Line 1: the coverage statement.
2. Lines 2 onward: one numbered line per date, with matter, category, the entered date and its source field.
3. Section: disagreements between entered and computed dates.
4. Section: date not established, with source and owner for each.
5. Section: not retrieved.

## Coverage statement

Every output opens with a coverage statement. It gives the scope searched, the record count, whether every page was read, and the time of the read. If the connector marks the read as incomplete, give the reason. List each item that could not be read under the heading "not retrieved". A failed or partial read is never shown as an empty result.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
- Deriving a governing deadline from a generic period.
- Choosing between two dates that disagree.
