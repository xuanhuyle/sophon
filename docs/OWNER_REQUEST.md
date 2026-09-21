# Requests to the owner

Nothing below has been done or assumed. `lab/ledger/owner_acts.json` is empty, and the lab returns
`REQUEST_AUTHORITY` for all 48 cases until you change that yourself.

## 1. One permission (recommended; about a minute of your time)

**May I run the recurrence study across your Claude Code history?**

- What it reads: `~/.claude/projects/*/*.jsonl` on this machine, for every project, not only this one.
- What it keeps: counts only. It never prints or stores a command, path, URL or prompt. A Bash call is reduced to the
  tool name plus the program name if it is on a short list of common programs (otherwise "other"); finer levels are
  salted hashes. Read the code first: `analysis/permission_log_study.py` (about 120 lines).
- What it answers: in a real agent workload with a real authority holder, how quickly does "settle each new kind of
  action once" turn into autonomy, and how does that depend on how far a settlement may generalize? This is the
  amortization question on real data, which nothing in the packet can answer.
- What it cannot answer: whether those settlements would be *right*, or anything about business policy.

```bash
python -B analysis/permission_log_study.py --all
```

I ran it on this project's single session only, as a smoke test (92 tool calls; not evidence).

## 2. Optional: reproduce the full-file IPSA base rates

The packet reports 18 "Not Paid" and 446 "Repaid" of 82,787 rows. Checking that means downloading
`individual_business_costs_2023_24.csv` from `www.theipsa.org.uk` (the packet's own `replay.py fetch`; size not
stated in the packet, 91,567 rows). I did not download it. Say so if you want it checked.

## 3. Optional: exercise the lab end to end (about 30–45 minutes of your time)

I do not recommend this as an experiment: both architectures give identical decisions for every possible settlement,
and at most 8 of the 24 held-out cases can be moved by anything you decide (`docs/REPORT.md` sections 4.5 and 6). It
is worth doing only to feel the workflow and to time yourself. If you do, these are the decisions, in order.

1. **Adoption.** Record this statement verbatim with a timestamp, or edit the draft first (then the hash changes):
   > I adopt the attached `draft_policy.md` for the fictional Sophon Lab sandbox, effective at [timestamp]. I
   > understand that it has no effect on IPSA, any real employer or any actual reimbursement.

   Current draft SHA-256: `ebee78addf435659fb7e36afc1e9ea0a6a72d4b747dee599b142ddf10fd0a04b`.
2. **Closure rule.** The draft never says what *is* reimbursable. Choose `ALL_CLAUSES_SATISFIED` (a claim that meets
   every clause is payable) or `SAFE_HARBORS_ONLY` (nothing is payable without an explicit grant from you).
3. **Does manager approval apply beyond travel?** The draft requires it only for travel. Choose `ALL`,
   `TRAVEL_ONLY`, or leave it for case-by-case review.
4. **What does "applies from its effective time" reach?** Expenses incurred after it, decisions made after it, or
   (the lab's conservative default) only cases where it was in force at both times.
5. **The dispositions in `lab/READING.md`.** In particular: is a claim that includes a tip blocked as submitted (the
   lab's reading) or paid net of the tip? Is a self-approved claim blocked, or sent back for another approver?
6. **The two orphan columns.** `transport_alternative_available` and `after_2200_work` have no clause. Add a taxi
   clause, or confirm they are unused.

The open terms (`hotel.reasonable`, `meal.modest`, `equipment.necessity`) are then settled, or deliberately left
unsettled, while you work through cases 1–24. Time each one from first look to recorded decision, including the ones
you reject.

How to record: fill in `lab/ledger/owner_acts.json`, then run `python -B -m lab.run_lab` and read section 1 of its
output. Shape of the file (placeholders, not suggestions):

```json
{
  "owner": "<your name>",
  "adoption": {"issuer": "<your name>", "effective_from": "<ISO time>", "policy_version": "<the SHA-256 above>",
               "closure": "<ALL_CLAUSES_SATISFIED | SAFE_HARBORS_ONLY>"},
  "acts": [
    {"type": "INTERPRET_OPEN_STANDARD", "issuer": "<your name>", "recorded_at": "<ISO time>",
     "effective_from": "<ISO time, not earlier than recorded_at>", "policy_version": "<SHA-256>",
     "payload": {"term": "hotel.reasonable",
                 "rules": [{"where": {"destination": "<city>"}, "max_amount": "<number>"}],
                 "outside": "<SEMANTIC_REVIEW | BLOCK>"}}
  ]
}
```

## 4. Housekeeping

I have not committed or pushed anything. Say if you want this committed to `main` and pushed to
`github.com/xuanhuyle/sophon` (private). The follow-up zip is extracted to `evidence_followup/`; the zip itself is
still in the repository root.
