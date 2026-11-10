---
name: before-i-paste
description: 'Category-based check before content is pasted; the check never sees the content first. Use
  when a user asks, for example: "can i paste this"; "is it safe to paste"; "check before i paste"; "may
  i share this document with claude".'
metadata:
  register: operational
  connector: none
  pack: mhsb-firm-core
  triggers:
  - can i paste this
  - is it safe to paste
  - check before i paste
  - may i share this document with claude
---

# /before-i-paste

## Promise

Category-based check before content is pasted; the check never sees the content first.

## Inputs

- The category of the content, chosen from a list. The content itself is not needed and should not be pasted yet.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Ask what kind of content it is before the user pastes anything.
2. Check the category against the firm's policy and the approved data categories.
3. Say yes, no, or yes with steps. Steps include removing names or numbers first.
4. If the category is not on the list, the answer is no until the attorney decides.

## Output shape

1. Line 1: the category the user chose.
2. Line 2: the answer, which is paste, do not paste, or paste after the listed steps.
3. Line 3: the reason, citing the firm's policy section.
4. Line 4: who to ask if the user disagrees.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
- Reading the content before the category check is done.
- Approving a category the firm's policy does not list.
