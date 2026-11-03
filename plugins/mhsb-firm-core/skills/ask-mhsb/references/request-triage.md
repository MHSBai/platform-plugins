<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/knowledge-work-plugins, customer-support/skills/ticket-triage/SKILL.md, commit 2574e29377c7173d0cecffef29a6ecbd7f8ccb5d.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten as the categorization and priority scheme /ask-mhsb applies when packaging a support request to MHSB; routing tiers, duplicate ticket linking and auto-responses removed, and a refusal of matter content added.
-->

# Request triage: packaging a support request for MHSB

This reference governs how `/ask-mhsb` categorizes, prioritizes and packages a firm user's support request for MHSB. The package describes the problem with the plugin line, the connector or the service. It never contains matter content: no client names, matter facts, document text, note bodies or record values. If the user's description contains matter content, `/ask-mhsb` says so, removes nothing on the user's behalf, and asks the user to restate the request without it.

## Step 1. Parse the request

Extract:

- The problem: what the user is experiencing.
- The symptom: the command used, the message shown, the time it occurred.
- The scope: one user or several; one command or all.
- Urgency: whether work is blocked, and whether a scheduled report or a client-facing date depends on it.

## Step 2. Category

| Category | Signals |
|---|---|
| Defect | an error, wrong output, a command that used to work and no longer does |
| How-to | how to do something with an existing command |
| Request | a command, view, report or template the firm does not have |
| Sign-in and access | connector sign-in, attestation, role mode, a pack not visible |
| Profile | a Firm Profile value that is wrong or out of date |
| Reports Service | a scheduled report not received, late or incomplete |
| Security | suspected exposure of client data, an unexpected write, a message that appears to impersonate MHSB |
| Data | a figure that does not match the platform |

Where a sign-in failure is caused by a defect, the category is Defect: the cause decides the category. Where in doubt between Defect and How-to, the category is Defect.

## Step 3. Priority

| Priority | Criteria | MHSB response target |
|---|---|---|
| P1 | Suspected client data exposure; any write to the platform; all users blocked | same business day, first hour where possible |
| P2 | A core command blocked for several users; a scheduled report missed; no workaround | within four business hours |
| P3 | One user affected, or a workaround exists | within one business day |
| P4 | How-to, requests, cosmetic issues | within two business days |

The priority rises when the request has waited past its target, when the same problem is reported by more than one user, or when a workaround stops working. Security reports are P1 regardless of the user's estimate.

## Step 4. Package

```
Request: {one-line summary}
Category: {category} | Priority: {P1 to P4}: {one-line reason}
Firm: {firm identifier from the Firm Profile}
User role: {role mode}
Command and version: {from /check-setup}
When: {date and time, firm time zone}
What happened: {two or three sentences, no matter content}
What was expected: {one sentence}
Workaround: available | none | unknown
Already tried: {steps the user took}
Matter content: none included (confirmed by the user)
```

## Step 5. Confirm and hand over

The package is shown to the user, who confirms that it contains no matter content and sends it through the firm's agreed support channel. The plugin does not send it.

## Not performed

Sending the request, attaching files, including screenshots of matter data, or diagnosing a platform problem that lies with the platform vendor.
