# Decision

**STOP_KERNEL.**

Applied mapping: `PROTOCOL.md` §8, frozen at sha256 `c87df4b7…` before any solver run. No threshold, metric
definition or acceptable-label set was changed after the runs. Where the preregistered reference set contains
rules whose implemented value the changed text does not alter, both the preregistered ("strict") count and a
value-corrected count are shown; the decision is the same under either reading. Inputs: `results/SCORES.md`,
`results/scores.json`, `results/stale_assurance.json`, `results/audit_verification.json`, `AUDIT_REPORT.md`,
`RUN_LOG.md`.

## 1. Primary outcome (T3: M0, M1, M2 impact recall, false-safe, cost)

| Task | Metric | Arm A | Arm B | Reading |
|---|---|---|---|---|
| M0 (no-op) | rules flagged AFFECTED (reference set empty) | 0 | 8 | B's 8 are rules carrying hard-coded 2026 branches that no sealed text supported; A put the same rules in NEEDS_REVIEW (33). Both said no in-force change occurred |
| M1 | IR strict | 20/21 | 20/21 | equal |
| M1 | FS strict (high confidence) | 1 (1) | 1 (1) | equal; the same rule in both arms (Cipav invalidité-décès share, 1,40 % in both versions) |
| M1 | IR / FS value-corrected | 20/20, 0 | 20/20, 0 | equal |
| M1 | tool calls | 32 | 32 | equal |
| M2 | IR strict | 7/9 | 7/9 | equal (B's ninth rule is NEEDS_REVIEW, A's UNAFFECTED) |
| M2 | FS strict (high) | 2 (2) | 1 (1) | B lower by one rule: `dirigeant . exonérations . ACRE`, the eligibility question, which the new D131-6-1 version does not alter; A's UNAFFECTED label is correct in substance |
| M2 | IR / FS value-corrected | 7/7, 0 | 7/7, 0 | equal |
| M2 | tool calls | 43 | 39 | B 9 % lower |
| T3 total | tool calls | 107 | 98 | B 8 % lower |
| T3 total | transposition correctness (reference replay, correct / incorrect / not transposed) | 22 / 0 / 0 | 22 / 0 / 0 | equal |

## 2. Secondary outcomes

| Metric | Arm A | Arm B |
|---|---|---|
| AR, Q1 (fields VERIFIED or correctly ABSENT / 9) | 9/9 | 9/9 |
| AR, Q2 missing source | pass | pass |
| AR, Q3 missing approval | pass | pass |
| T1b transposition (7 decree constants present; arm's own evaluation rows replayed) | 7/7; 28/28 | 7/7; 15/15 |
| T1b false-safe (strict; value-corrected) | 2; 1 (A labelled the IJ assiette rule UNAFFECTED while noting its value changes, a genuine labelling error) | 1; 0 |
| T1a abstention on text-less future values (9 rule-dates) | 9/9 abstained | 9/9 abstained |
| T1a IR strict (AFFECTED only; B chose NEEDS_REVIEW for the rate rules) | 4/9 | 0/9 |
| CFC (high-confidence label outside the acceptable set, R1–R5) | 0 | 0 |
| EI (claimed quotations found in a staged text / claimed; FAB = 0 both) | 123/123 (48 non-quotation strings in quote fields excluded; the classifier counted one of them, "notification only", as not found) | 438/438 (10 found with the arm's own annotation appended; 1 non-quotation string excluded) |
| SA, strict reading of §8 | not applicable (no store) | 3 rows (2 distinct links, both asserting values the new text also gives) |
| SA, stored checks that fail on re-run | — | 0 of 224 |
| hash-anchored evidence chain on every VERIFIED link | no hashes | yes, 224/224 recomputed |
| cost, all 11 tasks (tool calls / assistant turns / wall-clock s) | 314 / 538 / 11 180 | 301 / 640 / 12 927 |

## 3. The mapping, condition by condition

**STOP_KERNEL (i)**: B's IR ≤ A's IR and B's FS ≥ A's FS on M1 and M2 while B's COST ≥ A's COST. Holds on M1
(all equal), not on M2 (B's strict FS is lower, B's cost is lower). Not triggered.

**STOP_KERNEL (ii)**: SA ≥ 1 for B. Under the strict reading SA = 3 (links L0243, L0304 and one revalidation
row for L0243): VERIFIED assertions about reference-affected rules against the sealed pin in the new regime.
Under a value reading SA = 0: both links assert values (1,40 %; 0 % above the PSS) that the new text also gives,
and B recorded the values the new text contradicts as FAILED. **Triggered under the preregistered reading.**

**STOP_KERNEL (iii)**: B's AR ≤ A's AR on all three audit questions and B is not better on the primary outcome.
AR is equal on all three questions. Primary outcome: equal under the value reading; under the strict reading B
is "better" by one M2 false-safe that is a reference artefact (A's label is correct). **Triggered under the
value reading; under the strict reading it rests on counting a correct label as an error.**

**STOP_KERNEL (iv)**: the differentiator adds nothing A's notes did not already achieve. The store did what §1
says (diff-driven revalidation without a model call, as-of reports from stored hashes; `RESULTS.md` §4.6) and
the auditor confirmed its records are independently recomputable. But on the primary outcome and the audit no
scored answer differed: same impact sets, same transposed values, same five reverse labels, same abstentions,
same "none recorded" approvals, same audit reconstruction. The two secondary differences point in opposite
directions and are one label each: at T1b A mislabelled one affected rule UNAFFECTED (B did not); at T1a A
flagged the four rate rules AFFECTED where B chose NEEDS_REVIEW. **Triggered on the outcomes the mapping names;
not on process properties.**

**CONTINUE_BOUNDED** requires all of: B strictly better on the primary outcome (or strictly better on AR with
equal primary outcome); SA = 0; CFC = 0; one forward and one reverse episode scored; no incorrect D613-4 value;
EI ≥ 0,9; hash-anchored chains. CFC, episodes, D613-4, EI and chains hold. "Strictly better" holds only under
the strict reading, on one rule whose binding to the changed text does not hold; and under that same strict
reading SA = 3, so the SA = 0 condition fails. Under the value reading SA = 0 but the primary outcome is a tie.
**Not satisfiable under either reading.** §1's own forecast fixed the tie case in advance: "If A matches B on T3
and T4 after costs, the differentiator is not justified and the kernel stops."

**INCONCLUSIVE_EVIDENCE**: the reference was built for M1 and M2 (170 requirements, 143 fully observable); no
run is contaminated; the native runtime ran on every sealed input. Not applicable.

## 4. What is and is not concluded

Concluded, for this matched system, this model and n = 1 per cell: a persistent, hash-chained,
executable-check link store did not change the outcome of maintenance across two authentic successive changes,
of reverse checking, or of as-of audit, compared with the same model using native tools and free-form notes, at
about the same tool-call cost and higher token cost; on forward transposition the arms differ by one label each
way (T1b, T1a), with identical transposed values. The predeclared differentiator
(deterministic revalidation and hash-anchored as-of reports) worked as specified and produced correct statuses,
but everything it reported, the free-form arm also found by re-reading.

Not concluded: that provenance stores are useless in general; that the result transfers to BI semantic layers,
to downstream agents or to any business outcome (none was measured); that the result holds when the auditor
lacks the sealed inputs, when the rule set exceeds one context, when runs are longer than eleven tasks, or
for other models. The task-order leak (`RESULTS.md` §2.1) and pretraining on the public upstream history inflate
absolute correctness symmetrically and do not affect the between-arm comparison.

## 5. Next action

Stop developing the kernel as a differentiator. Do not run another arm-A-versus-arm-B comparison of the same
shape on another corpus; the mechanism is not what limited either arm here. If the store is revisited, the only
experiment this result motivates is one that removes the condition under which the two arms were equal: an audit
where the auditor has the arm's artefacts but not the sealed inputs, on a corpus that has drifted since the
artefacts were written. That is a different hypothesis (preservation, not transposition) and would need its own
preregistration.

Reusable by-products, independent of the decision: the native Publicodes adapter (`src/publicodes_eval.mjs`),
the dated legi-data snapshot builder and the scorer-only reference (170 requirements with OpenFisca
cross-checks), the sealed-input and transcript-audit harness, and the engine quirks both arms documented
(`durée` reads the wall clock; unknown rule-body keys are dropped silently; rule values can depend on evaluation
order within one engine instance).
