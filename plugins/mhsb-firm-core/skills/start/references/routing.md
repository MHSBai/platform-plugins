<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/knowledge-work-plugins, small-business/skills/smb-router/SKILL.md, commit 2574e29377c7173d0cecffef29a6ecbd7f8ccb5d.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten as the routing table for the MHSB command surface; the small-business routes are replaced by the core, operations and platform commands, and pack availability is read from the Firm Profile.
-->

# Routing: from an open request to one command

This reference governs how `/start` answers an open request ("what can you do", "where do I begin", "help with this matter") by recommending one command. `/start` routes; it does not perform the work of the command it recommends.

## Step 1. Read the context

Read the enabled packs and the user's role mode from the Firm Profile. A command from a pack that is not enabled, or a command the role mode excludes, is never recommended. Where the profile is absent, only core commands are offered and the user is referred to `/ask-mhsb` for setup.

## Step 2. Match the request

One best match is chosen, not a list. Where two are close, the more time-sensitive concern wins.

| The user says something like | Route to |
|---|---|
| "can I paste this", "is it safe to put this in" | `/before-i-paste` |
| "what does this mean", "explain this letter" | `/explain-this` |
| "write back to the client", "who do I owe a reply" | `/follow-up` |
| "write up the meeting", "notes from the call" | `/meeting-notes` |
| "we need an AI policy" | `/ai-policy-draft` |
| "train the staff on AI" | `/ai-training` |
| "ask MHSB", "something is not working" | `/ask-mhsb` |
| "what is on today", "what is stale", "caseload" | `/brief` |
| "prepare for the consultation", "hearing prep" | `/consult-prep` |
| "where is this matter", "status for the client" | `/matter-status` |
| "new leads", "who should we call back" | `/intake-triage` |
| "draft the letter", "decline letter" | `/letter` |
| "what deadlines are coming up", "court dates" | `/dates` |
| "what documents are missing" | `/checklist` |
| "clean up the fields", "duplicate contacts" | `/hygiene` |
| "run the weekly report" | `/report` |
| "does this sound like us" | `/on-brand` |
| "is everything connected", "check my setup" | `/check-setup` |
| Lawmatics: "are our forms protected" | `/form-protections` |
| Lawmatics: "are the automations working" | `/pipeline-health` |
| Clio: "hours per timekeeper" | `/timekeeper-hours` |
| Clio: "production by billing method" | `/production` |
| Clio: "budget versus actual" | `/budget-vs-actual` |

Pairs that sound alike: "who should we call back" about new leads goes to `/intake-triage`; about existing clients, to `/follow-up`. "Status" for one matter goes to `/matter-status`; across all matters, to `/brief`.

## Step 3. Recommend

One command, one sentence of reason, and a request to confirm before it runs. Where the request spans two commands, the more urgent is named first and the second is mentioned.

## Step 4. "What can you do"

For a user with no prior session, take the onboarding path (`references/onboarding.md`). Otherwise group the enabled commands by purpose (client communication, intake, matters and dates, reports, setup and support), lead with the group matching the user's role, and give one example phrase per command.

## Step 5. Missing connector

Where the best command needs a connector that is not active, say so before running anything, name the connector by category, and give the fallback (pasted text or an exported file) where the command has one. A command that would partly fail is never run silently.

## Step 6. No match

If no command fits, say so plainly and give the overview in Step 4. A capability that does not exist is never claimed. Legal research, filings, trust actions and platform writes are outside the plugin line in every combination.
