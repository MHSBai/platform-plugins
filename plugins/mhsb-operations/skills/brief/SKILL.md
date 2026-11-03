---
name: brief
description: 'Views for today, week, stale, missing, caseload and leaks, plus pack views; every view carries
  the coverage statement and a data-gaps section. Use when a user asks, for example: "what is due this
  week"; "anything stale"; "give me my morning brief"; "what is missing from my matters"; "caseload by
  staff".'
metadata:
  register: operational
  connector: firm
  pack: mhsb-operations
  triggers:
  - what is due this week
  - anything stale
  - give me my morning brief
  - what is missing from my matters
  - caseload by staff
---

# /brief

## Promise

Views for today, week, stale, missing, caseload and leaks, plus pack views; every view carries the coverage statement and a data-gaps section.

## Inputs

- The view: today, week, stale, missing, caseload or leaks, or a view a practice pack adds.
- The person or team, when the view is narrowed.

A question about a client, matter or case goes to the firm connector. The user does not have to name the platform.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Settle the view and whose work it covers.
2. Read the mapped fields through the firm connector.
3. Build the view in the firm's time zone.
4. Add a data-gaps section for fields that are empty or unmapped.

## Output shape

1. Line 1: the coverage statement.
2. Lines 2 onward: one numbered line per item, with matter, owner and date.
3. Section: data gaps.
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

- `references/needs-you-list.md`: Needs-you list: the short view of what requires a person.
- `references/portfolio-rollup.md`: Portfolio rollup.
