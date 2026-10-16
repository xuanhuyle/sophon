# Target validity of the B3 OBLIGATION probes — post-run note, 2026-10-15

**Scope:** offline repair of how the completed 20-call run is *interpreted*. 0 provider calls; the frozen run, score, receipt and source are unchanged. This is not a re-score, not legal adjudication, not evidence of library learning, and not automatic sub-provision segmentation.

**Verdict:**
- The single observed COLD → LEARNED regression (`B3whole:OBLIGATION`) rests on a **contested target**. It is neither an established error nor an established improvement.
- With both contested B3 OBLIGATION expectations bracketed, the arms tie at **14/14 vs 14/14** on source-positive engineering checks, which is a ceiling.
- Further model-learning pilots on this probe set are **HOLD**: they cannot be interpreted.

Spans and the arithmetic below are checked in CI by `TargetValidityTests` in `test_probe.py`, against `target_spans_2026-10-15.json` and the frozen source at `b9d698c`. The packet hashes verify: B3 `5fd249c7…`, B2 `72df1f0c…`.

## 1. Exact-span evidence (Google Cloud Storage SLA, 24 June 2021)

Offsets are character positions in the frozen packet's `text`, or in its `context` for U7/U8. Each quote occurs exactly once. A matching quote does **not** validate any reading of it.

| Unit | Packet [start, end) | Exact words | (a) What the words directly say | (b) Relation to other units | (c) Independent enforceable obligation? |
|---|---|---|---|---|---|
| U1 | B3 text [0, 38) | "Customer Must Request Financial Credit" | Heading. "Must" is used, and the object is a request for the Customer's own benefit. | Heads U2–U5. Not part of the probe excerpts B3a/B3whole, which start at U2; it is present only via `context`. | Unresolved; a heading is not operative text. |
| U2 | B3 text [40, 104) | "In order to receive any of the Financial Credits described above" | States a purpose: obtaining credits. | Makes U3/U4 a means to the Customer's credit entitlement (the B2 Financial Credit definitions). | — (frames U3) |
| U3 | B3 text [106, 151) | "Customer must notify Google technical support" | Deontic "must" syntax with an affirmative act by the Customer. | Subordinated to U2 ("In order to receive…"); its consequence is U5. | **Contested.** The syntax is a duty, but the only stated consequence of non-performance is loss of the Customer's own right (U5). No sanction or claim for Google is stated in the packet. |
| U4 | B3 text [152, 236) | "within 30 days from the time Customer becomes eligible to receive a Financial Credit" | Time limit; its trigger is eligibility, which is not defined in the packet. | Time limit on U3. | — (modifier: a DEADLINE on the notice act is supported by the words) |
| U5 | B3 text [238, 338) | "Failure to comply with this requirement will forfeit Customer's right to receive a Financial Credit." | The consequence of not doing U3/U4 is forfeiture of the Customer's right. | Calls U3/U4 a "requirement" and attaches only a loss of right. | Supports reading U3 as a **claim prerequisite / condition of a right**, not as a covenant that is independently enforceable against the Customer. Not adjudicated. |
| U6 | B2 text [142, 225) | "the Covered Service will provide a Monthly Uptime Percentage to Customer as follows" | Service-level undertaking ("will provide"). The grammatical subject is the Covered Service, not Google. | Followed by the SLO table and, via U8, by credits as the sole remedy. | **Contested in the other direction.** The words state an explicit service commitment, which the probe question names, but U8 limits the remedy for failure to credits. |
| U7 | B3 context [540, 664) | "if Customer meets its obligations under this SLA, Customer will be eligible to receive the Financial Credits described below" | The SLA itself calls the Customer's SLA requirements **"obligations"**, framed as a condition of eligibility. | Applies to U3/U4. | **Cuts against the mislabel hypothesis.** The document's own vocabulary is "obligations", even though their stated function is conditional. |
| U8 | B3 context [767, 862) | "This SLA states Customer's sole and exclusive remedy for any failure by Google to meet the SLO." | The remedy for U6 failing is limited to SLA credits. | Bounds U6. | Makes U6's enforceability limited, but U6 is still stated as a commitment. |

**What can be asserted offline:**
- Only the exact words, and two facts about them. U3 combines duty syntax ("must") with a consequence that falls solely on the Customer's own right (U5). The SLA labels such requirements "obligations" (U7).
- Whether U3 counts as an OBLIGATION therefore depends on Sophon's **taxonomy definition**. The question is whether a condition attached to one's own right, carrying a forfeiture, is a duty. Neither the source nor the probe question settles that. The probe question reads: "An explicit affirmative duty or service commitment imposed by this clause." Read literally, it arguably *includes* "must notify".
- So the original expectation that B3 states an OBLIGATION is **neither clearly wrong nor clearly right**: it is contested.

## 2. Sensitivity of the recorded score (interpretation only; the frozen score stands)

| Probe set | n | COLD passed | LEARNED passed |
|---|---|---|---|
| As recorded (frozen, unchanged) | 16 | **15** | **14** |
| Bracketing the contested `B3a:OBLIGATION` and `B3whole:OBLIGATION` | 14 | **14** | **14** |

Recorded probabilities for the contested probes (`score_jev_memory_20261014_approved_001.json`):
- `B3a:OBLIGATION`: COLD 0.26, LEARNED 0.28.
- `B3whole:OBLIGATION`: COLD 0.51, LEARNED 0.34.

This bracketing was chosen **after** seeing the result, so it is a sensitivity check, not a new score. What it shows:
- The apparent one-check regression exists only under the contested assumption.
- If the assumption were false, COLD's B3whole "pass" at 0.51 would have been a pass on a wrong target, and LEARNED's move to 0.34 would point *toward* the prerequisite reading. Neither direction is established.
- 14/14 vs 14/14 is **not** 100 % legal accuracy, not a successful library, and not proof that Jev is correct. The remaining checks are positive-only, engineering-selected and not legally validated, and there are no independent negatives.

## 3. Alternative explanation: a defective annotation rather than an inability to detect obligations

Suggestive evidence from the recorded COLD arm:

| Excerpt | OBLIGATION | PERMISSION_RIGHT | CONDITION |
|---|---|---|---|
| B2a, the U6 service-level undertaking | 0.87 | 0.20 | 0.76 |
| B3a, the U2–U5 notice requirement | 0.26 | 0.73 | 0.98 |
| B1a, "the Application is responsible for waiting" (Back-off Requirements) | 0.65 | 0.07 | 0.87 |

- Jev does report OBLIGATION for an explicit commitment (B2a) and for a Customer-side responsibility shown without a consequence (B1a).
- For B3a it reports a conditional right: PERMISSION_RIGHT 0.73 with CONDITION 0.98. That matches the U2/U5 prerequisite reading.

**Why this is not proof:**
- One sample per arm, and Jev's run-to-run noise is unknown.
- B2a and B3a differ in party, heading, context and length, not only in normative structure.
- The B2a "commitment" is itself remedy-limited (U8).
- B1a is weak support. In the full document, the Back-off Requirements are also condition-like ("Repeated identical requests do not count towards the Error Rate unless they conform…"). That sentence falls outside the B1a excerpt, so B1a may score high only because its consequence is not visible.

**One counterexample that would falsify the "Jev separates prerequisites from duties" explanation:** an *authentic* clause from this SLA family in which the Customer is under a standalone duty with a stated consequence other than loss of its own right. Examples would be a breach remedy for the provider, suspension, or termination. If Jev returned OBLIGATION < 0.5 for such a clause, its low B3 score would reflect under-detection of Customer-side duties, not a distinction. No such clause is in the frozen packets, so none is invented here.

## 4. Next evidence bottleneck and decision

- **Bottleneck:** the error signal lacks independent normative ground truth, and it also lacks a taxonomy rule for the one case that produced a difference: a requirement that conditions one's own right, with forfeiture.
  - The fix is **not** model voting, an invented gold standard, new reviewers, a legal ontology, automatic segmentation or a data pipeline.
  - One explicit labelling rule is needed. Is a claim prerequisite with forfeiture an OBLIGATION, or a CONDITION on a PERMISSION_RIGHT? This is a product-semantics choice for the owner, or for a bounded one-time independent reviewer. Until it is made, this case is UNRESOLVED.
- **KEEP:** the paired same-model harness and this target note (spans checked in CI).
- **REVISE:** the B3 OBLIGATION expectation is now marked *contested*, not an error. Any future probe set needs at least some targets where COLD actually fails on an uncontested reading, plus some independent negatives.
- **HOLD:** a further model-learning pilot on this probe set. With the contested targets bracketed, both arms are at ceiling (14/14), so no learning effect can show. Without the bracket, the only difference sits on an unresolved target. Either way, a new pilot would not be interpretable.
