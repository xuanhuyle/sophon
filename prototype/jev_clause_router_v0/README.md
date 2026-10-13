# Sophon — 5-clause Jev / adversarial / backward prototype (V0)

**Runnable orchestration skeleton, not a validated contractual interpreter.** Python 3.10+, standard library only. No database, no agent action, no production authorization. All five clauses in `clauses.json` are **fictional**. No private documents or real contractual promises are involved.

## Why this exists

Investigate a narrow hypothesis: a *Jev proposal* provides a primary normative function and probabilities for independent modifiers; two separately invoked LLM reviewers examine the proposal from opposing positions; a deterministic controller decides whether to route a provisional transposition **for human review** or to **hold for an unresolved omission**.

```
clauses.json (5 literal clauses)
      |                               +-----------------------------+
      v                               | independent from each other |
Jev: Choice + five Noul questions     |                             |
      |------------------------------>+ LLM1 adversarial challenge  |
      |                               +-----------------------------+
      |------------------------------>+ LLM2 backward evidence check|
      |                               +-----------------------------+
      v
JSON output / deterministic reconciler
      |---- HOLD_UNRESOLVED (dissent, missing modifier, missing source)
      +---- CANDIDATE_FOR_HUMAN_REVIEW (never legally approved)
      |
      v
SUGGESTED transposition pattern only (no generated rules deployed)
```

A clause can have a primary function plus **multiple modifiers**. Jev questions ask for one `Choice` and five separate `Noul` scores (`THRESHOLD`, `EXCLUSION`, `CONDITION`, `DEADLINE`, `CROSS_REFERENCE`). The code is aligned with the official TypeSafe API shape (`POST https://api.typesafe.ai/v1/systemone`, or use their SDK). The reviewers are given the literal source and identical Jev proposal but *not each other's answers*. A backward reviewer assumes the proposal is true and looks for verbatim entailment; an adversarial reviewer assumes it is wrong and actively looks for omissions. Their agreement is **not proof of completeness or legal correctness**.

## What has actually run here

```powershell
cd <folder-containing-these-files>
python prototype.py --mode demo --output results_demo.json
python -m unittest discover -s . -p "test_*.py" -v
```

This runs *entirely offline*. `mock_evidence.json` contains **hand-authored Jev-shaped scores and hand-authored reviewer answers**. Nothing in this mode calls Jev or an LLM. The fixture deliberately omits C3's claim deadline and C4's disclosure exception so that the adversarial route can be exercised. Scores in this file have **no calibration**, and the two author-written reviewer records are **not independent model judgments**. The demo establishes only that the controller makes the intended transitions with the given responses.

Example offline result:

| Clause | Simulated Jev choice | Adv. | Backward | Controller |
|---|---|---|---|---|
| C1 | OBLIGATION (94%) | Supported | Supported | Candidate for human review |
| C2 | DEFINITION (94%) | Supported | Supported | Candidate for human review |
| C3 | PERMISSION_RIGHT (91%) | Disputed | Supported with gaps | HOLD: missing DEADLINE |
| C4 | PROHIBITION (91%) | Disputed | Supported with gaps | HOLD: missed EXCLUSION and Schedule A absent |
| C5 | AUTHORITY (90%) | Supported | Supported | Candidate for human review |

**The table is a hand-authored fixture demonstration, not empirical classification accuracy.** `results_demo.json` records per-clause source hashes, all responses, review evidence, provisional transposition routes, and clear source provenance tags.

## Run the real three-model sequence

### Jev + two separate Claude Code CLI reviewer invocations

Requires a TypeSafe Jev API key (not provided in this ChatGPT environment) and a working `claude` CLI authenticated under your own account. On PowerShell:

```powershell
$env:TYPESAFE_API_KEY = "YOUR_JEV_API_KEY"
claude --version
python prototype.py --mode live --reviewer claude-cli --allow-external-calls --output results_live.json
```

The script performs **five real Jev requests + ten separate Claude Code CLI requests** (one adversarial and one backward per clause). These reviewer requests are separate calls, **not independent trained models** by default; their errors may be correlated. The script never silently falls back to fixtures if a provider fails.

If the CLI model identifier is rejected, use `--adversarial-model sonnet --backward-model opus` or appropriate models recognized by your CLI, or set explicit models. The code uses separate subprocesses and sends clauses to external services; don't run with confidential contracts until you have handled data protection and provider terms.

### Jev + Anthropic Messages API

Requires separate valid provider API keys; a Claude Max subscription is **not** the Anthropic API credential.

```powershell
$env:TYPESAFE_API_KEY = "YOUR_JEV_API_KEY"
$env:ANTHROPIC_API_KEY = "YOUR_ANTHROPIC_API_KEY"
python prototype.py --mode live --reviewer anthropic --allow-external-calls --output results_live.json
```

The default Anthropic model identifier is configurable through `--adversarial-model` and `--backward-model` (verify current IDs before live runs). Tokens may cost money. The real mode transmits the clauses to external providers; it never runs without the explicit `--allow-external-calls` flag. You can replace the reviewers with another provider without changing the controller. If you use a single model for both roles, you have independent calls, **not an independent oracle**.

## Files

- `clauses.json`: exactly five independently editable clauses (all invented for the lab).
- `prototype.py`: typed Jev API requests, live review adapters, deterministic routing and reconciliation, provenance output.
- `mock_evidence.json`: explicit demo-only Jev-shaped probabilities and reviewer responses.
- `results_demo.json`: recorded output generated by an offline run.
- `test_prototype.py`: the actual regression tests for the *controller*, including a deliberate missed deadline/exception and malformed evidence.

## What this cannot conclude

1. Neither a Jev probability nor concordant LLM reviews establishes the truth of a legal interpretation. The modal failure remains **a shared omission that both reviewers overlook**. A quote existing in a contract is not proof of the proposed interpretation's entailment.
2. The adversarial and backward prompts may be correlated even with different models. You would need independent subject-matter labels on an unseen corpus to measure recall, especially **conditional permission omissions**.
3. Clause-level classification alone does not recover connected clauses, exceptions in a chapeau, annexes, applicability, temporal amendments, obligation lifecycle or reliable real-world data bindings. C4 explicitly requires an **absent Schedule A**.
4. Nothing is compiled into a policy engine, no downstream agent reads this file, and no action is authorized. This is the *classification/review/routing skeleton* the user requested, not Sophon's end-to-end product.
5. The offline fixtures are intentionally authored to produce two catches. They demonstrate the **wiring**, not that Jev or the LLMs would identify those misses in practice.

**Next meaningful step (not an automatic roadmap):** Execute exactly this harness with real Jev and independently invoked reviewers on the five unchanged clauses. Replace the authored fixture with actual provider responses; count material missed modifiers, falsely alleged modifiers, review disagreement, and human adjudication outcomes. If the controller consistently fails to catch undiscovered conditions, no amount of green integration tests establishes reliability.
