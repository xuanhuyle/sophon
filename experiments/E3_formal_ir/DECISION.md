# E3: decision

**PASS_IR_GUARD_VALUE.**

The verdict is applied mechanically from PROTOCOL.md §7 (`src/gate.py` → `evidence/gate.json`). It is scoped to
the 54 preregistered scenarios and must be read together with the post-hoc gap in RESULTS §6.

## Why PASS

- **All four scenarios behaved as preregistered** (54/54 on the first scored run; 0 false VERIFIED).
  - S1 is DERIVED and becomes VERIFIED only with:
    - an approved reading;
    - all five guards on the same snapshot as the native receipt;
    - native = oracle.

    Missing, undeclared, failed or other-snapshot guards, and corrupted grain or expression, all block it.
  - S2 stays MEANING_UNRESOLVED while both native readings execute. One valid simulated choice promotes only that
    reading, and the other is kept as NOT_SELECTED. All twelve approval attacks block.
  - S3 stays unresolved without a scoped equivalence approval, despite the correct query. The approval promotes
    it; revocation or removal withdraws the promotion immediately.
  - S4 stays MISSING_REQUIRED_FACT even when the status proxy executes, matches its own oracle and carries a
    roster-valid simulated equivalence approval.
- **Bounded VERIFIED statuses rest on fresh native MetricFlow receipts** that equal independent raw-CSV oracles
  (erratum and E2 code, unmodified): S1, S2 customer reading and S3.
- **Five material invariants are enforced mechanically that E1 lacked or had only in part.**
  - Fully new:
    - computed-only status and claimed approvals (U2, U7);
    - unresolved alternatives block promotion (U1);
    - approval scope, roster, self-approval, effective window and as-of visibility (U5).
  - Partly in E1: revision binding (U3).
  - Already in E1: the designation check that rejects the status proxy (U4). E3 only adds that an approval
    cannot override it.
- **The fresh-process replay is byte-identical.**

## What this does and does not show

It shows, for four LAB_AUTHORED clauses on one synthetic estate, that a plain typed JSON record plus a small
read-only validator can keep three things apart mechanically, with each guarantee able to fail:
- approved meaning;
- native computability;
- independent evidence.

It does not show:
- that the invariants are novel; Pydantic and ordinary code enforce them;
- legal or business correctness;
- that `customers.country` means residence;
- reliability on authentic requirements;
- protection against consistent forgery of receipts.

**Post-hoc gap (non-scored).** A requirement that is not in force at the evaluated effective date can still be
marked VERIFIED, because only date ordering is checked. Before any reuse, this must be fixed as the first item
under a new protocol. It is not a reason to rewrite this verdict.

## Next experiment (recommended, not executed)

**E4: independent native semantic verification**, on a new branch from this PR's head. Use E3's records for S1
(derived) and S2 (approved customer reading) as the approved specifications. Then:
- introduce **wrong-but-plausible native implementations** in a disposable dbt/MetricFlow copy. Examples:
  - a `completed_revenue` filter changed to `!= 'cancelled'`;
  - a store-country join substituted for the customer-country join;
  - a price threshold implemented as `> 100` instead of `>= 100`;
- check that the frozen independent oracles reject each one, with a counterexample.

Two small prerequisites come first, under E4's own protocol:
1. add the requirement-in-force check (RESULTS §6.1);
2. re-execute native queries and oracles live for every promoted case, instead of trusting cached receipts
   (§6.2).

**STOP: E4–E8 were not started.**
