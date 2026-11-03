# 0003. Lint semantics for trigger overlap and reading level

Status: accepted, 2026-11-03 (Stage 1).

Trigger overlap (L10). Phrases are lower-cased and stripped of punctuation. Two skills collide when one claims a phrase equal to, or a contiguous word run of, a phrase another skill claims ("anything stale" collides with "is anything stale this week"). The check runs across all skills in the line, which is stricter than per combination; Lawmatics and Clio commands never share an installation, but a collision between them would still be reported. The sixty-phrase routing suite in Stage 8 tests model routing; this rule tests only the declared phrases.

Reading level (L06). Flesch-Kincaid grade, 0.39 x (words per sentence) + 11.8 x (syllables per word) - 15.59, computed on the SKILL.md body after removing frontmatter, code blocks, inline code, HTML comments, URLs and table rows. Each heading and list item counts as a sentence. Syllables are estimated with a vowel-group heuristic, which is approximate; the limits (9 operational, 12 document) carry enough margin that the approximation does not decide a result. The grade of every skill is printed by `python tools/lint.py` only on failure; the Stage 1 execution log records all twenty-four.

Banned phrases (L05). Applied to user-facing text: plugin READMEs, SKILL.md files, license notices, fragments, templates, the root README and CHANGELOG, and the descriptions in plugin.json and marketplace.json. Words match on word boundaries, so "adjust" does not match "just". Tool source, tests and decision records are outside the scope, because they must name the rules they enforce.

Firm names. The public-repository rule bars pilot firm names. The lint does not carry a denylist, because a list of names, or of hashes of short names, would itself disclose them. The zero-hit check runs from outside the repository (HANDOFF item 5).
