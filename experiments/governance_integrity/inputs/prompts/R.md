## Task {TASK} — reverse check of a semantic change with the governing text as given (decision date {DECISION_DATE})

The maintainers changed the rule library. The commit is in `inputs/diffs/{DIFF_ID}/` (`diff.patch`,
`stat.txt`, `meta.json`{DIFF_CONTEXT_NOTE}). The governing text is law snapshot {LAW_SNAPS}; it has
not changed as part of this event.

Decide what this semantic change is, with respect to the bounded articles:

- `HARMLESS_REFACTOR`: no change in what any bounded rule computes, or documentation/metadata only
  (show it by evaluating before and after where the engine can run both sides);
- `MISMATCH`: after the change the library computes something the governing text in force does not
  support, or still fails to compute what the text requires (give the quote, the version id, the
  engine values and the numbers you expected);
- `LEGITIMATE_INDEPENDENT_CHANGE`: a deliberate implementation choice the text does not forbid or
  that rests on a source outside the bounded set (say which);
- `UNRESOLVED`: the text available does not settle it (say exactly what is missing).

Do not call every diff a violation. Do not call a diff harmless because the numbers did not change if
what the engine computes changed. If the article the change depends on is outside the bounded set, say
so instead of guessing.

### Deliverable `output/answer.json`

```json
{
  "task": "{TASK}",
  "commit": "<sha from meta.json>",
  "label": "HARMLESS_REFACTOR|MISMATCH|LEGITIMATE_INDEPENDENT_CHANGE|UNRESOLVED",
  "confidence": "high|medium|low",
  "rationale": "<a few sentences>",
  "evidence": [{"kind": "article_quote|engine_before_after|diff_excerpt", "article": "D756-5", "article_version_id": "…", "quote_or_values": "…"}],
  "expected_values_if_mismatch": [{"rule": "<dotted>", "date": "DD/MM/YYYY", "found": 3.6, "expected": 3.9, "derivation": "<how the text gives it>"}],
  "outside_bounded_set": ["…"],
  "approval": "none recorded",
  "notes": "…",
  "self_reported_tool_calls": 0
}
```

Also write `output/NOTES.md`.
