<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/claude-for-legal, legal-clinic/skills/supervisor-review-queue/SKILL.md, commit 4a6c651889c97cc9140580363c73e0eb17379c2b.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten from the clinic supervisor review queue into the approval rule for /letter and other client-facing drafts: named approver, approve, edit then approve and return outcomes, and the record of each decision are kept; the local queue file and teaching signals are removed.
-->

# Approval queue

This reference governs how client-facing drafts from `/letter`, the client-facing variant of `/matter-status` and `/follow-up` reach the person who approves them. Every such draft names its approver from the Firm Profile. No draft is sent by the plugin.

## Approver

The Firm Profile names the approver for each kind of client-facing output. If the profile names no approver for the kind of draft requested, the plugin asks who approves and does not proceed until a person is named. An approver cannot be inferred from a role title.

## What the approver sees

Each draft is presented with:

- The draft itself, with the review label outside the letter body.
- The template it renders, with the template's adoption record (adopted by, date, version).
- The variables filled, with the source field of each.
- Placeholders still open and items not retrieved.
- The reason the draft needs approval: client communication, a date in the text, a sensitive field, or a flag from the fragment.

Drafts that carry an entered date within the warning ladder are presented first.

## Outcomes

| Outcome | Meaning |
|---|---|
| Approved | The approver accepts the draft as presented; a person sends it from the firm's system |
| Edited then approved | The approver changes the draft; the approved text is the edited one, and the original stays beside it so the drafter sees the change |
| Returned | The approver returns the draft with a note; a revised draft is presented again |

The plugin never approves on anyone's behalf and never treats silence as approval.

## Record of the decision

The approver's decision, the date and the version of the template are stated in the output so that a person can record them in the firm's own system. This record shows that a responsible attorney reviewed the communication before it left the firm.

## Firms without a formal queue

Some firms review drafts in conversation rather than in a queue. The Firm Profile records which method the firm uses. With either method, the approver is named and the draft is not sent until that person approves.

## Limits

The plugin does not hold a queue of its own, does not notify approvers and does not send. It presents drafts for approval in the session in which they are produced.
