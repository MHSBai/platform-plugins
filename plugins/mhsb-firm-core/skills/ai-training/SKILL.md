---
name: ai-training
description: 'Role lessons on what to ask, what never to paste, how to verify and how to bill. Use when
  a user asks, for example: "train my staff on ai"; "how should paralegals use claude"; "ai training for
  the team".'
metadata:
  register: operational
  connector: none
  pack: mhsb-firm-core
  triggers:
  - train my staff on ai
  - how should paralegals use claude
  - ai training for the team
---

# /ai-training

## Promise

Role lessons on what to ask, what never to paste, how to verify and how to bill.

## Inputs

- The learner's role: owner, associate, paralegal, intake or office manager.
- The firm's adopted AI policy, when one exists.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Confirm the learner's role.
2. Give the lesson for that role in four parts: what to ask, what never to paste, how to check the answer, and how to record time.
3. Use the firm's own policy where it exists.
4. End with three practice tasks.

## Output shape

1. Part 1: what to ask, with three examples.
2. Part 2: what never to paste.
3. Part 3: how to check an answer before use.
4. Part 4: how to record and bill the time, per the firm's policy.
5. Part 5: three practice tasks.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
- Training that conflicts with the firm's adopted policy. The conflict is reported to the attorney.
