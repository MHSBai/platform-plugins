# 0002. Adoption records in general availability packs before an attorney has adopted them

Status: accepted, 2026-11-03 (Stage 1). Items 1 and 2 superseded for the two general availability packs by decision 0004 (Stage 9); item 4 answered there.

## Problem

The lint rule requires an adoption record (adopted_by, date, version) on every template and fragment, and permits the literal `NOT ADOPTED` only in pilot and hidden packs. The personal injury and business and transactional packs are designated general availability by Catalog v2.1. No attorney has adopted either pack, and Stage 9 asks for these packs "with adoption placeholders". Read literally, the two rules cannot both hold today.

## Decision

1. The two general availability packs carry an adoption record marked `synthetic: true`, with `adopted_by: "Synthetic Adopter (fixture, not an attorney adoption)"`. The record states plainly that no adoption has occurred.
2. Rule L11 reports a synthetic record as a warning during development and as an error under `tools/lint.py --release`. docs/release.md requires `--release` to pass before a tag is cut, so neither pack can be released with a synthetic record.
3. Pilot and hidden packs carry `NOT ADOPTED` in all three fields, as the rule permits.
4. Per-firm adoption is recorded in the Firm Profile (Stage 3, `practice_areas` with adoption records). The repository record and the per-firm record are distinct; Stage 3 decides whether the repository record becomes MHSB's editorial version record or is removed.

## Alternatives rejected

Demoting the two packs to pilot would contradict the catalog. Inventing an attorney name would misstate an adoption. Permitting `NOT ADOPTED` in general availability packs would remove the gate the rule exists to enforce.

## Owner action

Richard Berman to confirm this reading, or to direct one of the alternatives, before Stage 9.
