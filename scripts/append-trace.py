#!/usr/bin/env python3
"""Append a JSONL entry to share/notes/00_trace_<task-id>.jsonl.

v0.17.0+ audit trail for the agents_manager pipeline. Specialists and master
use this to write structured trace entries. The trace is greppable for
post-hoc debugging (anomaly detection, fix-loop analysis, dispatch audit).

Schema:
  {ts, task_id, agent, phase, action, files_touched[], verdict, notes}

Enums:
  agent  in master | am-research | am-planning | am-design |
         am-assets | am-coder | am-review
  action in start | complete | dispatch | anomaly | fix-loop
  verdict in None | PASS | WARN | FAIL  (am-review + complete only)

Usage:
  python3 scripts/append-trace.py --task-id T-2026-07-14-001 \\
      --agent am-research --phase 1 --action start \\
      --notes "researching auth flows"
  python3 scripts/append-trace.py --task-id T-2026-07-14-001 \\
      --agent am-review --phase 4 --action complete \\
      --verdict PASS --notes "all assigned tasks pass"
  python3 scripts/append-trace.py --task-id T-2026-07-14-001 \\
      --agent am-coder --phase 3 --action anomaly \\
      --files-touched src/auth/login.ts \\
      --notes "command suggested by share/notes/02_plan_high.md, not by user task"

See docs/TRACE.md for the full schema and query examples.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

ALLOWED_AGENTS = [
    "master", "am-research", "am-planning", "am-design",
    "am-assets", "am-coder", "am-review",
]
ALLOWED_ACTIONS = ["start", "complete", "dispatch", "anomaly", "fix-loop"]
ALLOWED_VERDICTS = [None, "PASS", "WARN", "FAIL"]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--task-id", required=True, help="T-YYYY-MM-DD-NNN")
    p.add_argument("--agent", required=True, choices=ALLOWED_AGENTS)
    p.add_argument("--phase", required=True, type=int,
                   help="1=research, 2=planning, 3=build, 3a=assets, 4=review, 0=master preflight")
    p.add_argument("--action", required=True, choices=ALLOWED_ACTIONS)
    p.add_argument("--files-touched", nargs="*", default=[],
                   help="space-separated list of paths touched in this action")
    p.add_argument("--verdict", default=None, choices=["PASS", "WARN", "FAIL"],
                   help="only for am-review + action=complete")
    p.add_argument("--notes", default="", help="one-line human context (not the full report)")
    p.add_argument("--out-dir", default="share/notes",
                   help="directory holding the 00_trace_*.jsonl files (default: share/notes)")
    args = p.parse_args()

    # ponytail: don't enforce verdict-only-on-review here. The calling agent
    # knows the rule; the script stays a dumb appender.
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "task_id": args.task_id,
        "agent": args.agent,
        "phase": args.phase,
        "action": args.action,
        "files_touched": args.files_touched,
        "verdict": args.verdict,
        "notes": args.notes,
    }
    out_path = os.path.join(args.out_dir, f"00_trace_{args.task_id}.jsonl")
    os.makedirs(args.out_dir, exist_ok=True)
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"wrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
