# V3: masked contract-structure prediction (offline pilot)

**Question:** Do training-only conditional frequencies over *contract family → section function → provision type* (plus evidenced governing law where it varies) rank **masked** sections and provisions better than GLOBAL and FAMILY frequency baselines?

**Status:** done offline with 0 provider calls.
- Pre-registered primary: **`INCONCLUSIVE`**. Two heldout documents failed segmentation.
- Post-freeze repaired secondary: **`PREDICTIVE_SIGNAL_PROVISIONAL`**. The signal is limited to *provision-within-section* ranking; there is no section-level gain over FAMILY, Brier is worse than GLOBAL, and law was untestable.

See [RESULTS.md](RESULTS.md).

| File | Role |
|---|---|
| [PROTOCOL.md](PROTOCOL.md) | Pre-registration: sources, split, targets, masking, arms, metrics, decision rule. Frozen in `e205a3b` before heldout. |
| [PRIOR_ART.md](PRIOR_ART.md) | One-page gate: ClauseRec, LEDGAR, CUAD, Material Contracts Corpus. |
| `extract.py`, `labels.py`, `corpus.py` | Structure extraction, frozen label rules, record builder. Raw docs stay local. |
| `predict.py` | Arms, masking, tie-aware scoring, negative controls, decision rule (`--mode dev/heldout`). |
| `secondary.py` | **Post-freeze** segmentation repair run (labeled secondary). |
| `llm_baseline.py`, `RUNBOOK_V3_LLM_BASELINE.ps1` | Optional STRONG_LLM_CONTEXT arm. **NOT RUN.** ≤8 calls, operator-only, typed YES. |
| `data/` | Source manifest (URLs, accession, SHA-256), train / heldout / secondary structural records (headings and labels only). |
| `frozen/freeze_receipt.json` | Hashes of code, protocol and train data at freeze time. Four files were hashed as Windows CRLF working copies; `.gitattributes` pins them to CRLF on checkout, and `freeze_receipt_lf_normalized.json` (added post-freeze) gives platform-neutral hashes of the same content. |
| `results/` | `dev_loo.json` (train-only), `heldout_run.json` (primary), `secondary_repaired_run.json`, `posthoc_no_conflict_backoff.json` (diagnostic only). |
| `test_v3.py` | Offline tests with synthetic fixtures. They test plumbing, not predictive value. |
| [`adjudication/`](adjudication/REVIEW_PACKAGE.md) | **Human-adjudication package for the 8 secondary heldout cases** (added after the results; `AWAITING_HUMAN_ADJUDICATION`). Frozen results unchanged. |

The V2 post-run review for this branch is in [../jev_library_transfer_v2/V2_POSTRUN_REVIEW.md](../jev_library_transfer_v2/V2_POSTRUN_REVIEW.md).
