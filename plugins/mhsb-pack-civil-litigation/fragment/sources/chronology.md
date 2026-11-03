<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/claude-for-legal, litigation-legal/skills/chronology/SKILL.md, commit 4a6c651889c97cc9140580363c73e0eb17379c2b.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten from the litigation chronology skill into the civil litigation fragment's chronology rules: the disclosed-document use check, privilege posture gate, merged events, side framing, significance tiers, gaps and versioning are kept; eDiscovery connectors and file writes are removed.
-->

# Civil litigation chronology

This note defines how the civil litigation pack assembles a chronology of a dispute for attorney review. The chronology is the spine for a statement of facts, mediation preparation and witness preparation. It is built only from the record and the documents the attorney identifies, and it is a working draft.

## Use of disclosed documents

Before documents obtained through disclosure or discovery are used, the attorney confirms that the use falls within the proceeding in which they were produced, or that a protective order, consent or public filing permits it. Without that confirmation, the chronology is not built from those documents.

## Privilege posture

The attorney states one posture before extraction: cleared, mixed or unscreened (every entry flagged ok, flag or review, with flag as the default for any uncertain case), or stop until screened. The posture is recorded in the header. The chronology inherits the privilege of its sources and stays within the firm.

## Side framing

The underlying timeline is neutral. Significance depends on the firm's side, which the record or the attorney supplies:

- For the claimant: key events establish elements of the claim, close gaps the defense will argue, or fix when the claim accrued.
- For the defendant: key events break an element, support an affirmative defense, or bear on timeliness or jurisdiction.

The framing applied is stated at the top of the chronology.

## Rules

1. One event per occurrence, with all sources cited.
2. Every entry has a source: attachment, production number, note or field.
3. No supplement from general knowledge or outside search; thin periods are reported as gaps.
4. Contradictions are entered side by side and marked for the attorney.
5. Docket dates appear as entered; the chronology computes no deadline.
6. Matter history (internal steps such as holds and engagement) is kept apart from the chronology of the dispute unless the attorney adds an item.

## Significance tiers

Key, relevant and background, with key reserved for events that would move a factfinder. A borderline event takes the lower tier with a note.

## Variants

- Working chronology: complete, tiered, flagged.
- Statement of facts outline: key and relevant events in narrative order with record citations; entries flagged for privilege are excluded unless the attorney includes them expressly.
- Witness chronology: events in which a named witness sent, received, attended or is the subject.

## Gaps and versions

The gaps section lists date ranges without events, expected documents not on file, and sources not retrieved. A rebuild states what changed since the prior version: new events, events with added sources, and any removed entry with the reason.
