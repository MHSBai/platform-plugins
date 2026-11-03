---
name: ask-mhsb
description: 'Support request packaged for MHSB; matter content refused. Use when a user asks, for example:
  "contact mhsb support"; "something is broken with the plugin"; "ask mhsb a question".'
metadata:
  register: operational
  connector: none
  pack: mhsb-firm-core
  triggers:
  - contact mhsb support
  - something is broken with the plugin
  - ask mhsb a question
---

# /ask-mhsb

## Promise

Support request packaged for MHSB; matter content refused.

## Inputs

- What went wrong or what is needed, in the user's words.
- The output of the setup check, when available.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Ask what the user was trying to do and what happened.
2. Remove any client or matter content from the request.
3. Package the request with the plugin version and the setup check result.
4. Show the package to the user before it is passed on.

## Output shape

1. Line 1: a one-sentence summary of the request.
2. Line 2: plugin and profile versions.
3. Line 3: the steps the user took.
4. Line 4: what the user expected and what happened.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
- Matter content of any kind, including client names, facts or documents. The user is asked to remove it.

## References

Read these files in this skill's `references/` folder when the step needs them. Each one names its source and license at its top.

- `references/request-triage.md`: Request triage: packaging a support request for MHSB.
