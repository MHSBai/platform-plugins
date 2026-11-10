---
name: follow-up
description: 'Next message in the firm''s voice with the next step and its date; from the record when
  a connector is present, from pasted context otherwise; flags client threads older than two business
  days. Use when a user asks, for example: "draft a follow-up"; "write back to the client"; "what should
  i send next"; "reply to this client email".'
metadata:
  register: operational
  connector: none
  pack: mhsb-firm-core
  triggers:
  - draft a follow-up
  - write back to the client
  - what should i send next
  - reply to this client email
---

# /follow-up

## Promise

Next message in the firm's voice with the next step and its date; from the record when a connector is present, from pasted context otherwise; flags client threads older than two business days.

## Inputs

- The client or lead, and the matter.
- The thread or notes so far, from the record when a connector is present, or pasted.
- The firm's voice and sign-off from the Firm Profile.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Settle who the message is for and which matter it is about.
2. Read the last messages in the thread.
3. Flag any client thread with no reply for more than two business days.
4. Draft the next message in the firm's voice.
5. State one next step and its date.

## Output shape

1. Line 1: the approver line.
2. Line 2: who the message is for and the matter.
3. Lines 3 onward: the draft message.
4. Last lines: the next step and its date, then any thread older than two business days.

Every client-facing draft carries an approver line: "Approver: <name from the Firm Profile>". The approver is written at the top of the draft, above the first paragraph.

Every draft for a client ends with one next step and its date. If the date is not in the record, the draft says "date not established" and does not invent one.

## Coverage statement

When a connector is present and the record is used, the output opens with a coverage statement: the scope searched, the record count, and the time of the read. Items that could not be read are listed under "not retrieved". In paste mode the output says that it is based only on the pasted text.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
- Sending the message. The draft goes to a person.
