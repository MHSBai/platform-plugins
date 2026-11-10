<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/claude-for-legal, legal-clinic/skills/status/SKILL.md, commit 4a6c651889c97cc9140580363c73e0eb17379c2b.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten from the clinic audience-aware status skill into the internal and client-facing variants of /matter-status: audience rules, inclusions and exclusions are kept; the court-ready variant and student assessment are removed because filings are outside the read-only line.
-->

# Status variants

This reference defines the two variants of `/matter-status`: internal and client-facing. Both use the same facts from the record; they differ in reader, depth and register. Both open with the coverage statement and list any record that could not be read under "not retrieved".

## Internal variant

Reader: the responsible attorney or staff member. Knows the law and the matter; wants position, movement and decisions needed.

Contents, in order:

1. Header: matter identifier, practice area, stage as recorded, responsible person, date of the read.
2. Since the last update: activity recorded since the date of the previous status or the last stage change, most recent first.
3. Upcoming: entered dates only, each with category and source field, in a table of date, item and who acts.
4. Decisions needed: open questions recorded on the matter, and gaps the fragment marks as required.
5. Data gaps: fields the firm has chosen as required that are empty.

The internal variant does not assess the merits. Where the user asks for an assessment, the output leaves a marked section for the attorney to write.

## Client-facing variant

Reader: the client, often under stress and unfamiliar with procedure. Reading level within the Firm Profile limit for client correspondence.

Contents:

- What has happened since the client last heard from the firm, in plain words.
- What happens next and when, using entered dates only.
- What the client needs to do, or a statement that nothing is needed now.
- How to reach the firm.

Excluded from the client-facing variant:

- Legal analysis.
- Weaknesses in the matter, which are a conversation for the attorney.
- Terms of art without explanation.
- Any field outside the client-facing allowlist in the Firm Profile.

The client-facing variant renders only through an adopted template, names the approver from the Firm Profile, and carries a review label outside the letter body. The plugin does not send it.

## Choosing the variant

When the request does not say who will read the status, the plugin asks. A request that names the client, or asks for an update "to send", is client-facing. Everything else defaults to internal.

## Court-ready status

A status report for a court is outside the read-only plugin line. The request is refused with a note that court filings are prepared and reviewed by the attorney.

## Limits

The variants report status; they do not decide what the client is told about bad news, do not recommend strategy and do not write to the platform.
