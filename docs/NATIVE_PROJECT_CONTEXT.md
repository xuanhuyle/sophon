# Sophon native project-context guard

This is **development infrastructure**, not a Sophon product feature and not an additional agent. Its purpose is to stop new AI coding sessions from treating known components and historical experiments as if they had never existed.

## Authority and what loads

1. SOPHON_CHARTER.md v1.2 is the authoritative product definition. This branch includes it from charter PR #15.
2. PROJECT_STATE.json is a compact, machine-checked engineering snapshot: existing code, refs, observed results, limitations, current/held experiments and evidence links. Do not promote this snapshot into legal authority.
3. CLAUDE.md and AGENTS.md point to the same state. Claude Code loads its instructions; Codex reads AGENTS.md; GitHub-connected ChatGPT must retrieve the repository files explicitly.
4. Shared .claude/settings.json installs **SessionStart and UserPromptSubmit** command hooks. They validate charter/state and inject the same engineering context automatically (also after a session resume/compaction, provided the hooks run). Works in single-repository Claude Code cloud sessions and supported local sessions when the project folder is trusted. Uses installed Python as the only dependency; no network or provider calls.

**This does not magically synchronize GitHub with ChatGPT conversations, other repos, or branches that have not integrated these commits.** It does not guarantee an AI will follow the context, and it cannot algorithmically determine whether a proposed architecture is a redundant reinvention. It does make the right facts automatically available in Claude Code and exposes mechanical contradictions in CI.

**On an inconsistent state** the hook still exits 0 and injects `SOPHON_CONTEXT_GUARD_FAILED` plus each error as context, so the agent sees it and can repair the state. (Until 14 October 2026 it exited 2; Claude Code then shows stderr to the user only and blocks every prompt, including the one asking for the repair.) The `check` mode used by CI still exits 1.

## Verification status (14 October 2026)

| Item | Status | Evidence |
|---|---|---|
| Guard logic and regression tests | VERIFIED locally | `check` OK; 20 unit tests pass (Python 3.13, Linux). GitHub CI is reported separately on the PR. |
| Exact `.claude/settings.json` command runs and emits context | VERIFIED (interpreter substituted) | `test_settings_hook_injects_context` runs the committed command against a fixture repo, replacing only `python` with the test interpreter. Whether `python` resolves on a given host is NOT verified generally (absent by default on macOS and some Linux images; Windows may resolve a Store stub). |
| Hook fires in a fresh Claude Code session | OBSERVED once | One single-repository Claude Code cloud session (claude.ai/code) started on this branch at `44bfaf0`: harness reported `SessionStart:startup hook success` and `UserPromptSubmit hook success` with the injected text. |
| Local CLI (Windows/macOS/Linux), Claude Code Mobile, resume/compaction, live failure path | NOT_VERIFIED | No such session exercised. Multi-repository cloud sessions do not load project hooks (documented by Claude Code). |
| Agent actually follows the context | NOT_VERIFIED | Injection is not compliance. |

**Smoke test (about one minute, no code changes):** start a *fresh* Claude Code session on this branch, single repository, and send as the first prompt: `Without using tools, quote verbatim the line beginning "Branch:" and the line beginning "PR GRAPH" from any SOPHON NATIVE PROJECT CONTEXT you received; otherwise answer NONE.` PASS = both lines appear and the date matches `PROJECT_STATE.json` `updated_at`. NONE = hook did not load; run `/hooks` to see whether it is registered, then try `python .claude/hooks/context_guard.py hook` in that shell. To exercise the failure path, temporarily rename `pr_graph` in a scratch branch and expect `SOPHON_CONTEXT_GUARD_FAILED` in the next turn's context, not a blocked prompt.

## CI and regressions

Run locally or in Claude Code:

    python .claude/hooks/context_guard.py check
    python -m unittest discover -s tests -p test_context_guard.py -v

The always-triggered GitHub workflow named Sophon context integrity runs both. For PRs that change the charter, CLAUDE.md/AGENTS.md or a protocol/results/decision report under `prototype/`, `experiments/` or `viability/`, CI also requires PROJECT_STATE.json to change in the same PR. (Normal implementation-only edits don't require a state change.)

Checks specifically prevent accidentally erasing the established inventory (including the earlier public-data reviewer, Publicodes kernel, E0–E5 harness and normative-layer skeleton), a component without `location`/`does_not_prove`, an `OTHER_PR` component whose code is actually present here (or a local one whose code is absent), a PR referenced but missing from `pr_graph`, rewriting the frozen V3 primary as a success, using a v1.1 charter with a v1.2 state, removing the native session hooks, or recording a new formal experiment result without updating the snapshot.

To make the status check truly **merge-blocking**, the repository owner must add its job name, sophon-context-integrity, as a required status check under GitHub Settings > Rules > Rulesets / branch protection for main. CI checks alone report failures but do not block merges without that repository setting.

## Expected maintenance

- After a real experiment or approved decision: amend PROJECT_STATE.json *in the same PR* and preserve the original evidence with links/commit identifiers. Do not silently reinterpret unmerged PRs as merged.
- When starting on an old branch: update/rebase/cherry-pick the native guard AND the authoritative v1.2 charter; until then that branch has its own older context. A failed version check is a signal to resolve the conflict, not an instruction to delete the guard.
- For Claude Code Mobile or Cloud: select the repo's branch containing this guard, use a **single-repository** cloud session. Trust/re-approve project hooks if asked. On a multi-repository Anthropic cloud session, Claude Code currently does **not** load hooks from each repo's shared project settings.
- If a cloud environment blocks SEC or vendor sites, fix its network allowlist separately. The guard does not grant internet access or change sandbox policy.
- For ChatGPT: project-state retrieval through GitHub is still a deliberate assistant action. ChatGPT does not execute Claude Code hooks, so there is no claim of identical automatic enforcement there.

## Honest boundaries

- Automated adversarial, backward and library reviewers are already implemented on historical experimental branches. Their semantic agreement is not independently validated and cannot completely replace independent human spot checking. Use them first for triage and focus the manual work on high-risk cases and a blinded agreement sample.
- Snapshot recency is checked against committed content, *not live PR updates*: GitHub access may be blocked in the cloud. Refresh the state from the actual current PR heads before major decisions.
- Changes here do not merge PR #15, #17 or #18. If the native-context PR (based on charter #15's head) is merged into main, PR #15's content is already included and #15 should be closed as superseded, not merged again.

## Engineering modus operandi

The versioned [ENGINEERING_WORKFLOW.md](../ENGINEERING_WORKFLOW.md) is a standing engineering agreement, distinct from the product charter. The owner defines problems and constraints, and ChatGPT/Claude Code own independent technical judgments and one observable increment at a time. CLAUDE.md and AGENTS.md reference it. The native hook injects a concise reminder at each prompt and CI checks that the agreement exists and stays linked. The effectiveness of this behavior must be tested with a fresh agent session; static CI cannot prove an agent will act independently.

The GitHub file is the shared reference across sessions. ChatGPT conversations do not automatically execute Claude Code hooks: project-specific ChatGPT instructions should point here, and an assistant making a material Sophon recommendation must retrieve current repository state, workflow and evidence first.
