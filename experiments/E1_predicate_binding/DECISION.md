# E1 — decision

**PASS_KNOWN_BINDING.**

Applied as frozen in PROTOCOL.md §5 (commit `ee7db72`), without change after results.

| Condition | Observed |
|---|---|
| A verified for the lab calculation | FULLY_OBSERVABLE_FOR_THIS_CALCULATION; all three predicates bound, designated and natively exposed; metric definition consistent with the bindings; native `completed_revenue` = independent raw-CSV oracle per year to the cent |
| B1 correctly classified from real source and catalog evidence | PRESENT_IN_SOURCE_NOT_EXPOSED: `gold.fact_sales.unit_price` present with lineage and designated; absent from the native dimension list and every semantic model; MetricFlow rejected the probe filter natively |
| B2 correctly classified from the bounded inventory | NOT_FOUND_IN_BOUNDED_ESTATE, stated as not found in 155 columns / 5 raw headers, not as universal absence; estate fingerprint equal to the frozen inventory |
| Checks 4–9: no unsupported full verification | 4a–4d INVALID_BINDING; 5 NOT_FOUND with the identical native number; 6 UNVERIFIED (proxy refused); 7 INVALID_BINDING while the drifted native number changed; 8a/8b oracle rejects; 9 replay equal. All match EXPECTED.json |

Not PARTIAL: B1 was genuinely available. Not FAIL: nothing unexposed, missing, wrong or proxied was promoted, and
every identity or binding change changed the claim. Not BLOCKED: native runtime and inventory worked. Not
INCONCLUSIVE: the oracle agreed with E0's crosscheck and failed when its input or the compared value was altered.

## What this retires, and what it does not

Retires: **known-binding and observability mechanics for this tiny synthetic stack**. Given a supplied
interpretation and binding, a ~350-line evaluator over the native MetricFlow catalog and warehouse:
- separates "exposed and verified for this calculation" from "present in source but not exposed" and from "not
  found in the bounded estate";
- refuses an untrusted proxy;
- withdraws assurance when a required predicate is added, a binding is mutated, or the metric's native definition
  drifts.

Does not retire: R2/R3 under autonomous discovery; interpretation of ambiguous text or missing authority (case C
deferred); typed-IR value; independent verification of generated implementations; transposition; persistence and
audit; transfer to authentic requirements; Windows execution; that any real order status is or is not a
settlement fact anywhere outside this estate.

Unresolved uncertainties:
- The authority registry is the experimenter's designation; who designates authority, and how, in a real
  deployment is untested.
- The decision procedure handles only the predicate kinds needed here (sum measure, categorical equality, numeric
  threshold, time grain, external fact). Anything else is untested, not supported.
- B1-type gaps were classified, but closing one requires a native semantic change and approval, which is E5
  territory.

## Next experiment (recommended, not executed)

**E2 — autonomous relationship discovery**, on the same pinned upstream, metric and LAB-REV-1 family, reusing the
E0 adapter and this evaluator as the scoring harness. Withhold `bindings` and `authority_registry` from the
solver. Let it propose clause → predicate → semantic-object bindings, including abstentions, for A, B1 and B2 plus
a few unseen variants written and frozen before the run. Score the proposals with this evaluator and the frozen
expected outcomes: missed bindings, false associations, proxies accepted, unsupported FULLY_OBSERVABLE claims.

A small prerequisite: add a public `where` parameter to the E0 adapter, as an isolated reviewed change, so the
evaluator stops calling its private `_run`.
