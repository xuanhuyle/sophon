# Sophon: architecture investigation

An independent look at whether "Sophon", a control layer that lets AI agents act under written policy and widen
their autonomy as people resolve uncertainty, has a viable architecture. Done on 21 September 2026 from the packet in
`evidence/`, in answer to `Claude_Code_Sophon_Architecture_Prompt_2026-09-21.md`.

## Conclusions

1. **Don't build the proposed control plane or a new authorization kernel.** A competent policy-as-code setup gave
   the same decision as a purpose-built authority ledger on all 138,240 compared case decisions, and passed all 20
   adversarial probes once five ordinary conventions were added. Gateway enforcement for agents is already sold by
   the cloud vendors.
2. **The only part worth building is thin:** a ledger of typed, dated grants plus the workflow that turns a person's
   answer to an escalation into a single-use permit by default, or into a proposal for whoever is empowered to make
   a rule. Real adjudication works this way: in 46 published IPSA reviews about half contain a reusable reading, the
   person deciding the case cannot make it binding, and 4 led to a committed rule change.
3. **Whether that is a product is open and cannot be settled alone.** The real evidence leans against easy
   amortization: the largest share of disputes is discretion on unique facts, repetition is plentiful only at the
   level policy owners already cover with bright lines, and expenses are a domain where checking before acting
   prevents almost nothing (1 refusal in the 1,000-claim sample).
4. **Several of the packet's headline results do not show what they appear to.** The 1,000-claim replay returns
   `REQUEST_FACT` for every possible input; three of six authority-probe tests cannot fail; K1–K6 come without code.

A condensed web version of the report is published as a private artifact (open only to people the owner shares it with):
https://claude.ai/artifact/WPcfzHzh5jPqxYq3PVVvqD

Read `docs/REPORT.md` for the evidence, `docs/DECISION.md` for the recommendation and what would overturn it, and
`docs/OWNER_REQUEST.md` for what needs you.

## Jev assessment (added 21 September 2026, later the same day)

`docs/jev_assessment/JEV_IMPACT_ASSESSMENT.md` asks whether TypeSafe's Jev, a System One model that returns typed
decisions with probabilities instead of text, changes the conclusion above. Short answer: it does not. It touches one of
the four technical problems, fact extraction, and touches it as a cheaper proposer of facts the system may not trust.
The appendices beside it hold the evidence base: the Sophon ground truth used, the Jev evidence with vendor and
independent claims tagged separately, the verified fact sheet from a 17-agent research sweep, and the owner's brief.

## Reproduce

Python 3.10+, standard library only. Run from this folder. Nothing writes inside `evidence/`.

```bash
python -B audit/audit_packet.py        # hashes, label recount, constant-function proof, mutation test of the packet's guards
python -B analysis/recurrence.py       # repetition in the 1,000 real claim rows, by granularity
python -B corpus_study/analyze.py      # agreement and tabulation of the two coding passes over 46 reviews
python -B -m lab.run_lab               # real (empty) ledger, 1,440-settlement differential sweep, 20 probes, mutation test
```

Outputs land in `results/`. The 46 source PDFs are not stored here; `corpus_study/shards.json` lists their official
URLs and the SHA-256 each matched.

## Layout

| Path | What it is |
|---|---|
| `evidence/`, `evidence_followup/` | The packet as supplied, untouched (the follow-up zip is extracted into the second) |
| `docs/REPORT.md` | Problem statement, assumptions, audit, experiments, alternatives, limits |
| `docs/DECISION.md` | Recommended architecture, trust boundaries, what would change the conclusion |
| `docs/FORECAST.md` | Predictions written before the lab was run, with `results/forecast.sha256` |
| `docs/OWNER_REQUEST.md` | The permission and the decisions only you can give |
| `audit/` | Mechanical audit of the packet |
| `analysis/` | Recurrence analysis; the proposed study of a real agent's action history (smoke-tested only) |
| `corpus_study/` | Codebook, shard lists, both coding passes, analysis |
| `lab/` | Two architectures over the 48 lab cases, 20 probes, runner; `lab/ledger/owner_acts.json` is the real ledger and is empty |
| `results/` | Everything the scripts above produced |

## Status

Committed and pushed to `main`. No policy has been adopted and no settlement recorded; every authority used in the
lab is fixture authority held in memory by fictitious principals.
