# Jev memory probe v0 — live results

**Status: `RUN_RECORDED`, `COMPLETE`. 20/20 authorized Jev calls, executed once on 2026-10-15 (start 14:28:30Z).**

**Result: `NO_OBSERVED_LIBRARY_BENEFIT_ONE_PROBE_LOST` (component-scoped, INCONCLUSIVE about learning in general).** With the same `jev-1.13.0`, the same questions and the same source text, adding the GitHub-derived skeleton library:
- detected **0 additional** positive probes;
- **lost 1** positive probe (`B3whole:OBLIGATION`, 0.51 → 0.34);
- did **not repair** the one probe COLD already failed (`B3a:OBLIGATION`, 0.26 → 0.28).

Scope labels: `MANUALLY_CURATED_SOURCE_EXCERPTS` · `MULTI_LABEL_PER_EXCERPT` · `AUTOMATIC_SUBPROVISION_SEGMENTATION_NOT_IMPLEMENTED`. One provisional GitHub → Google transfer is not cumulative multi-contract learning, and none of this is certified legal accuracy.

## Run facts

| Item | Observed |
|---|---|
| Provider requests | 20 (10 cases × COLD/LEARNED), single pass, no retries, all HTTP 200 and schema-valid |
| Model | requested `jev-latest`, reported **`jev-1.13.0`** in all 20 responses |
| Arm parity | `score` verified every record's `request_sha256` against the frozen plan. Model, questions, clause and context are identical across arms; only `state.prior_provision_skeletons` differs (`[]` vs 3 source-linked skeletons). |
| Hashes | plan `e52eb9e0…`, questions `eebc8252…`, library `bc8086d7…`; raw recording SHA-256 `fd469bdb…` (git-ignored; see `receipt_jev_memory_20261014_approved_001.json`) |
| Tokens | COLD 15,630 in / 1,900 out; LEARNED 23,830 in / 1,900 out (**+52 % input** for the library) |
| Latency | 20 sequential calls finished within ≈4.7 s of start (≈0.23 s/call, from file timestamps; per-call latency not recorded) |
| Cost | Not reported by the API; not estimated here |

## Positive-probe outcome (16 engineering-selected source-quoted probes, pass = p ≥ 0.5)

| | COLD | LEARNED |
|---|---|---|
| Probes passed | **15/16** | **14/16** |
| Newly passed with library | — | 0 |
| Lost with library | — | 1: `B3whole:OBLIGATION` 0.51 → 0.34 |
| Failed in both | `B3a:OBLIGATION` 0.26 → 0.28 | |

The only real headroom was the clause "Customer must notify Google technical support within 30 days…" (B3a and inside B3whole). Jev reads it mainly as PERMISSION_RIGHT (0.73 / 0.89), not OBLIGATION, in both arms. The library did not correct this. In the compound passage it moved further away from OBLIGATION. A plausible, untested reading: the library's `CREDIT_CLAIM_AND_REMEDY_PROCEDURE` skeleton is hypothesised as PERMISSION_RIGHT only, so it reinforces the right-reading of a claim procedure. That is the kind of harmful template transfer the preflight warned about.

Full per-case COLD → LEARNED probabilities for all 10 labels are in `score_jev_memory_20261014_approved_001.json`.

## Unscored label behaviour (not negatives: no negative oracle exists)

- The library **was consumed**: 100 label probabilities moved (mean |Δ| 0.034 on 84 unprobed labels, max 0.21), so a null result is not an ignored-field artifact.
- The shift is small and mostly downward (mean Δ −0.012).
- Largest moves: B2b CONDITION 0.70 → 0.52; B2b EXCLUSION 0.37 → 0.19; B1a DEADLINE 0.90 → 0.69; B3b CONDITION 0.74 → 0.57.
- Unprobed 0.5-crossings: B3b OBLIGATION 0.59 → 0.47 and B3b PROHIBITION 0.46 → 0.52 (the credit-cap sentence).
- Whether any of these moves is a correction or an error is **not measurable** here.
- Literal-value transfer (GitHub 99.9 %/quarterly figures) cannot occur in this output format: Jev returns probabilities only, no quotes or values.

## Why this is not a verdict on library learning

- **n = 1 per arm, no repeat sampling.** Run-to-run noise in Jev is unknown, so a 0.51 → 0.34 move on one borderline probe cannot be separated from noise. That move is −0.17, larger than every other probed change (mean |Δ| 0.017).
- **The probes are engineering-selected positive anchors**, not independent legal labels. 15/16 COLD is near ceiling, so at most one probe could improve.
- **One library**, induced from a single GitHub SLA by an earlier pipeline (PR #17, partly from Jev's own readings), applied once. This is not a successively corrected library.
- **Jev's answers are not span-localized**: excerpt boundaries are hand-chosen, and labels apply to the whole excerpt.

## Engineering conclusion

**KEEP** the probe as a valid same-model, single-delta harness: parity verified, field consumed, cheap. **REVISE**: this provisional GitHub library gives no observed benefit on this target and slightly hurts the one compound obligation, so do not build further library updates on it unchanged. **STOP** for this paid task; any further calls need new owner approval.

## Earlier attempts (0 calls)

- 2026-10-14: `BLOCKED_NO_TYPESAFE_KEY`. A relative `--output` path guard bug was fixed.
- 2026-10-15 (attempt 2): the egress proxy denied `api.typesafe.ai`, so live mode was not started.
