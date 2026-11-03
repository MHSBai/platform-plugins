---
name: start
description: 'Five things to do by role and practice area; what changed in this release; which packs the
  Firm Profile enables. Use when a user asks, for example: "what can you do for me"; "where do i begin";
  "show me my commands"; "what changed in the plugin".'
metadata:
  register: operational
  connector: none
  pack: mhsb-firm-core
  triggers:
  - what can you do for me
  - where do i begin
  - show me my commands
  - what changed in the plugin
---

# /start

## Promise

Five things to do by role and practice area; what changed in this release; which packs the Firm Profile enables.

## Inputs

- The user's role, from the Firm Profile when one exists, or as the user states it.
- The practice areas and packs the Firm Profile enables.
- The release notes for the installed version.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Find the user's role. Ask if it is not known.
2. Pick the five commands that fit that role and practice mix.
3. Say what changed in this release in plain words.
4. List the packs the profile turns on. Say which are pilot only.

## Output shape

1. Line 1: the role and the firm, as the profile states them.
2. Lines 2 to 6: five commands, each with one sentence on when to use it.
3. Line 7: what changed in this release.
4. Line 8: the packs in use.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
- Advice on a legal question. The user is pointed to the attorney.
