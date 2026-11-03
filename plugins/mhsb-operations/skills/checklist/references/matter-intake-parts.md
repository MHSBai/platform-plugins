<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/claude-for-legal, litigation-legal/skills/matter-intake/SKILL.md, commit 4a6c651889c97cc9140580363c73e0eb17379c2b.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten from the ten-part litigation matter intake into the readiness parts /checklist reads per matter: identification, conflicts record and gate, source, owners, preservation, key dates and initial posture are kept as read checks; local file and log writes, risk calibration and materiality are removed.
-->

# Matter intake parts

This reference lists the parts of a complete matter intake that `/checklist` checks for each matter, alongside the document list in the practice pack fragment. Each part is reported as present, partial or missing from the record. The checklist reads; it does not complete any part and does not write to the platform.

## The parts

| Part | Present when the record shows |
|---|---|
| 1. Identification | matter name, client, opposing party, matter type, the firm's role (claimant, defendant, other), forum |
| 2. Conflicts record | status (cleared, pending, not run, waived), method, who cleared it, date, names checked |
| 3. Source | how the matter arrived: inquiry, demand letter, served complaint, subpoena, agency notice, referral |
| 4. Owners | responsible attorney, responsible staff member, and any co-counsel |
| 5. Engagement | engagement letter status (signed, sent, none) and fee model as recorded |
| 6. Preservation | whether a preservation or litigation hold notice was sent, its date, and the people it reached |
| 7. Key dates | entered response deadline, next hearing or conference, limitation date where the fragment requires it |
| 8. Initial posture | a short recorded note on the client's account, the other side's account and the pivotal fact |
| 9. Open questions | items the intake recorded as unknown |
| 10. Seed documents | the initiating document and the documents the fragment lists, each on file or requested |

## Conflicts gate

A matter whose conflicts status is "not run" is reported at the top of the checklist output as a gate item, ahead of every other part. The checklist does not suggest that work proceed on such a matter.

- "Pending" is reported with the person running the check and the expected date, where recorded.
- "Waived" is reported with a reference to where the waiver is kept.
- A recorded bypass is reported in every run until the record shows the check cleared.

The checklist reports what the record shows. Whether a conflict exists is the attorney's judgment.

## Preservation

Where the matter is active or reasonably anticipated and the record shows no preservation notice, the part is reported missing and flagged for the attorney. The checklist does not draft or send a notice.

## Dates

Key dates are entered dates only. A date the intake mentions but the record does not hold is reported as "date not established", with the source and the person who can supply it. The checklist does not compute a limitation or response date.

## Output shape

1. Coverage statement.
2. Gate items (conflicts not run, preservation missing on an active matter).
3. One row per matter: parts present, partial, missing, with counts.
4. Readiness view per matter: documents present against the fragment's list.
5. Not retrieved.
