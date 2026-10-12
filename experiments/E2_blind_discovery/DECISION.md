# E2 — decision

**PARTIAL_DISCOVERY_SIGNAL.**

Applied mechanically from the gates frozen in PROTOCOL.md §7 (freeze commit `6f736d7`). The blind run was sound:
a fresh, tool-less, history-less process with an audited packet. The solver got 4 of 6 cases correct under the
frozen rubric, with **zero false VERIFIED claims, zero proxy substitutions and zero invented evidence**.
Criteria 2 (≥ 5/6) and 3 (both representable positives) were missed.

What prevents PASS:
- **H6 (representable positive) was not verified.** The solver proposed the exact native query but declined to
  equate `customers.country` with "country of residence", because nothing in the packet documents that meaning.
  The frozen reference assumed it. This is an over-cautious abstention under the rubric. It is also a defect in
  the clause I wrote.
- **H3** was correct in substance (ambiguity named, no mapping accepted) but merged two predicates, which the
  frozen matcher counts as a missed predicate. A non-scored relaxation gives 5/6, still PARTIAL because of H6.

Not FAIL: no unsupported proxy, invented evidence or false full verification. The payment proxy (H1), the
unexposed e-mail domain (H5) and the "French market" ambiguity (H3) were all handled without assurance. Not
BLOCKED or INCONCLUSIVE: isolation and the scorer held, and the replay was identical.

Could a human-approved workflow compensate? Yes, for what was observed. The miss is caution, not error:
- every proposed native query that was executed reproduced the reference;
- the two open questions the solver raised (meaning of `customers.country`; which "French market") are exactly
  the questions an accountable owner would have to answer;
- an approval step that accepts or rejects the solver's flagged equivalences would have turned H6 into a
  verified mapping without the model inventing anything.

## What E2 shows and does not show

Shows, for one model, one sample, six LAB cases on one synthetic stack: a fresh model with only a packet can find
correct metric, dimension and physical chains, including near-match traps, and can separate present-but-unexposed,
missing and ambiguous facts without false assurance.

Does not show: an error rate; behaviour on authentic requirements or other estates; tool-using retrieval;
robustness across samples or models; that abstentions are well calibrated (one over-abstention observed).

## Also recorded: E1 erratum candidate

E1's B1 ("unit price ≥ 100") is natively expressible through MetricFlow metric filters at line grain, giving
exactly E1's raw-row values (PRIOR.md). E1's evaluator checked only dimension exposure, so E1's B1
classification was a conservative false negative. E1's files are unchanged; the owner should decide whether E1's
PASS_KNOWN_BINDING needs an erratum or a re-run with metric-filter awareness.

## Next step (recommended, not executed)

**E3 — minimal formal governance IR, scoped by what E2 observed.** Represent each requirement's predicates,
bindings and *explicit open questions* in typed JSON. Include "field meaning not established" (H6) and "reading
must be chosen" (H3) as first-class states with an approval slot. The validator must then:
- reject a binding whose semantic equivalence is unapproved;
- accept it once a (simulated) approval is recorded;
- capture metric-filter-expressible predicates, so the E1 blind spot cannot recur.

Reuse E2's six cases and solver output as inputs; do not build a DSL. Fix the E1 B1 classification first as a
separate small erratum, because E3's validator would inherit E1's dimension-only exposure check.
