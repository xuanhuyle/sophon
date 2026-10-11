# Run log (append-only, written by the orchestrator as runs complete)

Model for every solver and auditor context: `claude-fable-5-1` (session `get_session`: `session_context.model` and
`external_metadata.last_served_model` both `claude-fable-5-1`; effort setting of the session: ultracode). Each run is a
fresh subagent context pointed only at its staged directory. Tool-call counts and leakage flags come from
`src/audit_transcripts.py` over the subagent transcript (`AUDIT.json` in each frozen run directory).

| Round | Arm | Task | Staged prompt sha256 (first 12) | Agent transcript id | Tool calls | Assistant turns | Wall-clock (s) | Leakage flags | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | A | T0 | 84051a06530e | adc6d21fa4abb6cf6 | 31 | 53 | 1577 | none | 34 links (26 VERIFIED / 5 INFERRED / 3 UNKNOWN); found D632-1 floor mismatch; built a proposal fixing it; abstained on AE Acre rates |
| 1 | B | T0 | b32284f8cfbf | ae6cba687db0193d2 | 26 | 49 | 1422 | none | 55 links (34 VERIFIED / 10 INFERRED / 8 UNKNOWN / 3 FAILED recorded); store verify-store OK; same D632-1 finding; two further executable mismatches (CIPAV Acre leak, Acre degressive zone) |
| 2 | A | T1a | eb1ea45292f5 | ad9477f41ac571cfd | 25 | 47 | 902 | none | Found the S0→S1 delta (D613-4, D613-6 re-issued by Décret 2024-484, future versions by id/date only); 4 AFFECTED, 6 NEEDS_REVIEW (incl. the 4 DROM rules), 25 UNAFFECTED; abstained on all 2024-07/2025/2026 values; proposal adds citation notes and a "taux à confirmer" notification; build OK |
| 2 | B | T1a | 4e9a9b5b83f2 | a707eaecf844afc99 | 22 | 62 | 1100 | none | Same S0→S1 delta found; rate rules classified NEEDS_REVIEW (high) rather than AFFECTED, RCI rule AFFECTED, DROM NEEDS_REVIEW; abstained on all future values; store: S1 and proposal registered, revalidate run, 19 links added (74 total, verify-store OK); traceability-only proposal, build OK |
| 3 | A | T1b | 1f783b59ece9 | a078aea63f1217cf2 | 27 | 46 | 1222 | none | 7 changed articles, 52 rules classified (20 AFFECTED), 35 evaluations, 9 abstentions, proposal builds OK |
| 3 | B | T1b | fa992c95fc55 | a87ca64f615719503 | 25 | 58 | 1315 | none | 81 rules classified (22 AFFECTED / 20 NEEDS_REVIEW / 39 UNAFFECTED), 15 transposed numbers with quote + version id, 9 abstentions; proposal builds OK (641/1226); store: revalidate S3×G1 flagged 36 REASSESS_LAW_CHANGED + D136-5 unlinked, 35 links added (109 total, verify-store OK) |
| 4 | A | R1 | 663a38a98db6 | ad80cffbd5725253d | 16 | 30 | 471 | none | HARMLESS_REFACTOR (high): one `références` URL changed; before/after trees built and 69 evaluations byte-identical; noted (context only) that G1 still computes 21,1/21,2 while D613-4 in force since 2024-07-01 says 23,1/23,2 |
| 4 | B | R1 | 3a00c225212c | a8afc5d0dc2b0524f | 20 | 55 | 876 | none after review | HARMLESS_REFACTOR (high); reconstructed the before-tree by reverse-applying the patch (no git); 11 store reports. The first audit pass flagged 3 "GIT" hits; manual review of the commands showed only the word "git" in heredoc prose ("a git diff", "git-quoted paths", "not a git checkout"); the detector was tightened to match git commands only and all runs re-audited |

Both T0 solvers independently noted that the engine's `durée` mechanism reads the real wall clock rather than the
situation date, and worked around it by fixing durations in the situation. Both abstained on the micro-entrepreneur
Acre rates (governing article outside the bounded set).
