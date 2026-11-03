<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/claude-for-legal, litigation-legal/skills/legal-hold/SKILL.md, commit 4a6c651889c97cc9140580363c73e0eb17379c2b.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten from the litigation legal-hold skill into the civil litigation fragment's preservation rules: issue, refresh, release and status phases, scope inputs, departed-custodian handling and the attorney gate are kept as read and draft steps; docx generation, log writes and in-house role checks are removed.
-->

# Civil litigation preservation

This note records how the civil litigation pack treats the preservation duty. The pack's litigation hold notice is an adopted template in `templates/`; this note governs when the plugin surfaces a preservation item, what a draft draws on, and what it reports. The plugin drafts for attorney review and never sends a notice.

## Four phases

| Phase | What the plugin does |
|---|---|
| Issue | flags an active or reasonably anticipated matter with no recorded notice; on request, renders the adopted hold template with the scope inputs below |
| Refresh | flags a recorded notice whose refresh date (default six months after issue, or the firm's interval) has passed or falls within 30 days |
| Release | on request at matter close, renders the adopted release wording once the attorney confirms no appeal, reopening or related claim remains |
| Status | lists recorded notices: issue date, last refresh, next refresh, number of recipients, and attention items |

## Scope inputs for a draft

1. Categories of documents and communications, stated specifically (contracts with the other party, messages about the subject, related financial records, calendar entries).
2. Recipients: the client and the client's people likely to hold relevant material, as the attorney names them.
3. Date range: from the triggering event or earlier, through the present and continuing.
4. Systems: email, messaging, shared drives, devices including personal devices used for the matter, paper files, voicemail.
5. Effective date.

Scope is the attorney's call. Too broad a scope burdens the client; too narrow a scope invites a spoliation argument. The draft marks both scope and recipients for attorney verification.

## Attorney gate

A hold notice creates the preservation record on which the client may later be judged, and the notice itself may be discoverable. The draft carries a note, outside the notice body, that the attorney reviews, approves and sends it. Release is gated the same way, since custodians may begin deleting material once a hold is released.

## Departed recipients

Where the record shows that a recipient has left the client's organization since the last notice, the plugin reports a preservation item: that person's files and mailbox need preservation at the system level, not only by notice.

## Status attention items

- Refresh overdue.
- Refresh due within 30 days.
- Active matters without a recorded notice.
- Closed matters with a notice still active, for the attorney to consider release.

## Jurisdiction

Trigger timing, scope and sanctions for preservation vary by forum. The plugin states no preservation rule; the attorney applies the governing rule.
