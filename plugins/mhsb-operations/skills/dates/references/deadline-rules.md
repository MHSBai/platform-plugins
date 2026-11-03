<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/claude-for-legal, legal-clinic/skills/deadlines/SKILL.md, commit 4a6c651889c97cc9140580363c73e0eb17379c2b.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten from the clinic deadline ledger into read-only reporting rules for /dates: the do-not-compute rule, the 14, 7, 3 and 1 day warning ladder, persistent overdue status and the plausibility band are kept; the local ledger writes and add, update, complete and close modes are removed.
-->

# Deadline rules

This reference governs how `/dates` reports deadlines read from the firm's platform. The firm's platform is the record of every date. The plugin reads mapped date fields and reports them; it never writes a date, never marks a deadline complete, and never closes one. A missed deadline is the largest operational risk in a small firm, so the rules below favor early warning and persistent visibility.

## The do-not-compute rule

The plugin does not calculate a deadline from a triggering event. If a complaint was served on a given day and a rule allows a fixed number of days to answer, the attorney or staff member applies the rule and enters the resulting date in the platform. The plugin then reads that entered date.

- The entered date governs.
- A computed date appears only as a cross-check, labelled as such, and only where the fragment defines the computation as a cross-check.
- When the entered and computed dates disagree, both are listed under "disagreements". The plugin does not choose between them.
- When a field is empty, the line reads "date not established", with the source field and the person who can supply the date.

Computation rules vary by jurisdiction, court and local practice. A deadline produced by the plugin would carry a liability the plugin does not hold.

## Plausibility band

Where the practice pack fragment supplies a typical range for a category (for example, a range of days after service), the plugin compares the entered date with that range and the triggering date, if both are mapped.

- Inside the range: nothing is said.
- Outside the range by a material margin: the line is flagged "outside the typical range for this category; confirm against the governing rule". The flag is a prompt to recheck, not a correction.
- No range for the category, or no range for the firm's jurisdiction: the line carries "no plausibility band". The plugin never substitutes a range from another jurisdiction.

## Warning ladder

The default thresholds are 14, 7, 3 and 1 days before the entered date, in the firm's time zone. The Firm Profile may set other thresholds. The ladder is applied each time `/dates`, `/brief` or a scheduled report runs; the plugin does not push notifications on its own.

| Band | Contents |
|---|---|
| Overdue | Entered date has passed and the platform does not show the item complete |
| Today to 3 days | Due within three days |
| 4 to 7 days | Due within a week |
| 8 to 14 days | Due within two weeks |
| Beyond 14 days | Count only, expanded on request |

An overdue item stays in the overdue band in every report until the platform records it as complete or closed. The plugin never clears it.

## Report shape

1. Coverage statement.
2. Counts: active, overdue, due within seven days.
3. One table per band: matter, category, entered date, source field, responsible person, days remaining or days overdue.
4. Workload by responsible person: overdue, next 7 days, next 14 days, total active.
5. Grouping by practice area.
6. Deadlines with no responsible person.
7. Disagreements between entered and computed dates.
8. Date not established.
9. Not retrieved.

## Category marking

Every category from the fragment is marked either statutory, with its citation and the adopting attorney, or firm-set. A statutory category without an adopted citation is shown with the note "citation not adopted".

## Limits

The plugin does not compute deadlines, override local rules, file, serve, notify, or change any field. Changes to a date, its owner or its status are made by a person in the platform.
