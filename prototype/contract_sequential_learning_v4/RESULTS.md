# V4 sequential learning on authentic EDGAR credit agreements: RESULTS

**Status: `BLOCKED_SOURCE_ACCESS` (cloud) / `READY_NOT_RUN`.** 2026-10-14. **Provider calls: 0.**

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
