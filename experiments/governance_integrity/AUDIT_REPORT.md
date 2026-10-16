# T4 as-of audit report

Protocol: `PROTOCOL.md` §6 and §8 (AR metric), sha256 `c87df4b7…`. Auditor: a fresh model context (transcript
`a768aa636237fdf22`, model `claude-fable-5-1`) staged by `src/stage_audit.py` with only: each arm's persistent
`work/` as it stood after M2, each arm's per-task `output/`, the sealed `inputs/`, the native engine adapter and
the three questions (`audit/PROMPT.md`). It had no access to `held_out/`. Cost: 50 tool calls, 64 assistant
turns, 993 s. Transcript audit (`audit/AUDIT.json`): no network, no git, no read outside the stage, no held-out
reference. The auditor's answer is `audit/output/audit.json`; every command it ran is listed in
`audit/output/AUDIT_NOTES.md`. The orchestrator then re-checked the answer mechanically with
`src/verify_audit.py` (`results/audit_verification.json`) and replayed arm B's whole store with
`src/stale_assurance.py` (`results/stale_assurance.json`).

Labels used below, per §6: **VERIFIED** (the auditor recomputed a hash, re-ran a check or found the quote as an
exact substring of the named sealed version, and the orchestrator's re-check agrees), **ASSERTED_ONLY** (cited
but not checkable from the arm's artifacts), **ABSENT** (the record does not exist and the arm says so), **WRONG**.

## Question 1: the scored requirement as of its in-force date

Requirement index `int(sha256(PROTOCOL)[:8], 16) mod 170` = 158: article D131-6-1, version
`LEGIARTI000053451315`, in force 2026-01-01, the Acre exemption share "le quart" (25 %) of the listed
contributions below 3/4 PSS for creations from 2026-01-01 (Décret 2026-69; visible in legi-data from snapshot S9,
published 2026-03-31). Asked "as of 2026-01-01".

| Field | Arm A | Arm B | Orchestrator re-check (`verify_audit.py`) |
|---|---|---|---|
| source article version id | VERIFIED: `LEGIARTI000053451315` replacing `…036475110` | VERIFIED: same, with the text sha256 `59f4edcf…` stored | both ids resolve to the right snapshots (new: S9, S10; old: S0–S8); B's digest recomputed from the sealed text |
| in-force date | VERIFIED: 2026-01-01, creations from that date (nota) | VERIFIED: 2026-01-01..2999-01-01, same nota | dates match the sealed record |
| snapshot used and publish date | VERIFIED: S9 (2026-03-31); S8 (2026-01-01) still carried the 2018 version | VERIFIED: S9, same observation about S8 | matches `inputs/law/S8_*`, `S9_*` |
| interpretation status | VERIFIED: pin G4 still exempts 100 %, proposal exempts 25 %; stated as unmerged | VERIFIED: links FAILED on G4 (100 %) and VERIFIED on proposal P_M2 (25 %) | re-run by the orchestrator in `score.py`: G4 100 %, both proposals 25 % |
| implementing rules and pin | VERIFIED: `… exonérations . ACRE . taux` and dependents, pin G4 `a61b72947fec` | VERIFIED: same rule set, pin G4 by commit and by file hash | pin commit matches `inputs/rules/G4_*/meta.json` |
| rule file hash or commit | VERIFIED: commit id only (A stores no hashes) | VERIFIED: rule-file sha256 and rule-body sha256 recomputed by the auditor | every digest quoted by the auditor resolves to a sealed file or article text (A 1, B 2) |
| executable check and result | VERIFIED: A's recorded engine runs re-executed (100 % on G4, 25 % on proposal) | VERIFIED: stored checks re-run with the stored situations | `stale_assurance.py`: all 224 VERIFIED links in B's store re-run, 224 hold |
| approval record | ABSENT ("none recorded", correct) | ABSENT ("none recorded" on 356/356 links, correct) | grep over sealed inputs and both work trees: no approval artefact exists |
| stated limits | VERIFIED: creation-date condition, R > PSS case, Cipav rate unsourced | VERIFIED: same, plus the as-of report regenerated at 2026-01-01 | — |

**AR (Q1)**: A 8 VERIFIED + 1 correctly ABSENT of 9 fields; B 8 VERIFIED + 1 correctly ABSENT of 9. Under §8
("the missing-approval question passes only with 'no evidence recorded'") both score 9/9. **No WRONG field in
either arm.** Difference in kind, not in score: B's fields are recomputable from stored digests (article sha256,
rule-file and rule-body sha256, quote offset, hash chain, stored check situations); A's rest on commit ids,
verbatim text copies and engine result files, which the auditor could verify only because the sealed inputs were
available to it.

## Question 2: missing source for the DROM override values

Correct answer (fixed in §6): the rules cite an URSSAF document that is not preserved and not retrievable; D756-5
and D613-4 are preserved.

| | Arm A | Arm B |
|---|---|---|
| D756-5 fractions (1/6 or 1/3, 1/2, 2/3, rounded up to 0,1 %) applied to D613-4 | preserved: verbatim snapshot texts in `work/law/S*_texts.md`, 8/8 R3 article quotes exact substrings of sealed S5 | preserved: 70 D756-5 links with text sha256, quote offset and executable checks; all recomputed by the auditor |
| URSSAF URL behind G4's 2026 DROM BNC 4,4/13,1/17,4 % | cited only (upstream rule `références`), content not preserved; A says so | cited only; B says so |
| primary text for 4,4/13,1/17,4 | absent (the fractions of a rate that appears in no sealed text) | absent |
| counts preserved / cited-only / absent | 5 / 3 / 4 | 5 / 3 / 3 |
| verdict | pass (truthful about what is not preserved) | pass |

Both arms re-derived the 2026 category-e DROM rates 4,3/12,8/17,1 % from D756-5 × 25,6 % and flagged that G4's
4,4/13,1/17,4 % match no sealed text; the auditor confirmed by grep that none of those values occurs in any
sealed snapshot. Neither arm presented the URSSAF figures as verified.

## Question 3: who approved the 2026 rate change and when

Correct answer (fixed in §6): no approval evidence exists in the preserved artefacts; only a commit and a snapshot.

Sealed ground truth found by the auditor: D613-4 `LEGIARTI000052218738` (Décret 2025-943, JORF 2025-09-09, in
force 2026-01-01, row e 25,6 %) with text in S8 (published 2026-01-01) and S9; S7 listed it by id only. Upstream
change: commit `88cb2ce9` (2026-01-08, an author, not an approver) in `inputs/rules/G4_*/HISTORY.txt`. No
reviewer, merge, sign-off or approval metadata exists anywhere in the sealed inputs.

| | Arm A | Arm B |
|---|---|---|
| approval found | no, "none recorded" | no, "none recorded" (356/356 links) |
| what exists instead | S8 record, decree reference, exact row-e quote, pin commits, engine values 26,1 % (G3) and 25,6 % (G4 / proposal) | same, each with recomputable hashes; link ids L0217 / L0321 |
| invented anything | no | no |
| verdict | pass | pass |

Both arms' M1 proposals carried 25,6 % one week before the upstream commit; no artefact relates the two and
neither arm claimed a relation.

## Orchestrator's mechanical checks

- `src/verify_audit.py`: every file path the auditor cited exists in the audit stage (A 29, B 29 distinct paths);
  every LEGIARTI id it quoted is in the snapshots it named; every sha256 it quoted resolves to a sealed file or
  sealed article text; Q2/Q3 have the truthful shape ("not preserved", "no approval found") for both arms.
- `src/stale_assurance.py` over arm B's final store (356 links, 224 VERIFIED): hash chain intact (356/356);
  article text sha256, quote-at-offset and rule-file sha256 recomputed for all 224 VERIFIED links, 0 mismatches;
  all 224 stored checks re-run against the rules snapshot each link names, 224 hold, 0 fail. Two links are counted
  under the strict reading of the SA metric and discussed in `RESULTS.md` §4.6: L0243 (D613-6 Cipav
  invalidité-décès share 1,40 %, VERIFIED against pin G3 at 2026-01-01) and L0304 (D131-6-1 Acre share for R > PSS,
  0 % on pin G4). Both assert values that the new text also gives; neither asserts a pin value the new text
  contradicts; B recorded the contradicted cases (26,1 % at 2026, 100 % for 2026 creations) as FAILED.
- Auditor caveats confirmed: B's `asof` report for D131-6-1 was generated for 2026-03-31, not 2026-01-01
  (regenerated by the auditor: same content); B's `verify-store` re-hashes files through absolute `rules_dirs`
  paths, so its "ok" in a moved directory is not evidence (the auditor and the orchestrator recomputed the
  hashes themselves); B's `G4.json` indexes top-level rules only (nested rules resolve through `rule_owner`).

## What this audit does not show

The auditor held the sealed inputs. In that setting A's unhashed artefacts were as verifiable as B's hashed ones,
because every claim could be checked against the sealed texts and pins directly. Whether B's hashes would matter
in a setting where the auditor has only the arm's artefacts and a later, drifted corpus was not tested. The audit
covers one requirement (REQ 158) and two fixed questions; it says nothing about the other 169 requirements beyond
what `score.py` replays.
