# mhsb-lawmatics

Lawmatics platform commands: public form protection review and pipeline health. Bundles the MHSB Lawmatics connector. Read-only.

Release tier: pilot. License: `LicenseRef-MHSB-Source-Available`. Version: 0.1.0.

Bundles the MHSB Lawmatics connector (`https://mcp.mhsbsolutions.com/lawmatics`) as a remote MCP server. Every command is read-only.

This plugin is not listed in the marketplace. It is held at tier pilot until its connector passes `tools/release_check.py` (HANDOFF item 8). MHSB installs it for a named firm once the release conditions in the design are met.

## Commands

| Command | Promise |
|---|---|
| /form-protections | Public forms without protection, confirmation triggers reachable by a fake booking, and unauthenticated submit exposure. |
| /pipeline-health | Stage definitions versus use, dark automations, templates never sent, duplicate sends. |

## Scope

The plugin does no legal research, drafts no filings, produces no citations, takes no trust account action, sends nothing, deletes nothing and, in version 1, writes nothing to the firm's platform. Outputs require review by a licensed attorney.
