# 0004. Pack fragments: schema, held general availability, adoption records and date kinds

Status: accepted, 2026-11-03 (Stage 9). Supersedes decision 0002 items 1 and 2 for the two general availability packs; item 4 is answered below.

## 1. Schema

Each `fragment/fragment.yaml` is a YAML rendering of a document that conforms to the Stage 3 fragment schema (mhsb-firm-service `firm_profile/schemas/fragment.schema.json`, JSON Schema 2020-12). The schema is vendored unchanged as `tools/schemas/fragment.schema.json` (SHA-256 `9d537e09fd164f7cbd7206cb7043fd0e1b59f8d9d4225479d9099423f7aff2ac`, read from branch `cloud/pp3-firm-profile-v2` at `bfcddee`). The prompt names `schemas/fragment.schema.json`; Stage 3 placed the file under `firm_profile/schemas/`. Lint rule L15 validates every fragment against the vendored copy; `tools/validate_fragments_service.py` runs the Stage 3 validator itself (schema and `XR-*` cross rules) against a local checkout of the private repository. A change to the schema is made in the service repository first and copied here with the new hash.

## 2. General availability held at pilot

The lint permits a general availability pack only with a real attorney adoption record, and no attorney has adopted the personal injury or business and transactional fragment. Both packs therefore:

1. keep `release_tier: ga` in the fragment, which is the tier Catalog v2.1 assigns and the tier the Stage 3 rule `XR-TIER` expects;
2. carry `tier: pilot` and `catalog_tier: ga` in `catalog/manifest.yaml`, so they are unlisted in the marketplace and installed by MHSB for a named firm;
3. carry the placeholder `PENDING ADOPTION` in `fragment/adoption.yaml` and in every template's adoption frontmatter.

`catalog_tier` is accepted by `tools/manifest_lib.py` only as `ga` on a practice pack at tier `pilot`. Lint rule L11 permits `PENDING ADOPTION` only in such a held pack and `NOT ADOPTED` only in pilot and hidden packs that are not held. The Stage 3 validator reports `XR-GA-ADOPTION` and `XR-STATUTORY` on the held fragments; `tools/validate_fragments_service.py` reports them as HELD rather than as failures. Stage 11 records the adoption, sets the manifest tier to `ga`, removes `catalog_tier`, and the held findings disappear.

The synthetic records of decision 0002 are removed. A synthetic record remains a warning in development and an error under `--release`, but no file carries one.

## 3. Adoption record in two places

The schema's `adoption` object admits only `null` or a dated record; it cannot hold a placeholder string. The fragment therefore records absence as `adopted_by: null, adopted_on: null`, and the sibling `fragment/adoption.yaml` holds the lint's record (`adopted_by`, `date`, `version`), which is either the placeholder or the attorney's record. L11 requires the two to agree: a placeholder file requires null fields in the fragment, and a real record requires the same adopter, date and version in both. This answers decision 0002 item 4: the repository record is MHSB's library release record; the firm's own adoption remains in the Firm Profile `practice_areas` entry.

## 4. Statutory and firm-set

The schema has two kinds. In these fragments `statutory` means a period fixed by statute or rule, which therefore needs a citation and an adopter; `firm_set` means a date the firm sets, or enters from a court notice, order, contract or document, with no citation. Every date category has `entered_date_governs: true`. Where an adopter is absent, L15 requires the citation to begin `CITATION PENDING`, so no unconfirmed citation can read as real. MHSB supplied no citation.

Two readings follow from the Catalog's wording:

1. Civil litigation: Catalog 3.5 says answer deadlines, discovery cutoffs and appeal windows are entered from the docket and govern. Answer deadlines and appeal windows are fixed by rule and are marked `statutory` with citation placeholders (the stricter gate); discovery cutoffs come from the court's order and are `firm_set`.
2. Criminal defense and real estate: Catalogs 3.4 and 3.6 define only entered dates and forbid computed speedy-trial markers. These fragments have no statutory category, and their `/dates` eval cases assert the absence of statutory categories and computed markers instead of exercising one.

## 5. Gaps in the Stage 3 vocabularies

The fragments do not invent values outside the closed lists. Recorded for the service repository:

1. Report registry: no identifiers for speed-to-lead and conversion (criminal), deadline risk inventory (immigration), document readiness rate (bankruptcy), cross-practice handoff leakage, or automation and integration health. The criminal, immigration and bankruptcy fragments list no report.
2. Attorney-review flags: no immigration-consequences flag for criminal defense; the citizenship answer is a sensitive field for the attorney's review.
3. Sensitive tags: no tag for children or for safety-screen content (family law); the fragment records only that the safety protocol was followed and the contact rule status.
4. The PHI default (Catalog 3.1, 3.11) is a Firm Profile data rule with no fragment field.

## 6. Template identifiers

Template identifiers follow the schema pattern `^[a-z][a-z0-9_]*$` with a pack prefix (`pi_welcome`). L15 requires every `communication_templates` entry to resolve to a template file in the same pack and every template file to be referenced.
