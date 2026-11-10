<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/claude-for-legal, litigation-legal/skills/matter-intake/SKILL.md, commit 4a6c651889c97cc9140580363c73e0eb17379c2b.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten from the litigation matter intake into the personal injury fragment's intake completeness notes: identification, conflicts record, source, owners, preservation and key dates are kept and mapped to the injury intake; corporate risk, reserves and outside-counsel fields are removed.
-->

# Personal injury intake completeness

This note records how the personal injury fragment uses the uniform matter intake. Every injury matter is taken in through the same parts so that `/brief`, `/checklist` and the pack reports compare matters on the same fields. The note is data for the fragment; the firm's adopting attorney confirms each part at adoption.

## Parts and their injury meaning

| Part | Injury meaning |
|---|---|
| Identification | client, adverse party or parties, insurer of each party where known, loss type, forum if suit is filed |
| Conflicts record | names checked include the adverse party, the adverse insurer's insured, the driver and owner where different, and witnesses named in the intake |
| Source | how the lead found the firm (the fragment's source question), recorded for the intake source report |
| Owners | responsible attorney, case manager, and records staff where the firm assigns one |
| Preservation | letters to the adverse party or insurer asking that vehicle data, video and photographs be kept, with the date sent |
| Key dates | loss date as entered; limitation date as entered by the firm per matter type and incident-date range; any government notice-of-claim window as entered |
| Initial posture | the client's account of the loss, the adverse account where known, and the pivotal fact (for example, the signal phase or the notice of a hazard) |
| Seed documents | incident or police report, photographs, insurance cards and declarations, provider list |

## Conflicts gate

A matter whose conflicts status is "not run" is reported as a gate item in every pack view. The fragment does not mark such a matter ready.

## Dates

The limitation date is firm-set per matter type and incident-date range and recorded by the firm as its own; it governs as entered. A computed cross-check from the loss date may be shown beside it, labelled as a cross-check. A disagreement is listed and never resolved by the plugin. A government notice-of-claim window is shown only where its citation and adopter are recorded.

## Sensitive fields

Health, treatment and insurance limits are tagged sensitive. They appear in the intake completeness check as present or missing only, and are excluded from any ranking or scoring.

## What the note does not cover

Risk ratings, reserves and settlement value are not part of the intake record in this pack.
