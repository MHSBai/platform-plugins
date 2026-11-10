---
name: checklist
description: 'Documents present versus the fragment''s document list per matter; readiness views driven
  by the fragment. Use when a user asks, for example: "which documents are missing"; "is the file ready
  for signing"; "document checklist for this matter".'
metadata:
  register: operational
  connector: firm
  pack: mhsb-operations
  triggers:
  - which documents are missing
  - is the file ready for signing
  - document checklist for this matter
---

# /checklist

## Promise

Documents present versus the fragment's document list per matter; readiness views driven by the fragment.

## Inputs

- The matter or matters.
- The document list from the practice pack fragment.
- The readiness view, when one is asked for.

A question about a client, matter or case goes to the firm connector. The user does not have to name the platform.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Settle the matter and the checklist.
2. Read the documents on the record through the firm connector.
3. Compare them with the fragment's document list.
4. Build the readiness view the fragment defines, when asked.

## Output shape

1. Line 1: the coverage statement.
2. Lines 2 onward: one line per listed document, marked present or missing.
3. Section: readiness, when asked.
4. Section: not retrieved.

## Coverage statement

Every output opens with a coverage statement. It gives the scope searched, the record count, whether every page was read, and the time of the read. If the connector marks the read as incomplete, give the reason. List each item that could not be read under the heading "not retrieved". A failed or partial read is never shown as an empty result.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
