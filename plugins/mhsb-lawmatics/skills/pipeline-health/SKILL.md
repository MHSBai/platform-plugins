---
name: pipeline-health
description: 'Stage definitions versus use, dark automations, templates never sent, duplicate sends. Use
  when a user asks, for example: "pipeline health"; "which automations are dark"; "templates never sent";
  "duplicate sends".'
metadata:
  register: operational
  connector: platform
  pack: mhsb-lawmatics
  triggers:
  - pipeline health
  - which automations are dark
  - templates never sent
  - duplicate sends
---

# /pipeline-health

## Promise

Stage definitions versus use, dark automations, templates never sent, duplicate sends.

## Inputs

- The pipelines in scope.

A question about a client, matter or case goes to the firm connector. The user does not have to name the platform.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Read stage definitions and their use through the Lawmatics connector.
2. List stages defined but not used.
3. List automations with no recent runs, where the platform exposes them.
4. List templates never sent and messages sent twice.

## Output shape

1. Line 1: the coverage statement.
2. Section 1: stage definitions versus use.
3. Section 2: dark automations.
4. Section 3: templates never sent.
5. Section 4: duplicate sends.
6. Section: not retrieved, including parts the platform shows only in its own screens.

## Coverage statement

Every output opens with a coverage statement. It gives the scope searched, the record count, whether every page was read, and the time of the read. If the connector marks the read as incomplete, give the reason. List each item that could not be read under the heading "not retrieved". A failed or partial read is never shown as an empty result.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
- Turning an automation on or off.
