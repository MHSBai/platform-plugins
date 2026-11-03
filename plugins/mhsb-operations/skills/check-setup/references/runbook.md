<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/knowledge-work-plugins, operations/skills/runbook/SKILL.md, commit 2574e29377c7173d0cecffef29a6ecbd7f8ccb5d.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten as the fixed runbook shape that /check-setup uses for its checks and for the remedy text it hands to the firm's administrator; knowledge-base publishing and ticketing integration removed.
-->

# Runbook shape for setup checks

This reference governs the structure `/check-setup` uses for each check it runs and for the remedy it gives when a check fails. Each check is a short runbook a non-technical administrator can follow. `/check-setup` reads state; it changes no setting and signs in to nothing.

## Checks covered

Sign-in to the firm connector; the user's attestation; enabled packs; the role mode; the Firm Profile hash; plugin versions; scheduled reports and their last run (where the firm has elected the Reports Service).

## Runbook shape per check

```
Check: {name}
Owner: {firm administrator, MHSB, or the user}
Last verified: {date and time in the firm's time zone}

Purpose
{one sentence: what the check confirms and why it matters}

Prerequisites
[ ] {access the person needs}
[ ] {tool or page the person needs}

Procedure
1. {exact action, naming the screen or menu}
   Expected result: {what the person should see}
   If it differs: {what to do}
2. ...

Verification
[ ] {how to confirm the remedy worked: rerun /check-setup}

Escalation
| Situation | Contact | Method |
| {when the remedy does not work} | MHSB | /ask-mhsb |
```

## Rules for the procedure text

1. Each step names one action and the exact place it is taken ("Settings, Connectors, the firm connector, Sign in"), not a general instruction.
2. Each step states the expected result and the action if the result differs.
3. No step asks the user to paste a credential, token or matter content into the conversation.
4. No step instructs a change to platform data. Setup remedies concern sign-in, plugin installation and profile requests only.
5. A failure the firm cannot remedy (a profile hash mismatch, an expired authorization scope, a missed scheduled run) escalates to MHSB through `/ask-mhsb`, with the check name and time but no matter content.

## Troubleshooting table

Each check carries a short table of known symptoms:

| Symptom | Likely cause | Remedy |
|---|---|---|
| Connector reads return nothing | Sign-in expired | Sign in again; rerun the check |
| A pack command is missing | Pack not enabled in the Firm Profile | Request through `/ask-mhsb` |
| Profile hash differs from the recorded hash | Profile changed outside the change process | Escalate through `/ask-mhsb` |
| Scheduled report not received | Run missed or delivery failed | Escalate through `/ask-mhsb` with the report name and date |

## Output

1. Coverage statement for the checks (which ran, which could not run, time).
2. One line per check: PASS or FAIL.
3. For each failure, the runbook in the shape above.
4. Not retrieved: any check that could not be read.
