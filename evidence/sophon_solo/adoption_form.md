# Sandbox owner action — not yet executed

This form is intentionally unsigned. The attached policy and cases have **no operative authority** until the experiment owner writes an explicit adoption instruction. A model, coding assistant or previous IPSA decision cannot fill it in for them.

## Initial adoption

Owner statement to record verbatim in the experiment log:

> I adopt the attached `draft_policy.md` for the fictional Sophon Lab sandbox, effective at [timestamp]. I understand that it has no effect on IPSA, any real employer or any actual reimbursement.

Before use, verify and display the current SHA-256 from `manifest.json`. If the owner edits the draft, compute a new hash, save a new policy version and freeze the case set again. No automated default acceptance.

## Prospective settlements

For each open term, display the relevant source clause and at least the specific triggering case. The owner can choose: keep review required; decide only this case; ratify a prospective interpretation; add a constraint; relax one; or amend the source. Record exactly:

```json
{
  "actor": "owner identity entered by participant",
  "act_type": "INTERPRET_OPEN_STANDARD | ADD_CONSTRAINT | RELAX_CONSTRAINT | CASE_EXCEPTION | AMEND_SOURCE",
  "target_policy_version_and_clause": "...",
  "triggering_case": "LAB-...",
  "proposed_effect": "...",
  "scope": "beneficiary, cost category, time, amount/effect limits",
  "effective_from": "...",
  "expires_at": "... or absent if explicitly ongoing",
  "reason": "...",
  "owner_confirmed_at": "...",
  "elapsed_human_seconds": "..."
}
```

The tool must distinguish the participant's policy choice from source entailment and may not mark a mere case approval as reusable interpretation.
