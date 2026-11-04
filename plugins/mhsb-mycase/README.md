# mhsb-mycase

MyCase vocabulary and field mapping for use over the vendor's own connector. Adds no commands. MHSB service-side controls do not apply to records retrieved through the vendor connector.

Release tier: ga. License: `LicenseRef-MHSB-Source-Available`. Version: 0.2.0.

Contains no commands and bundles no connector. The firm uses the vendor's own connector; MHSB label resolution, masking, role mode, audit and scheduled reports do not apply to records retrieved through it.

## Installation

/plugin install mhsb-mycase --marketplace MHSBai/platform-plugins

From a shell, after `claude plugin marketplace add MHSBai/platform-plugins#<tag>`: `claude plugin install mhsb-mycase@mhsb-platform-plugins`.

## Scope

The plugin does no legal research, drafts no filings, produces no citations, takes no trust account action, sends nothing, deletes nothing and, in version 1, writes nothing to the firm's platform. Outputs require review by a licensed attorney.
