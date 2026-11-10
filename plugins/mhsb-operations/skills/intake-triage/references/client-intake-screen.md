<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/claude-for-legal, legal-clinic/skills/client-intake/SKILL.md, commit 4a6c651889c97cc9140580363c73e0eb17379c2b.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten from the clinic intake workflow into a read-only lead screen for /intake-triage: routing, cross-area issue spotting, conflict name-match and urgency classes are kept; case acceptance, student routing and deadline-entry blocks are removed.
-->

# Client intake screen

This reference governs how `/intake-triage` screens one lead or a batch of leads read from the firm's platform. It fixes the order of the screen, the issue-spotting table, the conflict record and the urgency classes. The screen gathers and structures what the record holds. It never decides whether the firm takes the matter; that decision belongs to the attorney named in the Firm Profile.

## Order of the screen

1. Read the lead from the record. Open the output with the coverage statement: scope, record count, whether every page was read, time of the read. Items that could not be read are listed under "not retrieved".
2. Route the lead to a practice area from the facts as stated, not from the label the lead chose. A lead often knows the problem and not the legal category.
3. Apply the intake questions of the matching practice pack fragment. A question the record does not answer is listed as open, with the person who can answer it.
4. Note every issue that falls outside the routed practice area (table below).
5. Record the conflict name-match (section below).
6. Assign one urgency class and one attorney-review flag set. Propose one next action for a person to take.

## Cross-area issue spotting

The fragment questions are asked for one area. Statements in the record that point to another area are recorded as cross-area flags, whether or not the firm practices in that area.

| Statement in the record | Cross-area flag |
|---|---|
| Concern about immigration status | Immigration, even in an injury or housing lead |
| Threats or fear of a partner or family member | Family law and safety; the firm's safety protocol applies |
| Inability to work after an injury | Possible benefits or disability claim |
| Deductions from pay by a creditor | Garnishment; consumer and employment overlap |
| A threat to report the person to an authority | Possible retaliation; immigration overlap |

A cross-area flag is a note for the attorney. The firm may handle the issue, refer it, or both.

## Conflict name-match

The screen records, and never resolves, the conflict position.

- Opposing party names as stated in the record.
- Related parties named in the record (co-defendants, spouses, owners, insurers).
- Positional concern: whether the requested outcome could harm a current client, where the record shows one.
- Result of the name-match against the firm's contact list, as counts and identifiers only.

Every match, including a partial or phonetic one, is an attorney-review flag.

## Urgency classes

| Class | Meaning |
|---|---|
| Urgent | An entered date falls within days, a safety concern is stated, or irreversible harm is stated as imminent |
| Time-sensitive | An entered date falls within weeks, or harm is ongoing |
| Standard | No entered date and no stated harm |
| Possibly outside scope | The issue falls outside the firm's practice areas; flagged for referral review |

The class rests on dates entered in the record or stated by the lead. The screen does not compute a limitation period or a response window to reach a class. Where a deadline is mentioned without a date, the output reads "date not established", with the source and the person who can supply it.

## Output elements

- Bottom line for the attorney: information present, information missing, proposed next action.
- The lead's situation in the lead's own words, before any legal categorization.
- Issues in the routed area and cross-area flags.
- Key facts in a table with the source of each and whether a document supports it.
- Conflict name-match result.
- Urgency class and the entered date that drives it.
- Verification items: facts to confirm with the lead, dates to confirm from the source document rather than memory.
- Not retrieved.

## Limits

The screen does not decide acceptance, resolve a conflict, advise the lead, or write to the platform. Any citation in the output carries a provenance note, and a citation not read from a source during the session is marked for verification. Sensitive fields tagged in the fragment are excluded from any ranking.
