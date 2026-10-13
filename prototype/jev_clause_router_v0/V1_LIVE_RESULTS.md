# JEV V1 live-evidence pilot — results (13 October 2026)

**Status: `BLOCKED_NO_LIVE_RUN`.** This iteration hit the task's hard stop: there is no Jev (TypeSafe) API key and no reviewer access in the implementing session. Only the readiness work, the frozen sources and the offline tests were completed. **This is a blocker, not a PASS. No claim about Jev, the reviewers or the A/B/C/D comparison is supported by anything in this file.**

Charter anchor: §5 stage 1 (FEASIBILITY) of an upstream interpretation/routing component. It is exploratory and outside the ratified BI semantic-layer path (§2, §4). It is not TRANSPOSE/VERIFY evidence and has no `/documents` or `/assess` integration. Task prompt: `Claude_Code_Sophon_JEV_V1_Live_Evidence_2026-10-13.md` (repo root).

## 1. ACTUAL vs SIMULATED counts

| Kind | Count | What it is |
|---|---:|---|
| `ACTUAL_PROVIDER` Jev calls | **0** | `TYPESAFE_API_KEY` absent |
| `ACTUAL_PROVIDER` Claude reviewer/baseline calls | **0** | `ANTHROPIC_API_KEY` absent; the CLI path is refused inside a Claude Code session (`CLAUDECODE` set) |
| `RECORDED_ACTUAL` replays | 0 | nothing recorded |
| `LAB_FIXTURE` | V0 demo (5 clauses, hand-authored) + mocked transport in `test_v1.py` | tests of code paths only, **not observations** |

Blockers as reported by `python prototype.py --mode preflight --clauses clauses.json --clauses external_github_sla_2021.json` (exit 2, zero network calls; saved as `preflight_2026-10-13.json`):
- `NO_TYPESAFE_API_KEY`: arms A, B and C cannot run.
- `NO_ANTHROPIC_API_KEY`: arms B, C and D cannot run via the Messages API. A Claude Max subscription is not an API key.
- Not in the preflight but enforced in code: `NESTED_CLAUDE_CODE_SESSION`. The `claude -p` reviewer path refuses to run inside Claude Code; the environment was not spoofed.
- A scan of user/machine environment scopes for keys was refused by the session's permission classifier and was not pursued.

## 2. Immutable source identification

| Corpus | File | `corpus_sha256` (canonical JSON) | Status |
|---|---|---|---|
| LAB-SLA-5 (C1–C5) | `clauses.json` (unchanged since V0) | `745802bc54061d621ef6bea21095bc3f07c27ec7d77b2a0a4a1b641cd968f801` | `LAB_AUTHORED`, fictional; smoke test only |
| GITHUB-SLA-EXT-5 (G1–G5) | `external_github_sla_2021.json` | `4023ee710fb3fc35a02de245eb6f685791fef15138d28b39b97aeb0c24c13cae` | official published terms, **not a signed contract**; applicability UNKNOWN |

The external set was frozen and committed (`d2bcb69`) **before any adapter change and before any model output existed**. Each excerpt carries an `excerpt_sha256`, which `check_clause_file` verifies at load time.

| ID | Structure | Source | `excerpt_sha256` (prefix) |
|---|---|---|---|
| G1 | credit tiers ("either (not both)", 10% / 25%) | GitHub Online Services SLA, June 2021, §1 table | `c3f2428b316fd536` |
| G2 | definition ("Downtime") | same, §1 table | `1aa7930e7cbbd21f` |
| G3 | exclusion (§2, whole) | same | `086472d29dfbe4d2` |
| G4 | claims timing, redemption conditions (§3, whole) | same | `ccd642966ac4c0f6` |
| G5 | version/effectiveness | GitHub "Updates to Customer Terms", June 2026 item | `074d77810acab8ed` |

- **2021 SLA PDF:** `https://assets.ctfassets.net/8aevphvgewt8/7rEf04yu01oTt1cGyeXz03/f58072058dfb2f1fb25cb80b0b285890/GitHub.Online.Services.SLA_20210630_locked`. Retrieved 2026-10-13T09:22:32Z, HTTP 200, 150,170 bytes, sha256 `70f1cdcd11bcfa0bc22796ebdca27a61b8f24bbdb2fc5ad559dd643cccc6a2a8` (identical on two fetches). The PDF is owner-restricted; the restriction was not removed. The excerpts were transcribed from the viewer rendering.
- **Change notice:** `https://github.com/customer-terms/updates`, HTTP 200 at 09:22:33Z. The whole page is dynamic HTML, so rely on the excerpt hash.
- **`EXTERNAL_CORPUS_PARTIAL`:** the June 2026 SLA at `https://github.com/customer-terms/github-online-services-sla` returned **HTTP 500** on three attempts (plain, `?locale=en-US`, final 09:22:34Z), and **406** with `Accept: application/pdf`. No 2026 SLA provision is in the corpus, and the 2026 tiers quoted in `../normative_layer/V02_PUBLIC_SOURCE_GITHUB_SLA.md` were **not re-verified**. That note's applicability caution remains in force.
- Context packs name the explicit missing references (Customer's agreement, the Status Page Service Feature definitions, the Agreement, the 2026 SLA text). They deliberately do **not** name the implicit dependencies, because those are the omissions under test:
  - G1 depends on §3 redemption conditions.
  - G2's "error rate" is defined only in the Packages row, and hourly.
  - G3 does not say who attributes causation.

**Provisional review matrix:** `review_matrix.json` (canonical JSON digest `5b897906…`), written before any model output and committed in `d2bcb69`. It records:
- primary type(s) and required vs contestable modifiers;
- 38 material conditions, each with an exact anchor substring and the harm if missed;
- explicit and implicit dependencies (including C4's absent Schedule A).

**It was authored by the implementing agent (claude-opus-5-5), the same model family as the default reviewers.** It is a transparent working reference, not an independent expert or legal oracle, and needs owner or expert review before any score built on it is trusted.

## 3. Failures found and code changed

Found by checking the code against the official TypeSafe docs (`docs.typesafe.ai/api`, `/models`, `/model-jaggedness/jev-1.13`, fetched 2026-10-13T09:16:49Z), the public `typesafe-sdk` 0.7.4 wheel, and current Claude API documentation. **None of these was observed in a live call.**

1. **Jev model ID was silently replaced.** V0 recorded `raw.get("model", model)`, so a missing `model` field would have been logged as the alias `jev-latest`. The official response requires `model`, which reports the versioned ID (docs: `jev-latest` → `jev-1.13.0`). It is now required, and its absence makes the output invalid.
2. **`usage` and `confidence` were not validated.** Both are required in the official schema. They are now checked: integers ≥ 0, and a probability in [0,1].
3. **Any malformed live output aborted the whole run.** One unanchored quote raised `ValueError` and lost every other clause's evidence. Live/replay now record a per-clause `REVIEW_INVALID_*` / `NOT_RUN` and fail closed to `HOLD_UNRESOLVED`. Fixture validation in the V0 demo stays strict.
4. **Near-tie Choice/probability mismatch.** V0 rejected any `choice ≠ argmax`. Now:
   - a gap ≤ 0.02 keeps the provider's label untouched, invents no probability, and is flagged `PROVIDER_CHOICE_PROBABILITY_INCONSISTENT_NEAR_TIE`, which holds every Jev arm;
   - a larger gap makes the output invalid;
   - a top-two gap ≤ 0.02 is flagged `PRIMARY_NEAR_TIE`.

   *I could not find official documentation of a rounding inconsistency* (API docs, jaggedness page, SDK 0.7.4, SDK changelog), so this guard is precautionary.
5. **Documented option-order bias.** The jev-1.13 jaggedness page reports a bias toward the first Choice option. The request now adds a `primary_reversed` Choice with reversed option order in the same call (zero extra calls). Disagreement is flagged `JEV_OPTION_ORDER_SENSITIVE` and holds.
6. **No retries.** The API documents 429/529. `post_json` now does 2 bounded retries with backoff on 408/429/5xx/529 and connection errors, and honors `retry-after(-ms)`. 401/403/404/422 are not retried and stop the live run; partial evidence is kept. There is no fallback to fabricated data.
7. **The Anthropic adapter would have failed or been stale.**
   - It sent `temperature: 0`, which current models reject with a 400. It is removed.
   - The default model was the previous-generation `claude-sonnet-4-5`. All three LLM roles now default to `claude-opus-5-5` with effort `medium`.
   - Server-side model fallback is deliberately **not** enabled, because it would silently change the model under test.
   - `stop_reason` `refusal`/`max_tokens` is recorded as a provider error.
8. **The CLI reviewer was contaminated and nested.** It ran `claude -p` with `cwd` = this repo, which would load Sophon's `CLAUDE.md` and charter instructions into the "independent" reviewer. It also ran inside Claude Code. Now:
   - it refuses when `CLAUDECODE` is set;
   - it runs from an empty temp directory with a replaced system prompt, `--tools ""` and `--no-session-persistence`;
   - it records the models the CLI reports and the CLI's cost. The remaining harness context is recorded as a caveat.
9. **Quote anchoring was byte-exact.** The GitHub text uses typographic quotes (“Downtime”, Customer’s), so honest straight-quote citations would have been rejected as hallucinated. Matching now normalizes only quotes, dashes and whitespace.
10. **Added Arm D (blind baseline).** Its prompt sees only the source packet. Also added: offline `replay` from stored raw outputs (refuses if the corpus hash differs), `preflight` (no network), a per-invocation call cap (`--max-provider-calls`, default 20), incremental writes of partial evidence, and `compare.py`.

Unchanged: `clauses.json`, `mock_evidence.json`, `results_demo.json`, `RESULTS.md`, the V0 demo path and all 15 V0 tests. The V0 demo still produces identical dispositions.

## 4. Models and prompts (recipe to be used by the live run)

- Jev: `POST https://api.typesafe.ai/v1/systemone`, model `jev-latest`, with **raw model ID to be recorded from the response (NOT OBSERVED)**. One Choice (`primary`), one reversed-order Choice, and five Nouls.
  - Question digests: plain-state `974cad49…`, structured-state `014b98c0…`.
  - LAB clauses are sent as a string state; external clauses as `{"clause", "context"}`.
- Adversarial / backward / blind prompts: `reviewer_prompt()` and `baseline_prompt()` in `prototype.py`. Each live record stores the full prompt and its sha256.
  - The adversarial and backward reviewers see the same packet plus Jev's proposal and provider flags, never each other.
  - The blind baseline sees only the packet.
- Reviewer engine: Messages API (`claude-opus-5-5`, effort `medium`, `max_tokens` 16000, neutral system prompt), or the Claude CLI from a terminal outside Claude Code.

## 5. Per-clause A/B/C/D comparison

| Corpus | A Jev | B Jev+adv | C Jev+adv+back | D blind LLM |
|---|---|---|---|---|
| LAB C1–C5 | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN |
| EXT G1–G5 | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN |

No candidate/hold coverage, missed-qualifier counts, false challenges, reviewer-unique findings or token overhead can be reported. `compare.py` produces exactly these per clause once recordings exist.

## 6. Costs

Spent this iteration: USD 0 on model calls. Pre-run estimate (preflight, characters/4, assuming 2,500 output+thinking tokens per LLM call):
- 40 calls in total (10 Jev + 30 Claude).
- Jev: about USD 0.0003.
- Claude at `claude-opus-5-5` list price: about USD 1.6. Via `claude-cli`, subscription quota is used instead.

## 7. Known shared omissions

None observed, because nothing ran. The a-priori correlated-failure risks:
- the matrix author and the reviewers share a model family;
- adversarial and backward are two prompts on the same model, so they are not independent adjudicators;
- the documented jev-1.13 weaknesses are literal reading, numbers, date/time comparison and indirection. The G1/G2/G4/G5 thresholds, quarters and effective dates sit squarely on those weaknesses. This is a hypothesis to check, not a finding.

## 8. Pre-registered decision rule (written before any live output)

Applied per corpus, using counts only (n=5 each):
- **DROP** Jev routing for this function if A has at least as many `candidate_with_missed_required` as D, and B/C recover no required modifier or implicit dependency that D also misses.
- **SIMPLIFY → drop the backward reviewer** if, across both corpora, `backward_only` findings recover nothing material beyond B. **SIMPLIFY → blind LLM only** if D ≤ C on missed-required plus unsupported, with ≤ 1/4 of the calls.
- **REUSE** only if C recovers at least one material omission (matrix-adjudicated, then human-checked) that both B and D miss, without converting most correct clauses into holds (`hold_with_no_missed_required`).
- Any result that rests only on the provisional matrix stays provisional until a human adjudicates the AUTO_HINT columns.

## 9. Decision

**No REUSE / SIMPLIFY / DROP decision is possible: `BLOCKED_NO_LIVE_RUN`.** Zero Jev outputs and zero reviewer outputs exist, so choosing any of the three would be a guess dressed as evidence. The single available observation is structural: arm A cannot report unresolved references or the evidence behind a modifier, so it cannot by itself satisfy the source-anchoring requirement. That is a property of the design, not a measured performance gap. This is not a go/no-go on Sophon.

## 10. No-claim list

This file does not claim:
- Jev accuracy or calibration, or reviewer recall;
- that any arm is better than another;
- legal correctness, completeness or the applicability of any GitHub term to any customer;
- that the 2026 SLA tiers are verified;
- independent ground truth;
- integration with a semantic layer;
- any authorization.

Mocked-transport tests show only that the code paths work.

## 11. Next bottleneck and exact operator command

**Next bottleneck: genuine provider access, run outside Claude Code.** In a new PowerShell window (not inside Claude Code):

```powershell
cd C:\Claude\sophon\prototype\jev_clause_router_v0
# With an Anthropic API key:
powershell -ExecutionPolicy Bypass -File .\RUNBOOK_V1_LIVE.ps1 -Reviewer anthropic
# Or, with only a Claude subscription login (claude CLI):
powershell -ExecutionPolicy Bypass -File .\RUNBOOK_V1_LIVE.ps1 -Reviewer claude-cli
```

The runbook:
- prompts for keys without echoing them;
- runs the no-network preflight;
- asks for an explicit `YES` before the 40 calls;
- writes raw recordings to `live_runs/`;
- replays them offline;
- runs `compare.py`.

Commit `live_runs/` unchanged, then apply §8.

## Commands run in this iteration

| Command (in `prototype/jev_clause_router_v0`) | Exit |
|---|---:|
| `python -m unittest discover -s . -p "test_*.py"` (15 V0 + 25 V1 tests) | 0 |
| `python prototype.py --mode demo --output results_demo.json` (output reverted; only list order and timestamp differed) | 0 |
| `python prototype.py --mode preflight --clauses clauses.json --clauses external_github_sla_2021.json` | 2 (blocked, as expected) |
