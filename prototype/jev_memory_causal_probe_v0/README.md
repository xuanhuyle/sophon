# Jev memory-effect probe v0 — executable, narrowly bounded

**Question:** With *the same cheap Jev model and identical multi-label questions*, does passing the provisional source-linked provision-skeleton library learned from the GitHub 2021 SLA change supported normative-function decisions on authentic, later Google 2021 SLA excerpts?

**This is a REAL causal intervention on the classifier input**, not another architecture sketch. Ten literal source excerpts (including two full compound-function passages), 16 source-anchored positive function/modifier checks, **20 Jev calls total** (10 COLD + 10 LEARNED), one source-backed previously induced library (G1/G2/G4), no Claude, no reviewer, no trained models or stronger-model competition. The two arms differ **only** in one `state.prior_provision_skeletons` field. The input context, function definitions, per-label Noul questions, model and call parameters are held constant. We allow multiple functions simultaneously.

**Sub-provision categorization is NOT implemented yet.** The ten excerpts are split by explicit, *hand-selected* start/end markers (`CASES` in `probe.py`), and each excerpt receives a set of independent yes/no normative-function questions. The model does **not** find sub-provision boundaries itself and does **not** assign each detected function to a verbatim internal span. Two full mixed-function passages test whether multiple function flags can coexist, not true sub-provision extraction. **Do not report this probe as automated sub-provision parsing or categorization.** That capability is a separate next increment whose value should be decided after observing this source-memory intervention.

**Not established:** this is a single A→B library exposure, **not multiple demonstrated learning updates**; the annotations are narrow literal-positive probes selected by engineering judgment (NOT independent expert legal labels), and there is no certified negative-function oracle. Source-linked quotes do not make legal interpretations authoritative. A change in scores may reveal sensitivity to memory, but is **not proof of absolute legal correctness or successive contract expertise**. Even a flat result cannot refute all library learning. All source files, model adapters and preliminary library structures are historical on unmerged PR #17; the new code uses `git show` at a pinned full commit and fails if that history is missing.

### Already runnable offline, with no credentials

```bash
python prototype/jev_memory_causal_probe_v0/probe.py preflight
python -m unittest discover -s prototype/jev_memory_causal_probe_v0 -p 'test_*.py' -v
```

The preflight **loads and validates authentic historical source hashes**, the three provisional GitHub source-linked skeletons, all sixteen frozen positive probes, and constructs/verifies all 20 paired requests. It makes **zero network/provider calls**.

### Optional real Jev call run — requires separate explicit paid-call authorization

This run is **NOT included in the present authorization or CI**. It can be performed in a local environment with the TypeSafe key, after reviewing its 20-request budget:

```bash
# Set TYPESAFE_API_KEY in your local environment, never commit it.
python prototype/jev_memory_causal_probe_v0/probe.py preflight
python prototype/jev_memory_causal_probe_v0/probe.py live --confirm-paid-calls YES --output prototype/jev_memory_causal_probe_v0/live_runs/run_001.json
python prototype/jev_memory_causal_probe_v0/probe.py score --recorded prototype/jev_memory_causal_probe_v0/live_runs/run_001.json
```

The live command refuses without the explicit confirmation flag and key; the key is loaded automatically from the process environment or an existing .env at the repository root (or next to probe.py), without displaying it. A .env on your Windows machine does not automatically exist in Claude Code's cloud container. Never commit or paste the .env. The live command refuses overwriting existing recordings, never silently retries or falls back to fixture data, and caps at 20 API requests. Its recorded raw model/version and request hashes enable offline re-scoring. Local `live_runs/` recordings are gitignored; only share redacted summary/sha receipts if desired.

### Decision after real run

Report *per positive source anchor* COLD vs LEARNED `noul` yes-probability, newly detected explicit functions/modifiers, lost detections, and all output functions including unscored ones. Evaluate also whether the library incorrectly transfers another contract's specific figures or parties, but do not automatically score such claims as legal correctness absent verified labels. A 100% cold ceiling is **INCONCLUSIVE about benefit**, not an automatic NO-GO.

Proceed to a second library update or a broader held-out independently checked corpus **only** if the real result identifies a discriminating weakness. If library has no effect, first verify Jev actually consumes the optional state field; do not pile on reviewers or a new framework to force a positive result.

**One genuine engineering risk:** Jev's typed Noul API gives probability rather than source quotations; the provision excerpts and library quotes are source-verified by our code, but **Jev's answer itself is not independently source-anchored**. Additional verification is separate future work if its incremental benefit justifies the cost. No agent approval, executable rules or downstream action occurs here.
