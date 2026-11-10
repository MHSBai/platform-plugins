# NOTICE

MHSB Platform Plugins. Copyright 2026 MHSB Solutions.

`plugins/mhsb-firm-core` is licensed under the Apache License, Version 2.0 (`plugins/mhsb-firm-core/LICENSE`). Every other plugin in `plugins/` is source-available under `LICENSE-SOURCE-AVAILABLE.md` in its own directory.

## Adapted sources

The plugin line adapts material from the permissively licensed sources below. Each adapted file carries the MHSB modification notice at its top (Apache License, Version 2.0, Section 4(b)) and has a row in `PROVENANCE.md` giving source, commit, license, date and change note. The adapted portions remain under their original licenses; the original copyright and license notices are retained in each file.

Stage 2 (harvest, 2026-11-03) added 32 adapted files: 27 from Apache-2.0 sources (anthropics/claude-for-legal, anthropics/knowledge-work-plugins), 3 from an MIT source (SuffolkLITLab/docassemble-AssemblyLine) and 2 from a CC0-1.0 source (frblaw/ai-policy-templates). The license texts are reproduced in `LICENSES/` and, for every plugin that holds an adapted file, inside that plugin's own `LICENSES/` directory, because a marketplace install copies only the plugin directory; neither Apache-2.0 source ships a NOTICE file. The MIT copyright and permission notice is also reproduced in each MIT-derived file. Every cloned repository, with its commit, license file hash and SPDX identifier, is recorded in `harvest/LEDGER.yaml`.

The adapted portions in source-available plugins remain under their original licenses; the source-available license of those plugins applies only to MHSB's own material in them.

| Source | License | Planned use |
|---|---|---|
| anthropics/claude-for-legal (legal-clinic, litigation-legal, commercial-legal, legal-builder-hub) | Apache-2.0 | ADAPT with per-file modification notices |
| anthropics/knowledge-work-plugins (small-business, legal, customer-support, operations) | Apache-2.0 | ADAPT with per-file modification notices |
| anthropics/skills | no root license; per-folder Apache-2.0 for skill-creator, mcp-builder and brand-guidelines; docx, pdf, pptx and xlsx are proprietary | BENCHMARK only: nothing copied or redistributed |
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
