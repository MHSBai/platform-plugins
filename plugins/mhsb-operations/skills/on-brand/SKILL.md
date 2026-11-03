---
name: on-brand
description: 'Checks a draft against the firm''s voice, register and vocabulary; no tool or AI names in
  client copy except the adopted AI disclosure sentence. Use when a user asks, for example: "is this on
  brand"; "check this draft against our voice"; "does this sound like the firm".'
metadata:
  register: operational
  connector: firm
  pack: mhsb-operations
  triggers:
  - is this on brand
  - check this draft against our voice
  - does this sound like the firm
---

# /on-brand

## Promise

Checks a draft against the firm's voice, register and vocabulary; no tool or AI names in client copy except the adopted AI disclosure sentence.

## Inputs

- The draft to check.
- The firm's voice, register and vocabulary from the Firm Profile.
- The adopted AI disclosure sentence.

A question about a client, matter or case goes to the firm connector. The user does not have to name the platform.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Check greeting, sign-off and formality against the firm's voice.
2. Check stage and field names against the firm's own names.
3. Flag any tool or AI name in client copy. The adopted disclosure sentence is the one exception.
4. Flag banned phrases the firm lists.

## Output shape

1. Line 1: the coverage statement.
2. Lines 2 onward: one numbered finding per line, each with the quote, the rule and a suggested change.
3. Section: not retrieved.

## Coverage statement

Every output opens with a coverage statement. It gives the scope searched, the record count, whether every page was read, and the time of the read. If the connector marks the read as incomplete, give the reason. List each item that could not be read under the heading "not retrieved". A failed or partial read is never shown as an empty result.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
- Rewriting the legal content of the draft.
