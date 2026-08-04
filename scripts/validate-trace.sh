#!/usr/bin/env bash
# Validate JSONL trace files under share/notes/00_trace_*.jsonl
# Exit 0 = clean, exit 1 = at least one issue.
# ponytail: stdlib only — uses python3 inline to avoid a jq dependency.
set -euo pipefail

python3 - <<'PY'
import json
import glob
import sys

REQUIRED = {"ts", "task_id", "agent", "phase", "action", "files_touched", "verdict", "notes"}
ALLOWED_AGENTS = {
    "master", "am-research", "am-planning", "am-design",
    "am-assets", "am-coder", "am-review",
}
ALLOWED_ACTIONS = {"start", "complete", "dispatch", "anomaly", "fix-loop"}
ALLOWED_VERDICTS = {None, "PASS", "WARN", "FAIL"}

errors = 0
files = sorted(glob.glob("share/notes/00_trace_*.jsonl"))
if not files:
    print("no trace files found", file=sys.stderr)
    sys.exit(0)  # no files is not an error — they only exist after a task runs

for path in files:
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                e = json.loads(stripped)
            except json.JSONDecodeError as ex:
                print(f"{path}:{i}: invalid JSON — {ex}")
                errors += 1
                continue
            missing = REQUIRED - set(e.keys())
            if missing:
                print(f"{path}:{i}: missing fields {sorted(missing)}")
                errors += 1
                continue
            if e["agent"] not in ALLOWED_AGENTS:
                print(f"{path}:{i}: bad agent {e['agent']!r}")
                errors += 1
            if e["action"] not in ALLOWED_ACTIONS:
                print(f"{path}:{i}: bad action {e['action']!r}")
                errors += 1
            if e["verdict"] not in ALLOWED_VERDICTS:
                print(f"{path}:{i}: bad verdict {e['verdict']!r}")
                errors += 1
            if not isinstance(e["files_touched"], list):
                print(f"{path}:{i}: files_touched must be array")
                errors += 1

if errors:
    print(f"\n{errors} issue(s) found", file=sys.stderr)
    sys.exit(1)
print(f"OK — {len(files)} trace file(s) clean")
PY
