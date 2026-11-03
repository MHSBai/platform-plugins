<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/claude-for-legal, legal-clinic/skills/client-letter/SKILL.md, commit 4a6c651889c97cc9140580363c73e0eb17379c2b.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten from the clinic routine-letter templates into rendering rules for /letter: the routine-only scope, required elements per letter type, the plain-language check and the review label kept outside the letter are retained; student sign-off and template bodies are replaced by the firm's adopted templates.
-->

# Client letter rules

This reference governs how `/letter` renders routine client correspondence from the firm's adopted templates. It defines the scope, the required elements of each routine type, the plain-language check and the review steps. The letter text itself always comes from a template the firm has adopted; this reference does not supply letter wording.

## Scope

Routine correspondence only: appointment confirmations, document requests and short procedural updates. The following are outside the scope of a template letter and are refused with a note to the attorney:

- Substantive advice, or anything that tells the client what the firm thinks of the case.
- Bad news: an adverse ruling, a decision to decline or withdraw, a matter closing for cause.
- Correspondence to opposing counsel, a court or any third party.

## Required elements by type

| Type | Required elements |
|---|---|
| Appointment confirmation | date, time and time zone; place or call details; the person the client meets; documents to bring; how to reschedule and the notice required |
| Document request | each document by plain name; how to deliver it; the date needed and the reason for that date; whom to contact if a document is unavailable |
| Short update | one line on what happened and when; one line on what happens next; what the client needs to do, or a statement that nothing is needed now |

A required element the record does not supply is left as a visible placeholder and listed for the reviewer. The plugin does not invent it.

## Variables

Variables are filled from the record and the Firm Profile only. Each filled variable is listed under the draft with its source field. A variable that could not be read is listed under "not retrieved".

## Plain-language check

- Short sentences and common words.
- A legal term is explained the first time it appears.
- Reading level within the limit the Firm Profile sets for client letters.
- The firm's adopted AI disclosure sentence, where the template carries it, is left unchanged.

## Review label

The draft carries a review label for the reviewer, placed above the letter and outside its body. The label is never part of the client copy. If a review label, a placeholder or a verification marker would remain in the client copy, the draft is incomplete.

## Before the letter leaves the firm

1. The approver named in the Firm Profile reviews the draft (see the approval queue reference).
2. All review labels and placeholders are removed.
3. The signature block matches the firm's adopted signature for the sender.

The plugin never sends the letter. A person sends it from the firm's own system.

## Refusals

An unadopted template, a template without an adoption record, or a request outside the routine scope is refused with the reason.
