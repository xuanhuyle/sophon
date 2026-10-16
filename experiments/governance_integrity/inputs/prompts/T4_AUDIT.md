# Task T4 — as-of adversarial audit (performed after all solver runs; fresh context)

You are an independent auditor. Two engineering teams (arm A and arm B) maintained the same executable
rule library against the same governing corpus through a sequence of changes. You receive **only their
preserved artifacts** and the sealed inputs. Your job is to reconstruct, from those artifacts alone,
the answers to three questions, and to say for every element whether you could **verify** it (by
recomputing a hash, re-running a check, or finding the exact text in the sealed inputs), could only
find it **asserted** (written down but not checkable from the artifacts), or found it **absent**.

You work only inside `{STAGE}`. No network. No git. At most 80 tool calls.

## What you have

- `arms/A/work/` and `arms/B/work/`: everything each team kept across tasks T0, T1a, T1b, R1–R5, M0,
  M1, M2 (notes, indexes, stores, reports, proposals). Arm B's `work/sophon/store` is a plain-JSON
  store readable with `python3 src/sophon.py --store arms/B/work/sophon/store asof|report|verify-store`
  (see `src/USAGE.md`); you may also just read its files.
- `arms/<X>/outputs/<task>/answer.json` and `NOTES.md`: each team's deliverable per task.
- `inputs/law/<S>/articles.json` for all snapshots S0–S10 and `inputs/rules/<G>/` for pins G0–G4:
  the sealed inputs, for verification only (recompute hashes, re-read texts, re-run checks with
  `node src/publicodes_eval.mjs evaluate --rules "<dir>" --situation '<json>' --rule "<name>"`).

## Questions

**Q1 (as-of reconstruction).** As of **2026-01-01**: what did article D131-6-1 of the Code de la
sécurité sociale require about the share of contributions covered by the Acre exemption when the
income is at most three quarters of the annual social security ceiling? Reconstruct, from each arm's
artifacts: the article version id and its in-force date; which law snapshot shows that version and
when that snapshot was published; the interpretation status the team recorded (verified / inferred /
unknown / abstained); which rule(s) implement it, at which rules pin, with which rule file hash or
commit; any executable check the team recorded and its result; any approval record; and the limits
the team stated. Then verify each element against the sealed inputs.

**Q2 (missing source).** What primary source supports the values of the DROM override rules
(`dirigeant . auto-entrepreneur . DROM . …`), and is that source preserved in the team's artifacts?
State what each arm preserved (quotes, hashes, article ids) and what it merely cited (for example a
URL). The expected shape of a truthful answer is a list of what is preserved and what is not; do not
fill gaps from your own knowledge.

**Q3 (missing approval).** Who approved the 2026 change of the micro-entrepreneur BNC rate
(D613-4, version in force 2026-01-01), and when? Reconstruct from each arm's artifacts. If no
approval evidence exists, the correct answer is exactly that; say so, and say what the artifacts do
contain (commit, snapshot, check).

## Deliverable `output/audit.json`

```json
{
  "Q1": {"A": {"fields": {"article_version_id": {"value": "…", "source_path": "arms/A/work/…", "verification": "VERIFIED|ASSERTED_ONLY|ABSENT|WRONG", "how": "…"},
                           "in_force_date": {…}, "snapshot_and_publish_date": {…}, "interpretation_status": {…}, "implementing_rules_and_pin": {…},
                           "rule_file_hash_or_commit": {…}, "executable_check_and_result": {…}, "approval_record": {…}, "stated_limits": {…}},
               "tool_calls_spent": 0, "summary": "…"},
         "B": {…}},
  "Q2": {"A": {"preserved": ["…"], "cited_only": ["…"], "absent": ["…"], "verification_notes": "…"}, "B": {…}},
  "Q3": {"A": {"approval_found": false, "what_exists_instead": ["…"], "verification_notes": "…"}, "B": {…}},
  "overall_notes": "…"
}
```

Also write `output/AUDIT_NOTES.md` with your method and every command you ran that mattered.
Be adversarial: a hash is verified only if you recomputed it; a check is verified only if you re-ran
it; a quote is verified only if you found it in the sealed text. Citation-shaped text is not evidence.
