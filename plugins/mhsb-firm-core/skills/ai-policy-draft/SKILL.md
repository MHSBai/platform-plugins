---
name: ai-policy-draft
description: 'Decision sheet, counsel-reviewed template for the firm''s state, and an adoption line. Use
  when a user asks, for example: "draft our ai policy"; "we need an ai use policy"; "ai policy for the
  firm".'
metadata:
  register: document
  connector: none
  pack: mhsb-firm-core
  triggers:
  - draft our ai policy
  - we need an ai use policy
  - ai policy for the firm
---

# /ai-policy-draft

## Promise

Decision sheet, counsel-reviewed template for the firm's state, and an adoption line.

## Inputs

- The firm's state or states of practice.
- The decisions recorded on the decision sheet: permitted tools, approved data categories, consent model, review duties and billing practice.
- The counsel-reviewed policy template for the state.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Present the decision sheet and record each answer the accountable attorney gives.
2. Fill the counsel-reviewed template with those decisions only. The template supplies all legal wording.
3. Mark every section that still needs a decision.
4. Add the adoption line for the accountable attorney.

## Output shape

1. Section 1: the decision sheet with each answer and who gave it.
2. Section 2: the policy draft rendered from the template.
3. Section 3: open decisions, if any.
4. Last line: "Adopted by: <attorney>, date: <date>, version: <version>", left blank until the attorney adopts it.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
- Writing policy wording that is not in the counsel-reviewed template.
- Marking the policy adopted. Only the attorney adopts it.

## References

Read these files in this skill's `references/` folder when the step needs them. Each one names its source and license at its top.

- `references/policy-base.md`: AI policy base.
- `references/policy-gap-interview.md`: AI policy interview and gap analysis.
