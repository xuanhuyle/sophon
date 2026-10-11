#!/usr/bin/env bash
# After a solver agent finishes: audit its transcript, record cost, and note the agent id in the run directory.
#   src/collect_run.sh ARM TASK AGENT_ID RUNS_ROOT
set -euo pipefail
arm="$1"; task="$2"; agent="$3"; runs="$4"
here="$(cd "$(dirname "$0")" && pwd)"
stage="$runs/$arm/$task"
transcript="/root/.claude/projects/-home-user-sophon/980382c3-789d-515f-926e-c8bdd3dd6b4b/subagents/agent-$agent.jsonl"
[ -f "$transcript" ] || { echo "transcript not found: $transcript" >&2; exit 1; }
python3 -B "$here/audit_transcripts.py" --transcript "$transcript" --stage "$stage" --out "$stage/AUDIT.json"
echo "$agent" > "$stage/AGENT_ID.txt"
if [ -f "$stage/output/answer.json" ]; then
  python3 -c "import json,sys; json.load(open('$stage/output/answer.json')); print('answer.json: valid JSON')" || echo "answer.json: INVALID JSON"
else
  echo "answer.json: MISSING"
fi
ls -la "$stage/output" "$stage/work" | head -30
