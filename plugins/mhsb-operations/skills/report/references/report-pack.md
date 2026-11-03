<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/knowledge-work-plugins, small-business/skills/report-pack/SKILL.md, commit 2574e29377c7173d0cecffef29a6ecbd7f8ccb5d.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten for the firm report catalog; report definitions come from the Firm Profile, scheduled delivery is an MHSB service, and every report carries coverage, data gaps and provenance lines.
-->

# Report pack: the firm's recurring reports as one briefing

This reference governs how `/report` assembles a firm's recurring reports into one briefing. The reports themselves are defined in the report catalog and selected in the Firm Profile. This procedure adds context and a fixed delivery shape. Scheduled delivery, where the firm has elected it, is performed by the MHSB Reports Service under the firm's authorization scope; the plugin itself schedules nothing and sends nothing.

## Step 1. Run the selected reports

1. Read the report selection from the Firm Profile. A report that is selected is run without asking the user to describe it again. Re-asking for a definition already recorded is a defect.
2. A report not yet in the Firm Profile is described once, confirmed once by the user, and run. Adding it to the profile follows the profile change process.
3. Each report computes over API fields in the firm's time zone, and carries:
   - the coverage statement (scope, record count, pages read, time of read);
   - a data-gaps section (records lacking the fields the report needs);
   - a provenance line per row (record identifier and field);
   - for any dated report, one counsel-review line at the top.

## Step 2. Add context

After the reports run, a short context section is added for the same period: open matter count and change, oldest unanswered client message, any matter past the firm's stage-age threshold, and the single item that most needs attention. The context section introduces no figure that does not appear in a report or in the record.

## Step 3. Deliver as one briefing

One output, in this order:

1. The headline figures from each report, each with its comparison period.
2. The context section in two or three lines.
3. The report tables.
4. Data gaps across all reports.
5. Not retrieved.

Two separate deliverables for one period are not produced.

## Step 4. Cadence

A cadence is offered once, after a run the user found useful, and only where the firm has elected the Reports Service. On a yes, the request is recorded for MHSB as a service delivery item; nothing is scheduled from the plugin. On a no, the offer is not repeated.

## Step 5. Incomplete data

A report is never withheld because one source failed. The affected figure reads "not retrieved", the source is named and the remaining reports are delivered. A silent omission reads as a fault in the service.

## Not performed

Scheduling, sending email, writing to the platform, or including note bodies, billing or time entries in any report the authorization scope excludes.
