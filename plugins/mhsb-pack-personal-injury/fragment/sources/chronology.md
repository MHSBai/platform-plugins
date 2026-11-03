<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/claude-for-legal, litigation-legal/skills/chronology/SKILL.md, commit 4a6c651889c97cc9140580363c73e0eb17379c2b.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten from the litigation chronology skill into the personal injury fragment's chronology rules: the privilege posture gate, one event per merged source set, significance tiers, gaps, and the no-supplement rule are kept and mapped to injury records; document-platform connectors and file writes are removed.
-->

# Personal injury chronology

This note defines how the personal injury pack assembles a chronology of a matter from the record for attorney review: the loss, treatment, records requests, insurer contact and offers. The chronology is a working draft. It is built only from what the record and its attachments hold.

## Privilege posture

Before any event is extracted, the attorney states the privilege posture of the sources:

- Cleared: the sources have been screened; entries carry no privilege flag.
- Mixed or unscreened: every entry carries a flag of ok, flag or review. Any uncertain case is marked flag, because under-marking is the error that cannot be undone.
- Stop: the sources are screened first and the chronology is built afterwards.

The posture is recorded in the chronology header. A chronology derived from privileged material inherits that privilege and stays within the firm.

## Event types in an injury matter

| Type | Typical source |
|---|---|
| Loss | incident or police report, intake answer |
| Treatment | provider records and bills: first visit, referrals, imaging, therapy, gaps in care |
| Records | dates of each records request and receipt |
| Insurer contact | claim opened, recorded statement requested, coverage position, offers and responses |
| Employment | dates off work and return, from wage-loss proof |
| Filing | suit filed, served, answer, as entered from the docket |

## Rules

1. One event per occurrence. Where several documents record the same occurrence, the event is entered once with every source cited.
2. Every entry names its source: the attachment, the note or the field. An event without a source in the record is not entered.
3. No supplement. Where the record is thin for a period, the chronology says so in the gaps section. It does not fill the period from general knowledge or public sources.
4. Contradictions stay visible. When two sources give different dates for one event, both are entered and marked; the attorney resolves them.
5. Dates as recorded. The chronology computes no limitation date; it shows the entered limitation date where the record holds one.

## Significance tiers

- Key: part of the pivotal fact, or a fact on liability, causation or damages.
- Relevant: context or pattern, such as a gap in treatment.
- Background: completeness only.

Key is reserved for events that would move a factfinder; a borderline event takes the lower tier with a note for the attorney.

## Shape

Header (matter, date built, source count, entry counts by tier, privilege posture), timeline table (date, event, tier, privilege flag, sources), key events with a line on why each matters, gaps (periods without records, expected records not on file, sources not retrieved), and version history.

Health and treatment detail is sensitive; it appears in the chronology for the attorney and is excluded from any scoring or client-facing view.
