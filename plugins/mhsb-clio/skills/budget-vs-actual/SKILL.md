---
name: budget-vs-actual
description: 'Budgeted hours versus recorded hours by matter. Use when a user asks, for example: "budget
  versus actual"; "flat fee matters over budget"; "budgeted hours versus recorded".'
metadata:
  register: operational
  connector: platform
  pack: mhsb-clio
  triggers:
  - budget versus actual
  - flat fee matters over budget
  - budgeted hours versus recorded
---

# /budget-vs-actual

## Promise

Budgeted hours versus recorded hours by matter.

## Inputs

- The matters in scope, or all flat-fee matters.

A question about a client, matter or case goes to the firm connector. The user does not have to name the platform.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Read the budgeted hours field and recorded time through the Clio connector.
2. Compute the variance per matter.
3. List matters with no budget set as data gaps.

## Output shape

1. Line 1: the coverage statement.
2. Lines 2 onward: one line per matter, with budgeted hours, recorded hours and variance.
3. Section: matters with no budget.
4. Section: not retrieved.

## Coverage statement

Every output opens with a coverage statement. It gives the scope searched, the record count, whether every page was read, and the time of the read. If the connector marks the read as incomplete, give the reason. List each item that could not be read under the heading "not retrieved". A failed or partial read is never shown as an empty result.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
