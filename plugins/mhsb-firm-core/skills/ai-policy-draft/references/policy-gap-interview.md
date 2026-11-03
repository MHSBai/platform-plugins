<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: frblaw/ai-policy-templates, skill/customize-ai-policy/SKILL.md, commit 080ccd9946bcb676104c036eda7da89bc14aaf5f.
Original license: CC0-1.0. The original copyright and license notices are retained.
Change note: Interview and existing-policy comparison rewritten for /ai-policy-draft against the MHSB policy base, with web fetch, vendor referral and upstream contribution steps removed.
-->

# AI policy interview and gap analysis

`/ai-policy-draft` uses this procedure with `policy-base.md`. The output is a working draft or a list of recommended edits for the firm's counsel. It is never adopted by this command.

## Step 1. Mode

Ask whether the firm already has an AI policy, or a related document (acceptable use, data security, confidentiality) that covers part of the same ground.

1. No existing policy: go to Step 3 and draft from the base.
2. Existing policy: run Step 2, then Step 3 for the gaps only.

Material the firm shares is confidential. It is read in the session and is not sent to any other service.

## Step 2. Compare an existing policy

Compare the firm's policy with the base on the twelve dimensions below. For each, record: the base's position; the assumption behind it; what the firm's policy says; and one classification: aligned, weaker, stronger, missing, or conflicts. Mark a dimension not applicable only when it does not apply to the firm.

| Dimension | Assumption behind the base |
|---|---|
| 1. Scope and definitions | Embedded and agentic AI need governing, not only chat assistants |
| 2. Approved tools only | Account control and no-training terms are the main leakage risks |
| 3. Verification | Fabricated citations and facts are the signature risk of AI output |
| 4. Confidentiality and data minimization | Confidentiality is lost on the input side |
| 5. Client disclosure and consent | Clients must be told and may need to consent |
| 6. Notetakers and consent of every participant | A standard stricter than the law avoids recording-law and privilege exposure |
| 7. Agentic AI controls | Autonomy needs human confirmation before any change |
| 8. Employment decisions | Bias and legal exposure are too high to allow |
| 9. Enforcement | A policy needs consequences proportionate to the risk |
| 10. Operating program | Training, acknowledgment, a named owner and honest billing make the document work |
| 11. Jurisdiction obligations | Obligations vary by jurisdiction and are tracked by counsel |
| 12. Monitoring and incident response | Oversight needs an audit right and a reporting path |

Present the material differences first (missing, weaker, conflicts). Then walk them one at a time, most consequential first. Frame each as the firm's choice: the base assumes this, for this reason; the firm's policy does that; the firm may keep its approach, adopt the base's, or combine them. Never describe the firm's policy as wrong.

The default output is "improve the existing policy": a gap table and a list of recommended edits keyed to the firm's own sections, with replacement wording for each accepted change. A rebuild on the base is offered only if the firm asks for it.

## Step 3. Interview

Ask a few related questions at a time and say briefly why each answer matters. In comparison mode, ask only about the gaps Step 2 found.

1. Identity: the firm's legal name and the intended effective date.
2. Administrator: the one person who owns the policy, with title and contact.
3. Tools: the AI tools the firm holds on business terms; the document system of record; the videoconference and notetaker arrangements; everyday software with AI features. If the firm holds only consumer accounts, state that the base's premise requires a procurement decision first.
4. Footprint: each jurisdiction where the firm practices; any regulated data (health, financial, education). This drives Appendix B, which counsel completes.
5. Judgment calls: the consent standard for notetakers; the employment-decision posture; which violations carry the most serious consequence.

## Step 4. Draft or edit

1. Replace every placeholder. Search the draft for an opening square bracket before handing it over; list any that remain with the person who can supply each.
2. Keep the base's protections. If the firm asks to weaken one, make the change and state the risk it opens.
3. Delete sections that do not apply rather than leaving references to them.
4. Never generate a citation. Any jurisdiction entry not supplied by counsel reads "verify with counsel".
5. Keep the closing lines: not legal advice; counsel review before adoption.

## Step 5. Close

1. Counsel review: state that the draft needs review by a lawyer licensed in each of the firm's jurisdictions before adoption, with particular attention to Appendix B and the employment section.
2. Adoption: the accountable attorney adopts the policy with a name and a date; until then the decision sheet shows it as not adopted.
3. Beyond the document: a tool inventory, training records, acknowledgment collection and a recurring review are still needed. `/ai-training` covers the role lessons.
