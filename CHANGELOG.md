# Changelog

Each entry describes what changed for the people who use the plugins at a firm. Version numbers follow the plugin versions in the marketplace.

## 0.2.0 (2026-11-04)

This release gathers the Stage 2, Stage 8 and Stage 9 changes below. It still reads nothing from a firm's records until the MHSB connectors are in service.

What changes for staff:

- Every command now has its full instructions. Each one says what it promises, what it reads first, the steps it follows, the exact shape of its answer, what it refuses, who approves a draft, and how it states the next step and its date. Each has worked examples from an invented firm.
- Ask in your own words. You do not need to know the command name or say which platform a matter is in. Sixty everyday phrases, such as "what's due this week", "anything stale" or "write back to Mrs. Alvarez", are quoted in the descriptions that Claude reads to choose a command, and no two commands claim the same phrase. Claude did not yet pick the right command for every phrase when first tested on 2026-11-10, and the descriptions have changed since that test; this version is not released until a new test shows the right command for every phrase. If a phrase needs a command your firm does not have, /start is written to say which plugin provides it.
- The commands ask before they guess. If two clients or matters could match, or a date is missing, the command asks or writes "date not established". It never makes up a date.
- Answers say what they could not read. Every answer from the firm's records opens with what was searched and when, and ends with a "Not retrieved" line. A partial read is never shown as a complete one.
- Refusals use the same plain sentence everywhere, so staff can recognise them.
- /report can now set up a weekly or daily report that the MHSB service emails to the people named in the firm's profile. It gives the owner the exact text to paste into a scheduled task on the owner's own Claude account.
- /ai-policy-draft uses the base policy for every state. The Florida and California additions are marked "state module not yet reviewed" until counsel has reviewed them.

Behind the scenes: each command has six test conversations (an ordinary request, an unclear person, a missing date, a record that contains hidden instructions, a request it must refuse, and a partial read). The automatic checks pass, but they check that the phrases quoted in the command descriptions do not overlap and that the written example answers meet the rules; they do not show how Claude behaves. The tests that use a Claude model first ran on 2026-11-10: 223 of 240 routing cases and 46 of 144 command conversations passed. Version 0.2.0 is not released until both pass in full on the current text.

What the plugins never do is unchanged: legal research, filings, citations, trust account actions, sending messages, deleting, bulk edits, or writing to the firm's platform.

## Included in 0.2.0: Stage 9 (2026-11-03)

All twelve practice packs now carry a complete or draft fragment in the shape the Firm Profile accepts: structured intake questions, attorney-review flags, the document list, a stage map to the canonical stages, the fee model, date categories marked statutory or firm-set, template references, consent rules, sensitive fields kept out of scoring, pack views and pack reports. No fragment states a citation; each statutory category waits for the adopting attorney to confirm one.

The personal injury and business packs are complete but are not yet in the marketplace listing. They return to it when an attorney adopts them. The six hidden packs each list the questions an attorney in the practice must answer first. The family law draft refuses any outreach draft unless the record carries a verified contact rule.

Pack evals check that the fragments support the date, intake, checklist and brief promises. Nothing changes in what the plugins never do.

## Included in 0.2.0: Stage 2 (2026-11-03)

The commands now draw on rewritten material from permissively licensed sources: intake screening, deadline reporting rules, letter rules and the approval step, matter status variants, contact records, brief views, report covers, the setup runbook, the start routing, and the AI policy base. The personal injury, civil litigation and business packs gain reusable intake question blocks and, for the first two, chronology, briefing and preservation notes. Each adapted file names its source and license at its top. Nothing changes in what the plugins never do.

## 0.1.0 (2026-11-03)

First structure of the plugin line. Nothing in this release reads or changes a firm's records yet, because the MHSB connectors that the commands use are built in later stages.

What a firm will see once the connectors exist:

- A free core plugin with eight commands for every member of staff. It explains how to start, checks whether something is safe to paste, explains a passage in plain words, drafts a follow-up, turns a call into notes, drafts an AI policy for the attorney to adopt, gives role-based training, and packages a support request.
- An operations plugin with eleven read-only commands for subscribing firms. Briefs, consultation preparation, matter status, intake triage, letters from adopted templates, dates, document checklists, data hygiene, reports, a register check and a setup check.
- One plugin per platform. Lawmatics adds two commands, Clio adds three, and MyCase adds vocabulary only.
- Twelve practice-area packs. They add no commands. They supply the questions, document lists, stages and date categories that the commands use. Two are ready for general use once an attorney adopts them; four are pilot only; six stay hidden until an attorney in the practice helps design them.

No firm sees more than 22 commands, whatever its practice mix.

What the plugins never do: legal research, filings, citations, trust account actions, sending messages, deleting, or writing to the firm's platform.
