<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/claude-for-legal, legal-clinic/skills/client-intake/SKILL.md, commit 4a6c651889c97cc9140580363c73e0eb17379c2b.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten from the clinic intake summary into the one-page shape for /consult-prep: the narrative, key-facts table, conflict section, urgency and verification prompts are kept; clinic supervision and deadline-entry blocks are removed.
-->

# Consultation preparation shape

This reference fixes the one-page shape that `/consult-prep` produces from the record before an initial consultation, and the same shape when a hearing is prepared. The page assembles what the record already holds for the attorney. It does not advise the client and does not decide whether the firm accepts the matter.

## Sources

The page is built from the lead or matter record, the intake answers, the practice pack fragment and the Firm Profile. The coverage statement opens the page. Any record or attachment that could not be read is listed under "not retrieved". Nothing is filled in from general knowledge of the matter.

## The page

1. Header: matter or lead identifier, practice area and any cross-area flags, the consultation date as entered, and the attorney named in the Firm Profile.
2. Bottom line: three short lines on what is known, what is missing and what the attorney is asked to decide.
3. The situation in the client's words, kept apart from the legal categorization so that the attorney reads the account before the analysis.
4. Key facts, one row each:

| Fact | Source in the record | Document on file |
|---|---|---|
| fact as recorded | intake answer, note or attachment | on file, or requested |

5. Gaps: fragment questions the record does not answer, each with the person who can answer it.
6. Conflict reminder: the opposing and related parties named in the record and the result of the name-match, as counts and identifiers. The page states that the conflict decision is the attorney's.
7. Dates: entered dates only, each with its source field. A date mentioned but not entered reads "date not established".
8. Conversations to hold: the fee model in the fragment and the disclosures the firm has adopted (for example, the AI disclosure sentence, recording consent, limited scope), each named by its adopted template.
9. Verification items: facts to confirm with the client, dates to confirm from the source document, and any legal point in the notes treated as a hypothesis to research.

## Hearing preparation

For a hearing, the same shape applies with three substitutions: the bottom line names the hearing and its entered date; the gaps section lists documents the fragment requires for that hearing type; and the conversations section lists what the client needs to bring and the attendance details as entered.

## Register

Short declarative sentences. Legal terms carry a plain explanation the first time. The page is marked as a draft for attorney review. Privileged material on the page inherits the privilege of its source, and the page is kept in the firm's own file store.

## Limits

The page does not compute deadlines, assess the merits, quote fees beyond the adopted fee model, or write anything to the platform.
