# mhsb-clio

Clio platform commands: timekeeper hours, production by billing method and flat-fee budget versus actual. Bundles the MHSB Clio connector. Read-only.

Release tier: ga. License: `LicenseRef-MHSB-Source-Available`. Version: 0.2.0.

Bundles the MHSB Clio connector (`https://mcp.mhsbsolutions.com/clio`) as a remote MCP server. Every command is read-only.

## Installation

/plugin install mhsb-clio --marketplace MHSBai/platform-plugins

From a shell, after `claude plugin marketplace add MHSBai/platform-plugins#<tag>`: `claude plugin install mhsb-clio@mhsb-platform-plugins`.

## Commands

| Command | Promise |
|---|---|
| /timekeeper-hours | Hourly, flat-fee and total hours per timekeeper; team totals by default. |
| /production | Billed amounts by billing method. |
| /budget-vs-actual | Budgeted hours versus recorded hours by matter. |

## Scope

The plugin does no legal research, drafts no filings, produces no citations, takes no trust account action, sends nothing, deletes nothing and, in version 1, writes nothing to the firm's platform. Outputs require review by a licensed attorney.
