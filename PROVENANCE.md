# PROVENANCE

Per-file ledger of every file in this repository that vendors or adapts third-party material. `tools/lint.py` (rule L12) reads the Ledger table below and fails when a listed file lacks the modification notice at its top or when a ledger field is empty.

## Policy

VENDOR (use code) and ADAPT (rewrite text) only from Apache-2.0, MIT, BSD, ISC or CC0 sources, with the license copy, retained notices and, for Apache-2.0 Section 4(b), a prominent modification notice in each modified file. BENCHMARK (compare coverage, copy nothing) for unlicensed repositories, recorded as "idea reference, written without the source open, similarity diff reviewed". MPL, GPL and AGPL are excluded. Client-specific or engagement-derived content is never published.

## Modification notice template

Placed at the top of every adapted file. In a file with YAML frontmatter, such as `SKILL.md`, the notice follows the closing `---` of the frontmatter, because the frontmatter must open on the first line. In Python or YAML files the same lines are written as `#` comments.

```
<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on YYYY-MM-DD.
Original: OWNER/REPOSITORY, PATH, commit FULL_SHA.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: ONE SENTENCE DESCRIBING THE CHANGE.
-->
```

For an MIT source, the `Original license:` line reads `MIT` and the original MIT copyright and permission notice is reproduced directly below the notice.

## Ledger

Columns: file (repository-relative path), source (owner/repository and path), commit (full SHA), license (SPDX), date (YYYY-MM-DD), change note.

| File | Source | Commit | License | Date | Change note |
|---|---|---|---|---|---|

Release 0.1.0: no rows. Every skill in this release was written for this repository.
