# mhsb-firm-core

Free core plugin for law firm staff: orientation, a pre-paste confidentiality check, plain-language explanation, follow-up drafting, meeting notes, an AI policy draft for attorney adoption, role-based training and a support request. Operates without a connector.

Release tier: ga. License: `Apache-2.0`. Version: 0.1.0.

Operates without a connector. Two commands, /follow-up and /meeting-notes, use the firm connector when one is present.

## Installation

/plugin install mhsb-firm-core --marketplace MHSBai/platform-plugins

From a shell, after `claude plugin marketplace add MHSBai/platform-plugins#<tag>`: `claude plugin install mhsb-firm-core@mhsb-platform-plugins`.

## Commands

| Command | Promise |
|---|---|
| /start | Five things to do by role and practice area; what changed in this release; which packs the Firm Profile enables. |
| /before-i-paste | Category-based check before content is pasted; the check never sees the content first. |
| /explain-this | Plain-language explanation of a passage; no legal conclusions. |
| /follow-up | Next message in the firm's voice with the next step and its date; from the record when a connector is present, from pasted context otherwise; flags client threads older than two business days. |
| /meeting-notes | Matter note, tasks and a follow-up draft; a consent gate when the input is a transcript. |
| /ai-policy-draft | Decision sheet, counsel-reviewed template for the firm's state, and an adoption line. |
| /ai-training | Role lessons on what to ask, what never to paste, how to verify and how to bill. |
| /ask-mhsb | Support request packaged for MHSB; matter content refused. |

## Scope

The plugin does no legal research, drafts no filings, produces no citations, takes no trust account action, sends nothing, deletes nothing and, in version 1, writes nothing to the firm's platform. Outputs require review by a licensed attorney.

## Third-party licenses

Some files in this plugin adapt permissively licensed sources. Each such file names its source, commit and license at its top; those portions remain under their original licenses, whose texts are in this plugin's `LICENSES/` directory.
