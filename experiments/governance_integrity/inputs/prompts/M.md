## Task {TASK} — change maintenance: a new law snapshot arrived (decision date {DECISION_DATE})

Two law snapshots are provided this time, the one you had ({LAW_PREV}) and the new one ({LAW_NEW}).
The rule library is at pin {RULES_PIN}. Your `work/` directory holds whatever you kept from the earlier
tasks on this system; use it.

1. Determine which bounded articles changed between the two snapshots (version id, text, in-force
   dates, modifying text). If nothing relevant changed, say so: that is a complete and correct answer.
2. For every bounded rule, classify `AFFECTED` / `UNAFFECTED` / `NEEDS_REVIEW` with evidence. State
   explicitly which rules you did **not** need to re-examine and why (what evidence lets you say so).
3. For affected rules, propose edits in `work/proposals/{TASK}/modele-social/règles`, run `build`,
   and `evaluate` before and after at the dates the new text makes relevant, each value justified by an
   exact quote and a version id. Abstain where the text does not settle a value.
4. If you keep persistent records, update them so that the next change can be handled from them.

### Deliverable `output/answer.json`

Same shape as T1a (`task: "{TASK}"`), plus:

```json
  "reassessed_rules": ["<rules you re-examined>"],
  "not_reassessed_rules": [{"rule": "<dotted>", "reason": "<what evidence lets you skip it>"}],
  "no_change_needed": false
```

Also write `output/NOTES.md`.
