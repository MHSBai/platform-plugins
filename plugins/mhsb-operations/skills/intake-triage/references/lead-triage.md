<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/knowledge-work-plugins, small-business/skills/lead-triage/SKILL.md, commit 2574e29377c7173d0cecffef29a6ecbd7f8ccb5d.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten for law-firm intake; CRM scoring fields replaced by fragment criteria, declines replaced by attorney-review flags, sensitive fields excluded from scoring, and all writes and enrichment removed.
-->

# Lead triage: ordering inbound leads for review

This reference governs how `/intake-triage` orders open leads. The criteria come from the practice pack fragment and the Firm Profile. The result is an ordered list with attorney-review flags and one recommended action per lead. The plugin never declines a lead, never changes a lead's status and writes nothing to the platform.

## Step 1. Read leads

1. Read open leads from the connected platform: leads not yet converted to a matter and not closed, in the firm's time zone.
2. Exclude existing clients and closed or converted leads.
3. Open the output with the coverage statement (scope, count, pages read, time of read). Anything unreadable is listed under "not retrieved".
4. Where the platform returns no leads of any status, say that the lead list is empty. Do not infer a filtering fault from an empty account.
5. Where no connector is configured, a pasted or exported list may be ordered by the same method; the output states that it was prepared from supplied data.

## Step 2. Score

Four dimensions, each from the record only:

| Dimension | Basis |
|---|---|
| Fit | Case type, jurisdiction and service area against the fragment |
| Time pressure | Stated hearing or court date, incident date, words such as "deadline" or "served" in the inquiry text; read from the note body, not inferred from a note count |
| Engagement | Replies and completed questionnaires in the last 30 days |
| Age | Days since the inquiry; older unanswered leads rise |

A lead touched by a person within the last 24 hours is moved down, because it has been attended to today.

Fields tagged sensitive in the fragment (for example health, treatment, citizenship or immigration status, criminal history, national origin, protected class) are excluded from every dimension. They may appear in the record; they never affect the order.

## Step 3. Check separation

When the highest and lowest composite scores differ by fewer than 10 points, the record does not support a ranking. The output says so and orders by facts instead: stated time pressure first, then age of inquiry. A false ranking directs staff to the wrong person.

## Step 4. Flags

Each lead may carry one or more attorney-review flags, never an automatic decline:

- possible limitation or deadline issue
- outside the firm's case types
- outside jurisdiction or service area
- conflict name match (counts and identifiers only)
- prior counsel of record

The conflict reminder records that a name in the lead matched a name in the record. It does not clear or decide a conflict.

## Step 5. List

List size follows volume: all leads up to 10; the top 5 from 11 to 30; the top 8 above 30. Each entry gives the lead identifier, case type as stated, composite score, flags, a one-paragraph summary of what the inquiry said, last activity, and one recommended action (call, request a missing item, route to an attorney for review). Where all engagement signals are older than 30 days, the entry is marked as stale.

## Step 6. Drafts on request

On request, one follow-up draft per selected lead is prepared in the firm's voice and shown for review. Nothing is sent.

## Not performed

Declining a lead, marking a lead unqualified, changing stage or owner, creating calendar events, sending messages, purchasing or running third-party enrichment, or writing any value back to the platform.
