# mhsb-lawmatics

Lawmatics platform commands: public form protection review and pipeline health. Bundles the MHSB Lawmatics connector. Read-only.

Release tier: ga. License: `LicenseRef-MHSB-Source-Available`. Version: 0.1.0.

Bundles the MHSB Lawmatics connector (`https://mcp.mhsbsolutions.com/lawmatics`) as a remote MCP server. Every command is read-only.

## Installation

/plugin install mhsb-lawmatics --marketplace MHSBai/platform-plugins

From a shell, after `claude plugin marketplace add MHSBai/platform-plugins#<tag>`: `claude plugin install mhsb-lawmatics@mhsb-platform-plugins`.

## Commands

| Command | Promise |
|---|---|
| /form-protections | Public forms without protection, confirmation triggers reachable by a fake booking, and unauthenticated submit exposure. |
| /pipeline-health | Stage definitions versus use, dark automations, templates never sent, duplicate sends. |

## Scope

The plugin does no legal research, drafts no filings, produces no citations, takes no trust account action, sends nothing, deletes nothing and, in version 1, writes nothing to the firm's platform. Outputs require review by a licensed attorney.
