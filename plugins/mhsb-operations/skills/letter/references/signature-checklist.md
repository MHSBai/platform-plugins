<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/knowledge-work-plugins, legal/skills/signature-request/SKILL.md, commit 2574e29377c7173d0cecffef29a6ecbd7f8ccb5d.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Reduced to the pre-signature checklist and signing-order record for documents rendered by /letter; envelope creation and sending for signature removed.
-->

# Signature checklist: readiness before a person sends for signature

This reference governs the pre-signature section `/letter` appends when a rendered document (an engagement letter, a limited-scope agreement, a closing statement) will be signed. The plugin checks and lists. It never creates an e-signature envelope and never sends a document for signature; a person at the firm does both in the firm's own signing tool.

## Step 1. Identify the document

The document is the output of `/letter` from an adopted template, or a file the user supplies. The template's adoption record (adopted by, date, version) is stated at the top of the checklist. A document from an unadopted template is refused by `/letter` before this step.

## Step 2. Pre-signature checklist

```
Pre-signature checklist: {document title}
[ ] Rendered from an adopted template; adoption record stated
[ ] Every record variable filled; no placeholder remains
[ ] Client named correctly; for an entity client, the entity named as the client
[ ] Signature blocks match the persons who will sign, with titles where an entity signs
[ ] Fee terms match the Firm Profile fee model for the practice area
[ ] Required disclosures present for the practice area (for example a limited-scope statement or the adopted AI disclosure sentence)
[ ] Dates entered or left blank for the execution date; none computed by the plugin
[ ] Attachments and schedules listed and present
[ ] Approver named, and the approver has reviewed the final form
```

Each unchecked item is listed with the reason. The checklist reports PASS only when every item is checked.

## Step 3. Signing order

The checklist records, as text for the person who will send:

| Order | Signer role | Signs for | Notes |
|---|---|---|---|
| 1 | Client or authorized signatory | Client | Entity title where applicable |
| 2 | Responsible attorney | Firm | Countersignature where the firm requires one |

Whether signing is sequential or parallel, and who receives the executed copy, follows the firm's procedure as recorded in the Firm Profile. Where it is not recorded, the checklist asks.

## Step 4. Output

1. Document title, type and the adoption record.
2. Pre-signature check: PASS, or the open items.
3. Signing order table.
4. Next step for the person who sends: the firm's signing tool, and the follow-up interval if the document is not signed.

## Notes

The most frequent defect is an incorrect party name; for entity clients, the entity's exact registered name is compared with the record. Authority to sign for an entity is the firm's determination, not the plugin's.

## Not performed

Creating envelopes, placing signature fields, sending for signature, filing the executed copy or giving legal advice on the document's terms.
