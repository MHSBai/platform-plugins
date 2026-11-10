# MHSB Platform Plugins

Claude plugin line for solo and small United States law firms on Lawmatics, Clio or MyCase, maintained by MHSB Solutions and offered as a buildout plus a per-firm subscription. The specification is held privately by MHSB. This repository holds no client names, tenant identifiers or secrets, and all sample content is synthetic.

## Layout

| Path | Contents |
|---|---|
| `catalog/manifest.yaml` | The one authoritative manifest: plugins, commands, release tiers, trigger phrases, combinations |
| `catalog/counts.md` | Command counts per supported combination (generated) |
| `docs/catalog.md` | Human-readable catalog (generated) |
| `.claude-plugin/marketplace.json` | Marketplace `mhsb-platform-plugins` (generated; general availability plugins only) |
| `plugins/` | Seventeen plugins: core, operations, three platform plugins, twelve practice packs |
| `tools/gen_manifest.py` | Generator for every derived file |
| `tools/lint.py` | Catalog and content lint, rules L01 to L14 and L16 |
| `tools/release_check.py` | Connector endpoint check (recorded edge, certificate, authenticated MCP initialize with the recorded server identity) run before a connector plugin is listed |
| `tests/` | Lint tests, one failing fixture per rule |
| `docs/decisions/` | Recorded decisions, including deltas from the plugin documentation |
| `docs/release.md` | Release controls and steps |
| `state/` | Project state and execution log |

## Use

The marketplace is added in Claude Code with `claude plugin marketplace add MHSBai/platform-plugins#<tag>`; plugins are then installed by name, for example `claude plugin install mhsb-firm-core@mhsb-platform-plugins`. Connected plugins require a Claude Team or Enterprise plan and an MHSB subscription.

## Checks

```bash
pip install -r requirements-dev.txt
python tools/gen_manifest.py --check
python tools/lint.py
python -m pytest -q
claude plugin validate .
```

## License

`plugins/mhsb-firm-core` is licensed under Apache-2.0. Every other plugin is source-available: readable and installable, not licensed for reuse or redistribution, and used under the MHSB Plugin Subscription Agreement. A MyCase firm without a subscription may also use `mhsb-mycase` under an MHSB AI Policy and Training buildout agreement. Each notice is generated from `catalog/templates/license-source-available.md`. See NOTICE.md and PROVENANCE.md.
