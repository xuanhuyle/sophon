## Your additional tool: the sophon store (read `src/USAGE.md` first, about 80 lines)

You also have `src/sophon.py`, a small provenance store under `work/sophon/store`. Use it as your
system of record:

1. Register the law snapshot(s) and the rules pin of this task with `snapshot-law` / `snapshot-rules`.
2. Record every requirement-to-rule link you establish with `link add`, with an exact quote from the
   article and, wherever a number can be checked, an executable check (`--check-rule`,
   `--check-situation`, `--expect`). The store marks a link VERIFIED only if the check passes now; a
   link without a check can only be INFERRED or UNKNOWN; a quote that is not in the text is rejected.
3. When a task gives you a new law snapshot or a new rules pin, register it and run `revalidate`
   before you reason about the change. Its report tells you which stored links are touched
   (REASSESS_LAW_CHANGED, REASSESS_RULE_CHANGED, BROKEN, STILL_VERIFIED) and which bounded articles
   have no link at all. Treat the report as a starting point, not as the answer: it only knows the
   links you recorded.
4. Before finishing, run `report` (evidence table) and `verify-store`, and keep their outputs under
   `work/sophon/reports/`. In `output/answer.json`, add a field `"sophon_reports"` listing the report
   paths you produced for this task.

The store never approves anything and never interprets text. It records what you give it if, and
only if, it can verify the quote and run the check.
