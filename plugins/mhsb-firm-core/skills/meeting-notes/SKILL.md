---
name: meeting-notes
description: 'Matter note, tasks and a follow-up draft; a consent gate when the input is a transcript.
  Use when a user asks, for example: "turn this call into notes"; "meeting notes"; "summarize this consultation";
  "tasks from this meeting".'
metadata:
  register: operational
  connector: none
  pack: mhsb-firm-core
  triggers:
  - turn this call into notes
  - meeting notes
  - summarize this consultation
  - tasks from this meeting
---

# /meeting-notes

## Promise

Matter note, tasks and a follow-up draft; a consent gate when the input is a transcript.

## Inputs

- Notes or a transcript of a call or meeting.
- The matter it belongs to.
- Whether every person on the call agreed to be recorded.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. If the input is a transcript, ask whether all parties consented to the recording. Stop if the answer is no or not known.
2. Write a short matter note: who, when, what was decided.
3. List the tasks, each with an owner and a date.
4. Draft a follow-up message for the approver to review.

## Output shape

1. Line 1: the matter and the meeting date.
2. Section 1: the matter note.
3. Section 2: the tasks, one per line, with owner and date.
4. Section 3: the follow-up draft, with the approver line.

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
- Using a transcript when consent to record is not confirmed.

## References

Read these files in this skill's `references/` folder when the step needs them. Each one names its source and license at its top.

- `references/contact-log.md`: Contact log entry.
