# E5: decision

**PASS_FORWARD_TRANSPOSITION_SIGNAL.**

The verdict is applied mechanically from PROTOCOL.md §7 (`src/gate.py` → `evidence/gate.json`).

**Scope.** This retires **R6 only for one controlled native field-threshold amendment**. It is a suggested
GO/HOLD/STOP input for the owner, not a self-approved gate.

## Why

**Prerequisite.** E4 = PASS_INDEPENDENT_VERIFICATION_SIGNAL. The combined E4 M6B + M2 baseline builds, and both
lab-added metrics query natively.

**Transposition from the approved delta.** A separate deterministic transposer:
- ran in an isolated directory with only the frozen packet, and opened no repository file;
- computed the clause-level delta (`unit_price_threshold` GE `100` → `120`) from the two approved IR versions;
- checked that the v1 rendering reproduces the deployed baseline;
- emitted one in-place edit of the existing `premium_completed_revenue` metric (filter and description). P2 was
  NOT_AFFECTED, with a stated rationale.

Its source contains no answer literal. It follows the IR threshold (`135`, `99.5`).

**Native verification.**
- The generated revision built, and genuine `mf` compiled `sales__unit_price >= 120`.
- On 2025+ rows it matched an independent raw-CSV v2 oracle by year and order line on PINNED and BOUNDARY120.
- The old revision was flagged against v2. Counterexamples: lines 15 (100.00) and 21 (119.99), and 69 pinned
  lines priced in [100, 120).
- Wrong patches were rejected with discriminating rows:

| Patch | Discriminating row |
|---|---|
| `>= 119` | line 21 at 119.99 |
| `> 120` | line 22 at 120.00, on the boundary fixture only |
| `!= 'cancelled'` | returned line 16 |

**Time and authority.**

| Knowledge time | v2 state | Generated revision |
|---|---|---|
| Before the amendment was known | NOT_KNOWN | NOT_VERIFIED for v2 although it executes; NONCONFORMING to the then-governing v1 |
| Observed but unapproved | NOT_APPROVED | NOT_VERIFIED |
| After approval | LAB_APPROVED | VERIFIED_FOR_LAB_CHECKS |

**History.**
- Explicit HISTORICAL_VERSION_ROUTING over the preserved v1 and generated v2 revisions reproduced the frozen
  routed reference.
- 2024 stays at 1 634 542.08. The naive single-metric query would have rewritten 2024 to 1 615 473.58.

**P2.**
- Unchanged in YAML, manifest node and native output; it conforms to its oracle.
- A planted collateral P2 edit was detected, with row counterexamples.

**State honesty.**
- 11/11 malformed or unauthorized amendments were BLOCKED or UNRESOLVED, with no patch.
- No IMPLEMENTED or DEPLOYED state is reachable. The state is `PROPOSED_VERIFIED_NOT_DEPLOYED`.
- The fresh-process replay was byte-identical.

## What it does not show

- **No independent authorship.** This is an engineered hold-out: one author for the amendment, reference and
  transposer.
- **No generality.** Only a single, narrow delta kind with a fixed binding was tested. This is not general
  language-to-semantic-code automation.
- **No native bitemporality.** History required explicit version routing over preserved revisions.
- **Limited discrimination.** It is bounded by the registered snapshots: `> 120` was caught only by the designed
  fixture.
- **No real authority.** There is no real authority, identity, deployment, downstream BI/agent behaviour or legal
  compliance, and no evidence of demand.

## Next experiment (recommended, not executed)

**E6: reverse reconciliation** (plan §5, R7).

**Setup.**
- Hold the approved P1 v2 IR and the verified generated revision fixed as the deployed state.
- Have **someone or something other than the reference author** introduce implementation-originated changes into
  a disposable checkout:
  - at least one material change, e.g. a dbt staging change to `unit_price` rounding, or a status-normalisation
    change;
  - at least one harmless change.
- Sophon must classify each change against the still-applicable approved IR, with row-level evidence.

**Kill condition.** E6 fails, and the forward/reverse loop is not worth building further, if any of these holds:
- any material implementation-originated change is accepted as `NO_MATERIAL_DRIFT` on the registered snapshots;
- any harmless change is flagged;
- detection requires a per-change, hand-built fixture written after seeing the change.

**STOP: E6–E8 were not started.**
