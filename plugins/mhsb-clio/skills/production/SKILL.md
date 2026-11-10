---
name: production
description: 'Billed amounts by billing method. Use when a user asks, for example: "production by billing
  method"; "billed amounts this month"; "how much did we bill".'
metadata:
  register: operational
  connector: platform
  pack: mhsb-clio
  triggers:
  - production by billing method
  - billed amounts this month
  - how much did we bill
---

# /production

## Promise

Billed amounts by billing method.

## Inputs

- The period.

A question about a client, matter or case goes to the firm connector. The user does not have to name the platform.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Settle the period in the firm's time zone.
2. Read billed amounts through the Clio connector.
3. Group the amounts by billing method.

## Output shape

1. Line 1: the coverage statement.
2. Lines 2 onward: one line per billing method, with the billed amount.
3. Section: not retrieved.

## Coverage statement

Every output opens with a coverage statement. It gives the scope searched, the record count, whether every page was read, and the time of the read. If the connector marks the read as incomplete, give the reason. List each item that could not be read under the heading "not retrieved". A failed or partial read is never shown as an empty result.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
