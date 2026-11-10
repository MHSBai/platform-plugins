<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/claude-for-legal, litigation-legal/skills/portfolio-status/SKILL.md, commit 4a6c651889c97cc9140580363c73e0eb17379c2b.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten from the litigation portfolio rollup into the caseload and anomaly rules behind the /brief views: stage distribution, dated horizons, staleness and the anomaly checks are kept and restated over platform fields; risk, materiality and reserve rollups are removed.
-->

# Portfolio rollup

This reference defines the rollup that underlies the caseload, stale and missing views of `/brief`. It answers three questions for the attorney or office manager: what the firm holds open now, what needs attention, and what is slipping. The rollup reads platform fields; it decides no priority and stores nothing.

## Scope and filters

Open matters by default. Closed matters are included only on request. Filters: practice area, responsible person, stage, staleness only.

## Rollup sections

1. Coverage statement.
2. Counts: open matters; closed this year when requested.
3. By stage: count per canonical stage from the practice pack fragment, with the platform's own stage names mapped.
4. By responsible person: open matters, overdue tasks, matters with no open task.
5. Upcoming entered dates in three horizons: within 14 days, 15 to 30 days, 31 to 60 days.
6. Anomalies (below).
7. Not retrieved.

## Anomaly checks

| Check | Condition |
|---|---|
| Overdue date | an entered date has passed and the matter is open |
| Stale | no recorded activity for 30 days on an open matter |
| Conflicts unresolved | conflicts status pending or not run on an open matter |
| Conflicts bypassed | a recorded bypass exists; reported until the record shows clearance |
| Unassigned | no responsible attorney or staff member |
| Preservation gap | the matter is active or anticipated and the record shows no preservation notice, where the fragment requires one |
| Missing fields | any field the firm has chosen as required is empty |

Each anomaly lists the matter identifiers that meet it. Counts and identifiers only; no client detail beyond what the view needs.

## Closing line

One or two sentences on what stands out, written only when something does. No closing line otherwise.

## Precision

Counts are exact for the pages read. If any page was not read, the coverage statement says so, and the counts are labelled as partial. A failed or partial read is never presented as an empty result.

## Limits

The rollup is a working view, not the system of record. It does not change stages, assign owners or close matters.
