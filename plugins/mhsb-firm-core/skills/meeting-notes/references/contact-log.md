<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/claude-for-legal, legal-clinic/skills/client-comms-log/SKILL.md, commit 4a6c651889c97cc9140580363c73e0eb17379c2b.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten from the clinic append-only communications log into the contact entry that /meeting-notes drafts for a person to record: entry fields, append-only correction and the pattern checks are kept; local file writes and the clinic integrations are removed.
-->

# Contact log entry

This reference defines the contact entry that `/meeting-notes` drafts after a call, meeting or message, and the pattern checks it applies when the user asks about a matter's contact history. The plugin drafts the entry; a person records it in the firm's platform. Nothing is written by the plugin.

## Why the entry matters

- Defense of the file: a dated entry shows what the client was told and when.
- Continuity: a colleague taking over the matter reads the history instead of asking the client again.
- Supervision: a run of unreturned calls becomes visible.
- Retention: contact history is part of the client file.

## Entry fields

| Field | Content |
|---|---|
| Matter | identifier as recorded |
| Date and time | in the firm's time zone; defaults to the time of the meeting |
| Direction | inbound (client to firm) or outbound (firm to client) |
| Medium | call, email, text, letter, in person, video, voicemail left, voicemail received |
| Firm participant | the staff member or attorney |
| Other participant | the client, or a described third party such as a family member or opposing counsel |
| Length | for example, a ten-minute call or a three-paragraph email |
| Summary | two to four sentences on what happened and what was substantive |
| Firm owes | each commitment to the client, with its date |
| Client owes | each item expected from the client, with its expected timing |
| Follow-up | a date, if one was set |
| Notes | language used, interpreter, accommodation, or tone where it matters |

The draft entry is shown to the user for confirmation before anyone records it.

## Consent gate

If the source is a transcript or recording, the entry is drafted only when the record shows that consent to record was obtained as the firm's adopted rule requires. Without that record, the plugin drafts from the user's own notes and states that the transcript was not used.

## Corrections

The log is append-only. An error is corrected by a new entry that references and corrects the earlier one. The plugin never proposes editing a past entry.

## Pattern checks

When asked about a matter's contact history, the plugin reads the recorded entries and reports:

- Unanswered inbound contact: several inbound entries with no later outbound entry.
- Missed follow-up: a follow-up date passed with no later entry resolving it.
- Language gap: the client's language noted as other than English and outbound contact recorded only in English.
- Tone shift: entries recording growing frustration or distress.
- Contact gap: a long period with no contact on an active matter.
- Client threads older than two business days without a reply.

The report opens with the coverage statement and lists any entry that could not be read under "not retrieved".

## Limits

The entry is a record of contact, not legal analysis; strategy belongs in the attorney's own notes. The plugin does not import call logs, does not record entries and does not edit history.
