# mhsb-clio

Clio platform commands: timekeeper hours, production by billing method and flat-fee budget versus actual. Bundles the MHSB Clio connector. Read-only.

Release tier: pilot. License: `LicenseRef-MHSB-Source-Available`. Version: 0.1.0.

Bundles the MHSB Clio connector (`https://mcp.mhsbsolutions.com/clio`) as a remote MCP server. Every command is read-only.

This plugin is not listed in the marketplace. It is held at tier pilot until its connector passes `tools/release_check.py` (HANDOFF item 8). MHSB installs it for a named firm once the release conditions in the design are met.

## Commands

| Command | Promise |
|---|---|
| /timekeeper-hours | Hourly, flat-fee and total hours per timekeeper; team totals by default. |
| /production | Billed amounts by billing method. |
| /budget-vs-actual | Budgeted hours versus recorded hours by matter. |

## Scope

The plugin does no legal research, drafts no filings, produces no citations, takes no trust account action, sends nothing, deletes nothing and, in version 1, writes nothing to the firm's platform. Outputs require review by a licensed attorney.
