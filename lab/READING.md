# How the lab reads `evidence/sophon_solo/draft_policy.md`

The draft is **unadopted**. Nothing here has authority. This table is the reading both arms implement so that they
can be compared; every row is a choice the sandbox owner must confirm or change at adoption
(see `docs/OWNER_REQUEST.md`). Even "bright-line" clauses need a disposition, and choosing it is an interpretive act.

| # | Clause | Reading | If not met |
|---|---|---|---|
| R0 | (none) | **The draft never says what *is* reimbursable**, only what is required or excluded. Whether "meets every clause" is sufficient for payment is a closure rule the owner must state (`ALL_CLAUSES_SATISFIED`), or else nothing clears without an explicit grant (`SAFE_HARBORS_ONLY`). | `REQUEST_AUTHORITY` |
| R1 | 1 | Purpose is documented (non-empty). | `REQUEST_FACT` |
| R2 | 1 | Supporting evidence: `receipt_present == yes`. Blank or anything else is *not* yes. | `REQUEST_FACT` |
| R3 | 1 | No self-approval: `approver != claimant`. | `BLOCK` (as submitted) |
| R4 | 2 | Travel (hotel, travel) needs `manager_approved == yes`. | `REQUEST_AUTHORITY` |
| R4x | 1–2 | **Unlisted ambiguity.** The draft requires manager approval only for *travel*. Whether meals and equipment need it is open term `approval.scope`. It only matters when `manager_approved != yes`. | `SEMANTIC_REVIEW` until settled |
| R5 | 5 | Amount is a finite positive number; `> 1000` needs Finance approval; `> 5000` needs CFO approval. Thresholds are changeable only by `RELAX_CONSTRAINT` / `ADD_CONSTRAINT`. | `REQUEST_FACT` / `REQUEST_AUTHORITY` |
| R6 | 3 | Alcohol or tip component `> 0` makes the claim, **at the exact amount submitted**, non-reimbursable. A net resubmission is a different action. | `BLOCK` (as submitted) |
| R7 | 3 | Purpose "Team celebration" needs a case-specific owner approval (`CASE_EXCEPTION`). | `REQUEST_AUTHORITY` |
| R8 | 2 | Hotel: open term `hotel.reasonable`. | `SEMANTIC_REVIEW` until settled |
| R9 | 3 | Meal (not a celebration): open term `meal.modest`. | `SEMANTIC_REVIEW` until settled |
| R10 | 4 | Equipment from a non-catalogue supplier: if the catalogue lacks the item, unavailability must be documented (`REQUEST_FACT` otherwise). If the catalogue *has* the item, "business necessity" is open term `equipment.necessity`. A de-minimis exemption is a **relaxation**, not an interpretation. | `SEMANTIC_REVIEW` until settled |
| R11 | 6 | `requested_exception == yes` needs a matching `CASE_EXCEPTION`. | `REQUEST_AUTHORITY` |
| R12 | — | Rail/taxi: the draft has **no clause** about transport alternatives or late working, although `cases.csv` carries `transport_alternative_available` and `after_2200_work`. Those columns are therefore unused. | — |
| R13 | 8 | **Unlisted ambiguity.** "Applies from its declared effective time" does not say whether that means expenses *incurred* or decisions *made* after it. The lab takes the conservative reading: a settlement must be in force at both times. | `SEMANTIC_REVIEW` |
| R14 | — | Any category outside {hotel, meal, equipment, travel} is outside the adopted surface. | `REQUEST_AUTHORITY` |

Three of these (R0, R4x, R13) are not in the draft's own list of open issues. The draft also pre-digests facts that
are judgments in real life: whether a meal was a "team celebration" or a "work planning meeting" is exactly the
kind of question the Aquarone review turned on, and here it arrives as a clean column.
