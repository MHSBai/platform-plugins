---
name: explain-this
description: 'Plain-language explanation of a passage; no legal conclusions. Use when a user asks, for
  example: "explain this in plain language"; "what does this mean"; "help me understand this document".'
metadata:
  register: operational
  connector: none
  pack: mhsb-firm-core
  triggers:
  - explain this in plain language
  - what does this mean
  - help me understand this document
---

# /explain-this

## Promise

Plain-language explanation of a passage; no legal conclusions.

## Inputs

- A passage the user pastes after the pre-paste check, or a document the user names.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Confirm the pre-paste check was done for this content.
2. Explain the passage in plain words, one point at a time.
3. Mark any term whose meaning depends on the facts of a case.
4. Stop short of any view on what the law requires in this case.

## Output shape

1. Line 1: what the passage is, in one sentence.
2. Lines 2 onward: the points, each in plain words.
3. Last line: "This is an explanation, not legal advice. Ask the attorney how it applies."

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
- A legal conclusion, a prediction of outcome, or advice on what to do.
