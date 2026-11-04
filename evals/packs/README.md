# Pack evals

Contract cases for the practice-pack fragments (Stage 9). Each GA and pilot fragment (personal injury, business and transactional, estate planning and probate, criminal defense, civil litigation, real estate) has four cases:

| Skill | What the case proves |
|---|---|
| `/dates` | a statutory category carries a citation placeholder and counsel review, a firm-set category does not, the entered date governs, a disagreeing cross-check is listed and not resolved, and an unmapped or empty field derives nothing |
| `/intake-triage` | sensitive fields are excluded from scoring (the case also re-scores with the sensitive answers changed and expects the same score and action), signals raise attorney-review flags, and no lead is declined |
| `/checklist` | documents present versus the fragment's list, with required gaps blocking readiness |
| `/brief` | a pack view declared by the fragment returns rows from the mapped anchoring field, data gaps for matters without it, and the coverage statement |

The family law draft adds three outreach-gate cases: no contact rule, a rule without a verifier, and a verified rule.

Criminal defense and real estate have no statutory category (Catalog 3.4 and 3.6); their `/dates` cases assert that no statutory category and no computed marker exists (decision 0004).

Run:

```bash
python tools/pack_evals.py
```

`tools/pack_evals.py` holds a deterministic reference evaluator for the fragment-driven part of each promise. It is not the skill and calls no model; it fails a case when the fragment cannot support the promise. Model-graded evals of the skills themselves belong to Stage 8. All case data is synthetic.
