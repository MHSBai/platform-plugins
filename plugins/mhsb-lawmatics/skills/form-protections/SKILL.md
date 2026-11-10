---
name: form-protections
description: 'Public forms without protection, confirmation triggers reachable by a fake booking, and
  unauthenticated submit exposure. Use when a user asks, for example: "are our intake forms protected";
  "public form exposure"; "can someone submit a fake booking".'
metadata:
  register: operational
  connector: platform
  pack: mhsb-lawmatics
  triggers:
  - are our intake forms protected
  - public form exposure
  - can someone submit a fake booking
---

# /form-protections

## Promise

Public forms without protection, confirmation triggers reachable by a fake booking, and unauthenticated submit exposure.

## Inputs

- The scope: all public forms, or named forms.

A question about a client, matter or case goes to the firm connector. The user does not have to name the platform.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Read the public forms through the Lawmatics connector.
2. List forms that have no protection against automated submits.
3. List confirmation triggers that a fake booking could reach.
4. List submit paths that need no sign-in.

## Output shape

1. Line 1: the coverage statement.
2. Section 1: forms without protection.
3. Section 2: confirmation triggers reachable by a fake booking.
4. Section 3: submit paths open without sign-in.
5. Section: recommended changes, each with the click path for a person to follow.
6. Section: not retrieved.

## Coverage statement

Every output opens with a coverage statement. It gives the scope searched, the record count, whether every page was read, and the time of the read. If the connector marks the read as incomplete, give the reason. List each item that could not be read under the heading "not retrieved". A failed or partial read is never shown as an empty result.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
- Submitting a test form or booking.
