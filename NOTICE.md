# NOTICE

MHSB Platform Plugins. Copyright 2026 MHSB Solutions.

`plugins/mhsb-firm-core` is licensed under the Apache License, Version 2.0 (`plugins/mhsb-firm-core/LICENSE`). Every other plugin in `plugins/` is source-available under `LICENSE-SOURCE-AVAILABLE.md` in its own directory.

## Adapted sources

The plugin line adapts material from the permissively licensed sources below. Each adapted file carries the MHSB modification notice at its top (Apache License, Version 2.0, Section 4(b)) and has a row in `PROVENANCE.md` giving source, commit, license, date and change note. The adapted portions remain under their original licenses; the original copyright and license notices are retained in each file.

Release 0.1.0 contains no adapted file. The ledger in `PROVENANCE.md` is empty, and rows are added in Stage 2 (harvest) as files are adapted.

| Source | License | Planned use |
|---|---|---|
| anthropics/claude-for-legal (legal-clinic, litigation-legal, commercial-legal, legal-builder-hub) | Apache-2.0 | ADAPT with per-file modification notices |
| anthropics/knowledge-work-plugins (small-business, legal, customer-support, operations) | Apache-2.0 | ADAPT with per-file modification notices |
| anthropics/skills (skill-creator, mcp-builder, brand-guidelines) | Apache-2.0 | build tooling only |
| marshall1727/clio-mcp | Apache-2.0 | catalog generator pattern; no-write lint reference |
| WYRE-AI node-clio, clio-mcp | Apache-2.0 | typed errors, fixtures, elicitation pattern |
| snyk/agent-scan | Apache-2.0 | CI on the public repository only; not redistributed |
| dschnurbusch/mattergate policy package | MIT | role-mode pattern; MIT notice beside any port |
| LegalMate/hyacinth | MIT | Clio client candidate (service repository) |
| RosenAdvertising clio-mcp, lawmatics-mcp, mycase-mcp | MIT | test and audit patterns; catalog benchmark |
| oktopeak clio-mcp, lawmatics-mcp | MIT | audit redaction and read-only gating patterns |
| lasso-security/mcp-gateway presidio plugin | MIT | masking pattern reference |
| SuffolkLITLab/docassemble-AssemblyLine | MIT | intake question blocks |
| frblaw/ai-policy-templates | CC0-1.0 | policy base |

Sources under MPL, GPL or AGPL are excluded. Unlicensed repositories are used for benchmarking only and are not copied.
