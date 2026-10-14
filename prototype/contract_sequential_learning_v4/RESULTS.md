# V4 sequential learning on authentic EDGAR credit agreements: RESULTS

**Status: RUN COMPLETE. Frozen verdict `STOP: NO_OBSERVED_CUMULATIVE_GAIN`.** 2026-10-14. **Provider calls: 0.**

**Scope of the verdict:** primary metric only; the mechanical *textual-proxy* features of §3 on 24 masked subsections of 6 evaluation agreements, 2024 H1 8-K EX-10 credit agreements. It does not cover legal meaning, other contract families, BI/agent value or LLM quality (PROTOCOL §7).

## Execution record

- **Environment.** Claude cloud session, after the owner enabled SEC egress and set `SEC_USER_AGENT` in the environment settings. The value is not recorded anywhere in this repository.
- **Preflight, shortly before 2026-10-14T14:12Z.** `efts.sec.gov`, `www.sec.gov` and `data.sec.gov` all returned proxy CONNECT 200 and HTTP 200.
- **Frozen pipeline, run unchanged.** The freeze gate passed (no frozen file changed). Commands, in order:
  1. `python -m unittest test_v4 -v` → 9/9 OK.
  2. `python v4_corpus.py fetch --raw-dir raw` (2026-10-14T14:12:34Z–14:17:11Z) → `OK: 8 accepted, 306 screened`. It made 4 search requests; their SHA-256 values are in `data/source_manifest.json`.
  3. `python v4_corpus.py build --raw-dir raw` → 8 views; bodies were written to `local_hidden/` (gitignored).
  4. `python v4_sequential.py run`.
  5. `python v4_sequential.py replay`, in a fresh process → `replay_identical_sealed_predictions: true`, chain head `58796ccc4b6cdb5bc1102da9023f05a01a6f17475f516e64ffff9f859320a932`.
- **No deviations.** No protocol, selection rule, target logic, source URL or frozen code was changed. No document was hand-selected or replaced.

## Corpus (content-blind, frozen eligibility rule)

| Doc | Role | Filed | Accession | Exhibit | Issuer |
|---|---|---|---|---|---|
| CA4-01-1109354 | SEED | 2024-01-19 | 0000950170-24-005565 | EX-10.1 | Bruker Corp |
| CA4-02-1539838 | SEED | 2024-03-06 | 0001140361-24-011751 | EX-10.2 | Diamondback Energy |
| CA4-03-751364 | EVAL | 2024-04-17 | 0000950170-24-045141 | EX-10.1 | NNN REIT |
| CA4-04-1792789 | EVAL | 2024-05-01 | 0001193125-24-127459 | EX-10.1 | DoorDash |
| CA4-05-1062231 | EVAL | 2024-05-17 | 0000947871-24-000495 | EX-10.1 | American Axle & Manufacturing |
| CA4-06-1703056 | EVAL | 2024-05-24 | 0000950142-24-001403 | EX-10.1 | ADT |
| CA4-07-1771514 | EVAL | 2024-06-03 | 0000950170-24-067888 | EX-10.1 | ExchangeRight Income Fund |
| CA4-08-821002 | EVAL | 2024-06-06 | 0001558370-24-008935 | EX-10.1 | G-III Apparel Group |

- **Screening outcomes** for the 306 candidates: 8 eligible; 122 rejected by the amendment screen; 13 by segmentation; 1 because no body was located; 1 for issuer reuse; the rest for size below 150,000 bytes.
- **Provenance.** Every screened candidate, its decision and its SHA-256 is in `data/source_manifest.json`.
- **No V3 issuers.** The issuer CIK exclusion was applied.

## Primary result: mean Brier over live features (lower is better)

- **Ceiling guard.** `INLINE_DEFINITION` was observed at a rate of 0.00 across all 24 targets, so it is excluded from the primary.
- **Primary features:** EXCEPTION (0.54 observed), PROVISO (0.42), QUANT_THRESHOLD (0.29), CROSS_REFERENCE (0.33).

| Agreement | FROZEN_SEED | CUMULATIVE | SIMPLE_COUNTS | PRECEDENT |
|---|---|---|---|---|
| CA4-03 | 0.2083 | 0.2083 (tie: same library at step 3) | 0.2521 | 0.3100 |
| CA4-04 | **0.2008** | 0.2325 | 0.2286 | 0.3600 |
| CA4-05 | 0.2327 | 0.3361 | **0.2195** | 0.2600 |
| CA4-06 | 0.1298 | 0.1310 | **0.1136** | 0.1600 |
| CA4-07 | 0.2212 | 0.2282 | 0.1164 | **0.0600** |
| CA4-08 | 0.2953 | 0.3203 | **0.2913** | 0.5100 |
| **Mean** | 0.2147 | 0.2427 | **0.2036** | 0.2767 |

**Decision checks (frozen rule):**
- CUMULATIVE beats FROZEN_SEED in **0/6** agreements, with a mean gain of **−0.028**. The first KEEP condition requires ≥ 4/6 and ≥ +0.01, so it fails: **STOP**.
- CUMULATIVE beats SIMPLE_COUNTS in 1/6 (gain −0.039).
- CUMULATIVE beats PRECEDENT in 4/6, so the `PRECEDENT_COPY_EQUIVALENT_OR_BETTER` qualifier is not added.
- Negative control: SIMPLE_COUNTS beats FROZEN_SEED in 4/6.

With all five features included (ceiling version), the order is the same: SIMPLE_COUNTS 0.163 < FROZEN_SEED 0.172 < CUMULATIVE 0.195 < PRECEDENT 0.223.

**Interpretation, limited to what was observed:**
- Accumulating more source-anchored events did not improve these textual-proxy expectations; it made them worse.
- A type-free base-rate model was at least as good as the type-conditioned arms.
- This does not show that no learnable within-provision structure exists. It shows that this frozen predictor and library did not extract any on this corpus.

## Secondary results (provisional: rule-authored labels, not verdict-bearing)

| Arm | Type hit@3 | Xref-type recall@3 (mean) |
|---|---|---|
| FROZEN_SEED | 7/12 | 0.302 |
| CUMULATIVE | 8/12 | 0.406 |
| SIMPLE_COUNTS | 1/12 | 0.000 |
| PRECEDENT | 5/12 | 0.083 |

- **Labels are provisional.** Type and cross-reference-type labels come from V3 heading rules (`PROVISIONAL_AGENT_AUTHORED`), and only 12 of the 24 targets have a non-OTHER rule type.
- **The CUMULATIVE edge is not established.** It is small, unreviewed and below any significance threshold.
- **Blind review is still open.** `results/review_packet.csv` (24 rows, blind to arm predictions) has not been reviewed by a human, so no label is VERIFIED.

## Counterexamples and persistence

The run logged 5 confident CUMULATIVE errors. All are *under*-predictions of a present feature:
- **EXCEPTION:** CA4-04 §5.05, p = 0.105.
- **QUANT_THRESHOLD:** CA4-05 §6.04 (p = 0.027), CA4-05 §6.10 (p = 0.027), CA4-08 §6.05 (p = 0.017), CA4-08 §5.10 (p = 0.099).

The low QUANT_THRESHOLD belief for covenant articles persisted from step 5 to step 8 despite the step-5 counterexamples. This is the append-only persistence that §5 says will be reported.

## Caveats on this run

- **Feature truth is a textual proxy.** It is regex presence in the revealed body, not contractual understanding.
- **`INLINE_DEFINITION` had no hits on any target.** This may reflect the feature regex rather than the contracts. The frozen ceiling guard excluded it from the primary as designed. It is recorded here as a possible proxy defect and has not been retrofitted.
- **Exhibit size.** CA4-03 (NNN REIT) is a 13.9 MB exhibit. It passed every frozen screen and was kept.
- **Sample size.** Six evaluation agreements give no statistical significance.

## Committed derived evidence

- `data/source_manifest.json`
- `data/views/*.json`: ToC headings, rule labels and hashes only.
- `results/predictions/*.json`: sealed first-run predictions.
- `results/run.json`: chain, hidden-access order, per-target scores with offsets and hashes, decision.
- `results/library_final_events.json`
- `results/review_packet.csv`

Raw exhibits (`raw/`) and revealed bodies (`local_hidden/`) stay local and are gitignored. No contact identity appears in any committed file.

---

## Historical record (pre-run, superseded by the run above)

Earlier status: **`BLOCKED_SOURCE_ACCESS` (cloud) / `READY_NOT_RUN`**, recorded before SEC egress was enabled.

**No sequential experiment was run, so there is no learning result and no KEEP/REVISE/STOP verdict on the hypothesis.** The frozen protocol does not allow a substitute corpus: no synthetic, benchmark or snippet data, and V3-seen documents may be used for plumbing only.

## What blocked execution

- **Network.** This cloud session's egress policy refuses CONNECT to `www.sec.gov`, `efts.sec.gov` and `data.sec.gov`.
  - The frozen fetch was attempted at 2026-10-14T12:12:00Z.
  - It failed with `URLError: Tunnel connection failed: 403 Forbidden`, and the proxy logged `efts.sec.gov:443 connect_rejected`.
  - Earlier probes the same day logged the same denial for `www.sec.gov` and `data.sec.gov`.
- **No local copy to fall back on.** The repository holds no previously downloaded full-text agreements on any branch. V3 committed only headings, labels and SHA-256 hashes; its raw files are on the owner's machine.
- **No verifiable mirror.** A bounded web search found none; the only bulk source, sec-api.io, is commercial. Per the owner's instruction, no further egress workaround was attempted.

## What was prepared and frozen (this commit)

| File | Role |
|---|---|
| `PROTOCOL.md` | Frozen: content-blind corpus rule (2 seeds + 6 evaluation agreements, 2024 H1 8-K EX-10 credit agreements), masking, 4 arms, metrics, verdicts, stated limits |
| `frozen/freeze_receipt.json` | LF-normalized SHA-256 of the protocol, V4 code and the reused V3 `extract.py` / `labels.py` / `predict.py`. The runner refuses to run if any of them changes. |
| `v4_corpus.py` | EDGAR fetch plus eligibility screens. ToC and bodies via V3 `extract`; labels via V3 `labels`. Views are committed; bodies stay local. |
| `v4_sequential.py` | predict → seal (hash chain) → reveal (guarded) → score → counterexample log → append-only learning; `replay`; blind `review_packet.csv` |
| `test_v4.py` | 9 offline tests on **synthetic fixtures (plumbing only, not evidence)**: masking hides the target; hidden bodies cannot be read before sealing; the frozen library never changes; the growing library holds exactly the earlier agreements; replay is identical; the decision rule returns KEEP on a planted learnable dependency and STOP/REVISE on random features |
| `RUNBOOK_V4.ps1` | One operator-local command sequence: test → fetch → build → run → replay → commit/push |

**Checks run in this session:**
- `python -m unittest test_v4` → 9/9 OK.
- V3 `test_v3` still OK; V3 files are unchanged.
- Freeze gate: run refused after a one-byte edit to `PROTOCOL.md`.
- Empty corpus: run refused with `BLOCKED_SOURCE_ACCESS`.

**Defects found while building, fixed before the freeze:**
1. Leaving the article's visible types in the type candidates diluted the type mixture. Reverted to V3's convention of removing them.
2. V3 per-type presence scores are not a distribution over the masked slot. Feature expectations now mix over V3's top-3 shortlist only.

Both fixes were made on synthetic fixtures before any authentic agreement existed.

## Limits that will apply to the run

These are carried from `PROTOCOL.md` §7:
- Feature truth is mechanical text matching: textual presence, not legal meaning.
- Type and cross-reference labels are V3 heading rules: `PROVISIONAL_AGENT_AUTHORED` until the 24-row blind packet is reviewed.
- Six evaluation agreements give no statistical significance.
- A gain matched by `PRECEDENT` is flagged as possible clause copying.

## Unblock (single next action)

The owner either:
- runs `RUNBOOK_V4.ps1` locally with `SEC_USER_AGENT` set (no provider calls, a few minutes), or
- adds `www.sec.gov` and `efts.sec.gov` to this cloud environment's allowed domains, so the same commands can run here.

The run commits `data/`, `results/` and per-agreement learning logs to PR #18.
