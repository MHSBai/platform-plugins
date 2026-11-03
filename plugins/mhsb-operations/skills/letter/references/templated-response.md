<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/knowledge-work-plugins, legal/skills/legal-response/SKILL.md, commit 2574e29377c7173d0cecffef29a6ecbd7f8ccb5d.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten for law-firm client and third-party correspondence; in-house inquiry categories replaced by firm letter categories, escalation triggers restated as refusals to render, and template creation tied to the adoption record.
-->

# Templated response: when an adopted template may be used

This reference governs how `/letter` decides whether a templated reply may be rendered, and how the record variables are filled. `/letter` renders only templates the firm has adopted (adopted by, date, version). Every rendered letter is a draft that the named approver reviews and a person sends.

## Step 1. Identify the category

| Category | Typical templates |
|---|---|
| Client routine | welcome, status, document request, appointment confirmation, no-show and reschedule |
| Prospective client | not-a-fit notice, decline and refer |
| Matter events | preservation instructions, litigation hold notice, scope letter, event update |
| Closing | closing letter with file retention notice |
| Third party | records request cover, insurer acknowledgement of receipt |

If the user does not name a category, the adopted templates for the matter's practice area are listed and the user chooses.

## Step 2. Load the adopted template

The template is taken from the firm's document register through the Firm Kit. Where no adopted template exists for the category, `/letter` says so and stops. It does not compose a substitute letter. A request for a new template is referred to MHSB through `/ask-mhsb` and follows the adoption process.

## Step 3. Check for conditions that preclude a template

Before rendering, the request is checked against these conditions. If any applies, no templated letter is rendered; the condition is named, the reason given, and the matter is referred to the responsible attorney.

Conditions for every category:

- The recipient is a court, a government agency, a regulator or law enforcement.
- The recipient is an opposing party or opposing counsel, unless the template was adopted for that recipient.
- The letter would state a deadline, waive a right, accept or reject an offer, or commit the firm to a course of action not already recorded.
- The matter involves possible criminal exposure for the client, unless the template is from the criminal defense pack.
- The record shows a safety or contact restriction, or the contact rule is unknown (family law and similar packs).
- The situation is not one the template's "use when" lines describe.

Additional conditions by category:

- Prospective client decline: a possible limitation issue is flagged (the attorney decides the wording of any limitation warning).
- Preservation or hold notice: the scope is unclear or disputed, or an earlier hold exists for the matter.
- Third-party records request: the request concerns psychotherapy notes or other records the fragment marks as separate.
- Any category: a subpoena, a demand or a regulatory inquiry is involved. These always go to an attorney.

## Step 4. Fill the variables

Variables come from the record only. Each variable is filled, or the letter is not rendered and the missing variable is listed with its source field and the person who can supply it. Dates are those entered in the record; none is computed. Names, matter numbers and the signature block are taken from the record and the Firm Profile.

## Step 5. Register

The letter keeps the adopted wording. The plugin does not rephrase adopted text. Where the template allows a free-text paragraph, that paragraph is written plainly, in the firm's voice, and contains no legal conclusion.

## Output

```
Draft: {template name}, version {n}, adopted by {name} on {date}
To: {recipient from the record}
Subject: {from the template}

{rendered body}

Precluding conditions: none found | {conditions found and referral}
Missing variables: none | {list with source and owner}
Approver: {name from the Firm Profile}
After sending: {follow-up actions listed in the template}
```

## Template metadata expected in the register

Category, name, version and last-review date, adopter, "use when" conditions, "do not use when" conditions, variables with their source fields, subject line, body, and follow-up actions. A template lacking adoption metadata is treated as unadopted.

## Not performed

Sending, creating an email draft in the mailbox, setting calendar reminders, composing a letter where no adopted template exists, or editing adopted wording.
