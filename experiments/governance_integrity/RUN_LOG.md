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

Both T0 solvers independently noted that the engine's `durée` mechanism reads the real wall clock rather than the
situation date, and worked around it by fixing durations in the situation. Both abstained on the micro-entrepreneur
Acre rates (governing article outside the bounded set).
