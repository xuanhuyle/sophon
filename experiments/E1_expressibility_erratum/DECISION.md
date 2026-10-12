# E1 expressibility erratum: decision

**CONFIRMED_E1_ERRATUM.**

The verdict is applied mechanically from PROTOCOL.md §7 (`src/gate.py` → `evidence/gate.json`). All eight
gates hold:

| Gate | Result |
|---|---|
| G1 source identity | equal to E0 |
| G2 genuine native `mf` witness | runs with the exact E2 text; compiled SQL obtained and read |
| G3 yearly equality with an independent raw-CSV oracle | 2024 1 634 542.08, 2025 1 400 232.75, 2026 752 191.54 |
| G4 line-level equality | 3 305 lines |
| G5 guards on the pinned rows | quantity ≥ 1; revenue = q × u exactly; prices exact; line ids unique; exact comparison |
| G6 anti-vacuity | witness < status-only < unfiltered; a below-threshold line in a mixed order is excluded; `Dimension('sales__unit_price')` is rejected while the metric filter is accepted; `unit_price` is not listed |
| G7 negative controls | negative and zero quantity break the derivation and the capability check refuses; the 99.99 / 100.00 / 100.01 boundary is exact |
| G8 capability check | 9 tests pass |

## Corrected E1 conclusion (one sentence)

On the pinned estate, E1's B1 requirement is **not directly exposed but is natively derivable** through
MetricFlow metric filters at sales-line grain. This holds only under guards (quantity > 0, exact
revenue = quantity × unit price, unique line entity) that the data satisfies and the semantic layer does not
enforce. E1's B1 classification, its "B1 correctly classified" claim and its PASS_KNOWN_BINDING as a
substantive verdict are therefore withdrawn. E1's case A, case B2 and its other safety findings stand
(ERRATUM.md §4).

## What this does not show

- Any pattern other than this one.
- Any estate other than this synthetic snapshot.
- That the guards will keep holding.
- A general method for finding derivations. The witness was supplied by E2, not discovered here.
- Independence of the replication: the same orchestrator wrote E0–E2 and this erratum.

## E3 prerequisite (recommended, not executed)

Start E3 from its own specification on a **new branch based on this erratum PR's head**. The direct technical
prerequisite: E3's validator must not reuse E1's dimension-only exposure rule as an expressibility verdict. At
minimum it must:
1. carry the four classes of ERRATUM.md §3;
2. represent a derivation as a native query, plus its proof obligations (guards) and their observed status on
   a named data snapshot;
3. refuse the derivable class when a guard is missing, unevaluated or false (as `src/capability.py` does for
   this pattern);
4. record guards as data assumptions that are re-checked when the data changes.

**STOP: E3 was not started.**
