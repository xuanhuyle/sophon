# Sophon JEV V2 — does an A-derived provision library transfer from GitHub to Google?

**Status: READY_NOT_RUN.** Everything offline is implemented and tested; **zero Google (Contract B) provider calls have been made**. Results live in [V2_TRANSFER_RESULTS.md](V2_TRANSFER_RESULTS.md). Task prompt: `Claude_Code_Sophon_JEV_V2_Provision_Library_Transfer_2026-10-13.md` (repo root). Charter: Sophon Charter v1.2 (PR #15) — this is a **Stage 1 component-feasibility** test of an *upstream interpretation/learning subcomponent*; it proves no BI integration, no enforcement, no legal authority and no market demand.

## Question under test

Can Jev (TypeSafe System One) plus two independently invoked LLM checks, given a **versioned provision-structure library induced from the GitHub Online Services SLA (June 2021)**, recover more correctly supported material slot/value facts from three unseen packets of the **Google Cloud Storage SLA (archived 24 June 2021)** than the same pipeline with (a) no learned memory and (b) the raw GitHub examples instead of a library — **without transplanting GitHub's quarterly window, tiers, percentages or deadlines**?

Only **dimension 4 (provision structure)** is scored. Dimensions 1–3 (governing law, contract family, section) are frozen descriptive sidecars given identically to every arm.

## Protocol

| Step | What | Provider calls |
|---|---|---|
| A | Reuse the owner's genuine V1 recording `../jev_clause_router_v0/live_runs/live_EXT_*.json` for G1–G4 (Jev `jev-1.13.0` + adversarial + backward `claude-opus-5-5`, all `ACTUAL_PROVIDER`). Verified by corpus hash, source hashes, provenance and schema. | **0 new** |
| Induce | `transfer.py --mode induce`: deterministic DISCOVER / REFINE / ABSTAIN over anchored reviewer quotes + Jev outputs → `library_v1.json` + `library_events.json`; rejected by `validate_library` if any rule fails. | 0 |
| B freeze | `google_storage_sla_20210624.json`: three packets B1–B3 with excerpt/context hashes, literal headings and nesting, applicability `UNKNOWN`. `reference_checklist_b.json`: sealed provisional checklist + rubric + contamination markers, frozen before any B output. | 0 (one HTTP GET of the public page) |
| Live | Per packet: COLD_B, WARM_LIBRARY_B, WARM_RAW_A_B each = 1 Jev + adversarial + definition/backward; plus BLIND_LLM_B. | 27 + 3 (+1 optional A-only synthesis) ≤ **31** |
| Replay / score | Offline re-derivation from stored raw outputs; scoring against the sealed checklist; pre-registered rule. | 0 |

**Only the memory differs between the three pipeline conditions.** Jev receives it through the official `choice` criteria (template ids + definitions) and, for WARM_RAW_A_B, through `prior_examples` in the structured state. The reviewers receive it in a `MEMORY` block; prompts, source packet, section context, model, effort and output schema are otherwise identical, and the prompt text and memory hash are recorded per call.

## Data boundaries

- **Contract A** (GitHub, frozen in V1): G1–G4 only. G5 (change notice) is excluded (`ABSTAIN` event).
- **Contract B** (Google): `https://cloud.google.com/storage/sla-20210624`, HTTP 200, retrieved 2026-10-13T12:07:25Z, 711,725 bytes, page sha256 `e5b91991…0314` (dynamic chrome; rely on packet hashes). Archived version, explicitly "not the current version". Vendor standard terms, **not a signed agreement**; applicability `UNKNOWN`.
- **Leakage controls (tested):** the library may contain no Contract B vocabulary (`B_LEAKAGE_TOKENS`); COLD/RAW memories contain no learned template; the optional synthesis prompt is A-only; the checklist never enters any prompt; replay refuses a changed corpus or library.
- **Not blind:** the same agent froze B, wrote the checklist and wrote the inducer after reading A and the V1 recordings. Recorded in the corpus file (`preparer_blindness`) and the checklist (`authored_by`).

## Commands (all offline unless stated)

```powershell
cd C:\Claude\sophon\prototype\jev_library_transfer_v2
python transfer.py --mode validate                 # frozen hashes, library and context validators
python transfer.py --mode diagnose-v1              # field-level cause of the V1 blind-baseline failures
python transfer.py --mode induce                   # library_v0 -> library_v1 from the real A recording
python transfer.py --mode preflight                # readiness, caps, cost estimate; no network
python -m unittest test_v2 -v                      # offline tests (mocked transport)
powershell -ExecutionPolicy Bypass -File .\RUNBOOK_V2_TRANSFER.ps1 -PreflightOnly
# LIVE (new terminal outside Claude Code; explicit YES; <= 31 logical calls):
powershell -ExecutionPolicy Bypass -File .\RUNBOOK_V2_TRANSFER.ps1 -Reviewer anthropic
# afterwards, offline:
python transfer.py --mode replay --recorded live_runs\live_V2_<stamp>.json --output live_runs\replay_V2_<stamp>.json
python transfer.py --mode score  --recorded live_runs\replay_V2_<stamp>.json --output live_runs\score_V2_<stamp>.json
```

`live_runs/` is git-ignored; the runbook writes `receipts_<stamp>.json` (SHA-256 of every raw file) for commit.

## Files

- `transfer.py` — engine: A-evidence loader, deterministic inducer, library/context validators, per-condition Jev requests and reviewer prompts, field-level output validation, reconciliation, scoring, pre-registered rule, live/replay/preflight.
- `library_v0.json` (bootstrap), `library_v1.json` (A-derived, provisional), `library_events.json`.
- `context_libraries/` — `legal_context.json`, `contract_family.json`, `section_functions.json`, `section_registry.json`, `provisions.json`.
- `google_storage_sla_20210624.json`, `reference_checklist_b.json` (sealed).
- `RUNBOOK_V2_TRANSFER.ps1`, `test_v2.py`, `V2_TRANSFER_RESULTS.md`.

## Pre-registered decision rule (frozen with the checklist)

- **PROMISING_TRANSFER_PROVISIONAL**: WARM_LIBRARY_B recovers ≥2 additional correctly supported material elements vs COLD_B, recall gain ≥20 pp, zero critical wrong transfers, and recovers ≥1 element WARM_RAW_A_B misses. Engineering signal on n=3, not generalization.
- **NO_OBSERVED_INCREMENTAL_LIBRARY_VALUE** otherwise, with the failing checks named.
- **INCONCLUSIVE_OR_BLOCKED**: any pipeline condition without scorable output on every packet.
- Reported alongside: whether BLIND_LLM_B matches or exceeds WARM_LIBRARY_B; token/attempt/latency overhead per condition; `HOLD_UNRESOLVED` counts kept separate from recall.

## What this cannot show

Legal correctness, generalization beyond three packets, cross-family or jurisdiction transfer, section-taxonomy learning, BI semantic integration, agent enforcement, or that any template is authoritative. The library stays `PROVISIONAL` until the owner reviews it.
