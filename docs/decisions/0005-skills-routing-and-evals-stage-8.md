# 0005. Skills to final text, routing suite and evals (Stage 8)

Status: accepted for the Stage 8 pull request; open to review. Date: 2026-11-04.

## 1. Base branch

Stages 1, 2 and 9 have not merged to `main`. The branch `cloud/pp8-skills-evals` is cut from `cloud/pp9-pack-fragments` (head adfce89), the most recent open `cloud/pp*` branch, which already contains Stages 1 and 2. Merge order: Stage 1, Stage 2, Stage 9, then this branch, rebased onto `main` after each merge.

## 2. Tools a skill calls

The service core (mhsb-firm-service, Stage 4a) registers `firm_profile_get`, `firm_export` and `service_status` on the firm server and a first set of Lawmatics and Clio reads. The skills also name read tools by tool group (`matters_search`, `contacts_search`, `intake_read`, `dates_read`, `tasks_read`, `documents_metadata_read`, `notes_metadata_read`, `communications_metadata_read`, `templates_read`, `fields_read`, `reports_read`, and the `lawmatics_*_read` and `clio_*` reads). These names are the contract that the connector stages (6 and 7) implement; a name that changes there changes here in the same release. No skill calls `report_run` or `firm_profile_change_request`: the first is called only by the owner's scheduled task (Design Section 6, route 2), the second only through an approver-confirmed change request. The eval checker treats any create, update, delete, send, submit, enable, disable or change-request tool, and `report_run`, as a write attempted.

## 3. Triggers and the routing suite

Design Section 4 requires that each of sixty ambiguous phrases resolve to exactly one skill in every supported combination. The manifest's trigger sets were extended so that every phrase in `evals/routing/phrases.yaml` contains a trigger of its expected skill and no other installed skill's trigger. Matching is a contiguous word run after lower-casing, contraction expansion and punctuation removal (`tools/routing_check.py`). The lint rule L10 still forbids any trigger that overlaps another skill's trigger.

A phrase whose expected command is not installed (for example a Clio command in a Lawmatics combination, or any operations command in the core-only combination) resolves to `/start`, which names the plugin that provides it (`start/SKILL.md`, Procedure step 8). The suite records the expected skill for each of the four command sets; the check expands them to all 895 combinations.

## 4. Exact refusals

The sentences a skill gives when it refuses, and the notices for injection and missing dates, are held once in `evals/skills/refusals.yaml`. Every SKILL.md quotes the nine universal refusals verbatim (legal research, filings, citations, trust, sending, deleting, bulk edits, any write, matter content in a support request), and every sentence its evals expect. "Refusals exact" in the Design Section 12 pass bar is checked as verbatim presence.

## 5. Eval transcripts and the pass bar

Each skill has at least six cases in `evals/skills/<skill>.yaml`, one of each kind in Design Section 12. A case carries a reference response; `tools/skill_evals.py` checks the reference against the pass bar, and `tools/model_evals.py` checks a model's response against the same function. Grounding is made checkable by a convention: each line of a client-facing draft starts with "> " and ends with a source tag, `[field: ...]`, `[template: ...]` or `[unverified]`, and an approver line precedes the draft. A date in a response counts as invented when it appears neither in the user's words, the case context, nor the case's stated date of today.

The reference transcripts prove that the expectations are satisfiable and consistent with the skill text. They do not prove that a model follows the skill; that is the model eval's purpose.

## 6. Model evals

The routing eval uses the current Sonnet identifier and the skill eval the current Opus identifier (`evals/model-config.yaml`, checked against the models page on 2026-11-04: `claude-sonnet-5-5`, `claude-opus-5-5`). Spend is capped at 40 US dollars per run. At the configured estimates a full run (240 routing requests and every skill case) is about 11 US dollars, so the cap is a guard rather than a sampling constraint; the sampling order (every routing phrase on the Lawmatics set, one case per skill, then the rest) applies if prices or estimates rise.

In this session `ANTHROPIC_API_KEY` was EMPTY. The model evals are recorded as pending with that reason (`evals/results/model-evals.json`, state/EXECUTION-LOG.md); the deterministic checks ran. CI does not hold an API key and runs the deterministic checks only.

## 7. AI policy state modules

`/ai-policy-draft` applies a state module only where a counsel-reviewed module exists. Florida and California ship with the status "state module not yet reviewed" and no legal wording. No text derived from California SB 574 is included; that waits for a decision record here stating verification against the chaptered statute.

## 8. Firm identifiers in the execution log

The Stage 9 log entry for the private denylist check named two short pilot codes in its output line. This branch rewrites that line to "two short codes" so that no identifier from the specification appears in the public repository. The check's result is unchanged.

## 9. Review XREVIEW-PP-STACK-A dispositions (2026-11-10)

PP4-M1. The deterministic results are labelled for what they show: the routing check shows trigger-list disjointness (no phrase is claimed by two installed skills' trigger sets), and the skill check shows reference-transcript conformance (the written reference answers meet the pass bar). Neither shows how a model routes or behaves; Claude selects a skill from its name and description, not from `metadata.triggers`. The CHANGELOG says so. A release is gated on the model evals: on a `v*` tag CI runs `python tools/model_evals.py --check-release`, which fails unless `evals/results/model-evals.json` records `status: ran`, every routing and skill task run, and 100 percent passed on both suites. Version 0.2.0 is not tagged until that gate passes.

PP4-L1. The spend cap is enforced per request on that request's worst case (max_tokens of output and one input token per three characters) rather than a fixed estimate, so the cap cannot be overshot. A `--budget` above 40 US dollars is clamped unless `--allow-over-cap` is given. The routing request's max_tokens is 2048 so that thinking cannot exhaust it. At worst case a full run is about 22 US dollars.

PP4-L2. `report_run` counts as a send. It stays a decoy and a write-tool match in the evals: no interactive session may call it. The scheduled task of route 2 is exempt from the session refusal for four reasons, stated also in `/report`. The owner creates the task on the owner's own account. The owner allows the tool once during the buildout sitting. In the task the model chooses only an enumerated report identifier. The service, not the model, delivers to recipients fixed in the Firm Profile (Design Section 6).

PP4-L3. The fallback citation now names `start/SKILL.md`, Procedure step 8.

The inherited findings PP1-H1, PP1-M1, PP1-M3 and PP2-M1 belong to the Stage 1 and Stage 2 pull requests and are fixed there, not on this branch.

## 10. Trigger phrases in the description (fix session FIX-PP-STACK-A, 2026-11-10)

Claude Code selects a skill from its `name` and `description` and does not act on `metadata`, so a trigger list in `metadata.triggers` could not route anything at runtime. Every trigger phrase that the manifest declares for a command is now quoted in that skill's description, in the "Use when a user asks, for example" sentence, exactly as the routing suite matches it. `metadata.triggers` is removed from all 24 skills; the manifest keeps the phrases because the generated catalog and lint rule L10 read them there. Lint rule L03 fails when a manifest phrase is not quoted in the description or when `metadata.triggers` reappears. `tools/routing_check.py` takes each skill's trigger set from the phrases quoted in its SKILL.md description, the same text the model evals send. The check now shows description-phrase disjointness: no routing phrase matches the descriptions of two installed skills, and each phrase reaches its expected skill or `/start`. It still does not show how a model routes.

The model evals recorded in `evals/results/model-evals.json` (run 2026-11-10: routing 223 of 240, skills 46 of 144) used the descriptions as they stood before this change. They must be re-run on the current descriptions, and both suites must reach 100 percent, before version 0.2.0 is tagged (Section 9).


## 11. Review XREVIEW2-PP-STACK-A dispositions (2026-11-10)

PP4-N1. Each model eval record now carries `input_digest`: sha256 over every `SKILL.md`, `evals/routing/phrases.yaml`, the skill eval files, `evals/model-config.yaml` and `catalog/manifest.yaml`, taken by sorted path and content. `--check-release` refuses a record whose digest is absent or differs from the tree. The API-1 record has no digest, and its text has since changed, so it cannot pass the gate.

PP4-N2. L06 now ends sentences only at `.`, `?` and `!`. It also grades each description with its "Use when a user asks" trigger sentence removed, against the same bound as the body (9 operational, 12 document). The 24 description promises were rewritten as short sentences. The trigger sentences are unchanged, so routing is unaffected. Grades on the lint estimator: bodies 4.0 to 5.8, descriptions 3.1 to 7.1. A cross-check with textstat could not run in the cloud session, because its pronunciation dictionary download is refused by the proxy.

PP4-N3. Open, for the owner. Merging this branch makes main list `mhsb-firm-core` 0.2.0 while the only model evidence is a failed run. The two options are (a) a model eval run on the current text that meets the Section 12 bar, or (b) an owner decision that main is a development branch not offered to firms, stated in the README and the marketplace description until a signed tag exists.
