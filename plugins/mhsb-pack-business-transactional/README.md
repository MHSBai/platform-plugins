# mhsb-pack-business-transactional

Business and transactional practice fragment: intake questions, attorney-review flags, document list, stage map, deadline categories, template references and report entries. Data only; adds no commands.

Release tier: ga. License: `LicenseRef-MHSB-Source-Available`. Version: 0.1.0.

Contains no commands. The fragment in `fragment/fragment.yaml` is merged into the Firm Profile and is overridden by the firm's own answers. Templates in `templates/` carry adoption records; the generator fills variables only.

## Installation

/plugin install mhsb-pack-business-transactional --marketplace MHSBai/platform-plugins

From a shell, after `claude plugin marketplace add MHSBai/platform-plugins#<tag>`: `claude plugin install mhsb-pack-business-transactional@mhsb-platform-plugins`.

## Scope

The plugin does no legal research, drafts no filings, produces no citations, takes no trust account action, sends nothing, deletes nothing and, in version 1, writes nothing to the firm's platform. Outputs require review by a licensed attorney.
