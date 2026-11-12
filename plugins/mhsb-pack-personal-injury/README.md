# mhsb-pack-personal-injury

Personal injury practice fragment: intake questions, attorney-review flags, document list, stage map, deadline categories, template references and report entries. Data only; adds no commands.

Release tier: pilot. Held from general availability (catalog tier ga) until an attorney adoption is recorded; see `fragment/adoption.yaml` and docs/decisions/0004. License: `LicenseRef-MHSB-Source-Available`. Version: 0.1.0.

Contains no commands. The fragment in `fragment/fragment.yaml` is merged into the Firm Profile and is overridden by the firm's own answers. Templates in `templates/` carry adoption records; the generator fills variables only.

## Installation

This plugin is not listed in the marketplace while it is held at pilot. MHSB installs it for a named firm; it returns to the listing when the adoption record names the attorney adopter (Stage 11).

## Scope

The plugin does no legal research, drafts no filings, produces no citations, takes no trust account action, sends nothing, deletes nothing and, in version 1, writes nothing to the firm's platform. Outputs require review by a licensed attorney.

## Adapted fragment sources

The fragment is accompanied by `fragment/intake-blocks.yaml`, `fragment/sources/chronology.md`, `fragment/sources/matter-intake.md`. Each file names its source, commit and license in its header and has a row in the repository's `PROVENANCE.md`.

## Third-party licenses

Some files in this plugin adapt permissively licensed sources. Each such file names its source, commit and license at its top; those portions remain under their original licenses, whose texts are in this plugin's `LICENSES/` directory.
