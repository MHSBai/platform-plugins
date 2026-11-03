<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/knowledge-work-plugins, small-business/skills/call-list/SKILL.md, commit 2574e29377c7173d0cecffef29a6ecbd7f8ccb5d.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten as a read-only call sheet for client and lead follow-up; calendar event creation and CRM stage changes removed; client threads older than two business days flagged.
-->

# Call list: who to contact today

This reference governs the call sheet that `/follow-up` produces when a user asks whom to call today. It draws on the ranking in `/intake-triage` for leads and on the connected record for open client threads. The output is a list for a person to work from. The plugin creates no calendar event, changes no record and sends nothing.

## Arguments

- Count: the number of entries, default 5, between 1 and 10.
- Date: the day the list is for, default today in the firm's time zone.

## Step 1. Gather

1. Leads: take the order produced by the lead-triage procedure (`plugins/mhsb-operations/skills/intake-triage/references/lead-triage.md`). This procedure does not re-score.
2. Clients: read open matters with a client message unanswered for more than two business days. These are listed ahead of leads of equal rank, because an unanswered client is the more serious lapse.
3. For each entry, read the last three messages in the thread, where the connector exposes them.
4. Open with the coverage statement. Any source that could not be read is listed under "not retrieved"; a failed read is never presented as an empty list.

## Step 2. Select

Select exactly the requested count when that many entries exist. Ties go to the entry with an unanswered inbound message. Where the lead-triage step reports that scores did not separate, the list follows its factual order (age of inquiry, then last contact) and says so.

## Step 3. Call card

Each entry is one card:

```
{Rank}. {Contact} ({lead or client; matter display number when a client})
Last contact: {n} business days ago | Channel: {phone, email, portal}
Reason on the list: {unanswered message, new inquiry, missing document, other}

Points for the call
- {point from the thread}
- {point from the record}
- {open question}

Purpose of the call: {one sentence}
Outcome: ______________________
```

Talking points restate what the record and thread say. They contain no legal conclusion, no deadline computed by the plugin and no settlement or fee figure unless that figure appears in the record.

## Step 4. Follow-up drafts

For each entry with an unanswered email older than three business days, a two-sentence draft is prepared: one sentence that refers to the earlier message and one that states the next step or question. Drafts are shown for review. A person sends them.

## Step 5. Time blocks

The plugin may list suggested times for the calls, taken from the connected calendar, as text. It does not create calendar entries.

## Output

1. Coverage statement.
2. The call cards in rank order, in a print-friendly layout.
3. Follow-up drafts, each labeled with its entry.
4. Not retrieved.

## Not performed

Sending email, creating calendar events, changing lead or matter status, or writing notes to the platform.
