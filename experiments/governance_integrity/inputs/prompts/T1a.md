## Task T1a — forward transposition after a governing change (decision date {DECISION_DATE})

A new law snapshot has arrived ({LAW_SNAPS}). The rule library is still at pin {RULES_PIN}. Compare the
new snapshot with what you knew (your `work/` directory holds what you kept from the previous task;
the previous snapshot's articles are not re-supplied, so rely on what you preserved).

1. Identify every bounded article whose version id, text or announced future versions changed, with
   the modifying text named in `lienModifications` and the in-force dates.
2. For each rule in the bounded set, classify it `AFFECTED`, `UNAFFECTED` or `NEEDS_REVIEW` with
   respect to this change, with evidence.
3. For the affected rules, propose the change in a disposable copy
   (`work/proposals/T1a/modele-social/règles`), run the native `build`, and `evaluate` the changed
   rules on **2024-06-01, 2024-07-01, 2025-01-01 and 2026-01-01** (liberal BNC situation above; also
   BIC service, vente, and Cipav where you can), showing value before and after and the article quote
   that justifies each value. **If the text available to you does not state a value for a date,
   abstain for that date and say so explicitly.**

### Deliverable `output/answer.json`

```json
{
  "task": "T1a",
  "changed_articles": [{"article": "D613-4", "from_version_id": "…", "to_version_id": "…", "in_force_from": "YYYY-MM-DD", "modifying_text": "<from lienModifications>", "what_changed": "<one sentence>", "new_text_available": true}],
  "rules": [{"rule": "<dotted>", "classification": "AFFECTED|UNAFFECTED|NEEDS_REVIEW", "confidence": "high|medium|low", "evidence": ["<quote or engine result>"]}],
  "proposal_dir": "work/proposals/T1a/modele-social/règles",
  "build_ok": true,
  "evaluations": [{"rule": "<dotted>", "date": "DD/MM/YYYY", "situation": {…}, "value_before": 21.1, "value_after": 23.1, "expected_from_text": 23.1, "quote": "<exact substring>", "article_version_id": "…"}],
  "abstentions": [{"rule": "<dotted>", "date": "DD/MM/YYYY", "reason": "<why the text does not settle the value>"}],
  "approval": "none recorded",
  "notes": "…",
  "self_reported_tool_calls": 0
}
```

Also write `output/NOTES.md`.
