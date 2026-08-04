# Agents Manager — System Overview

A multi-agent task pipeline where one **master agent** orchestrates four **specialist sub-agents** to take a user task from request to reviewed, shipped work.

The master agent does **not** implement, code, research, or review. It routes work, gates phases on user confirmation, and decides chunk sizes.

## The pipeline

```
USER TASK
   │
   ▼
[0] INGEST       ← master captures the task verbatim
   │
   ▼
[1] RESEARCH     ← am-research: analyze, doubt, brainstorm, investigate
   │              ↓ asks user clarifying questions if needed
   ▼
[2] PLANNING     ← am-planning: phased plan + task table
   │              ↓ master presents to user, waits for confirmation
   ▼
[3] BUILD        ← am-coder: implement assigned tasks, write summary
   │
   ▼
[4] REVIEW       ← am-review: per-task verdicts (PASS / WARN / FAIL)
   │
   ├── FAIL → loop to [3] with fix list
   ├── plan-change-needed → loop to [2]
   ├── research-gap → loop to [1]
   └── all PASS → DONE
```

## The five agents

Each agent is defined in `opencode.jsonc` with its own permission block. Walls are enforced by OpenCode's permission layer — not by prose.

| Agent | Type | What it does | What it does NOT do |
|---|---|---|---|
| **Master** | `master` | Routes work, gates on user confirmation, decides chunks, reads review reports, enforces programmatic gates and the `max_fix_loops = 3` cap, tracks metrics. | Implement, plan, code, review. |
| **Research** | `am-research` | Brainstorm, doubt, analyze the task. Surfaces unknowns. Asks clarifying questions when answers change the plan. Self-critiques before returning. | Propose a plan. Write code. |
| **Planning** | `am-planning` | Produces high-level plan + phased plan + task table + plan self-score. Self-critiques before returning. | Write code. Self-confirm. |
| **Coder** | `am-coder` | Implements an assigned chunk of tasks. Writes a work summary listing files changed. Self-critiques before returning. | Plan. Self-approve. Edit `agents_manager/**` (enforced by permission). |
| **Review** | `am-review` | Reads the code (not just the summary), runs documented tests/builds, writes per-task verdicts. Self-critiques before returning. | Fix code. Change the plan. Edit source files (enforced by permission). |

## Folder layout

```
agents_manager/                    ← controller (master + 4 specialist folders)
├── SKILL.md                       ← master orchestrator
├── README.md                      ← this file
│
├── research/                      ← am-research sub-agent
│   ├── SKILL.md
│   ├── rules.md
│   ├── notes/                     ← past research notes
│   └── resources/
│
├── planning/                      ← am-planning sub-agent
│   ├── SKILL.md
│   ├── rules.md
│   ├── notes/
│   └── resources/
│
├── coder/                         ← am-coder sub-agent
│   ├── SKILL.md
│   ├── rules.md
│   ├── notes/
│   └── resources/
│
└── review/                        ← am-review sub-agent
    ├── SKILL.md
    ├── rules.md
    ├── notes/
    └── resources/

share/                              ← inter-agent bus (project root)
├── handoffs/                       ← user task capture
├── notes/                          ← research, plans, coder summaries
└── reports/                        ← review verdicts

tasks/                              ← task tracker (project root, one .md per task)
```

Each sub-agent's folder is its persistent memory — past notes live there, and the agent reads them on re-invocation. Each agent's `notes/` is split into `episodic/` (per-task) and `semantic/` (curated cross-task insights).

## How the master invokes a specialist

The master spawns each specialist as a separate OpenCode agent via the task tool:

```
task(subagent_type="am-research",   prompt="<task id, user task, handoff path>")
task(subagent_type="am-planning",   prompt="<task id, research output path>")
task(subagent_type="am-coder",      prompt="<task id, phase id, assigned task ids>")
task(subagent_type="am-review",     prompt="<task id, phase id, coder summary path>")
```

Each specialist runs in its own context window with its own permission block (see `opencode.jsonc`). When it returns, the master copies its artifact path into `tasks/<task-id>.md` and advances to the next phase.

## Key conventions

- **Every artifact is a file in `share/`** — no out-of-band chat.
- **Tasks are tracked in `tasks/<task-id>.md`** with the canonical table schema and a `## Metrics` block (timestamps, loop counts, files touched).
- **Re-entries append, never overwrite** — history is preserved.
- **Honesty over flattery** — research says "I don't know," review says "FAIL," coder says "partial."
- **The user confirms the plan** before any code is written.
- **Every sub-agent self-critiques** before returning to the master (3-bullet block in every output template).
- **Each sub-agent runs documented tests** when validating a chunk. The reviewer re-runs them independently.
- **Max 3 fix-loops per chunk.** After that, the master escalates to the user instead of looping.
- **The master enforces programmatic gates** between phases — no agent output advances until its required sections exist.
- **Parallel research is opt-in.** Master may decompose big tasks into 2–3 parallel research angles and merge.

## Quick start (for the user)

1. Give the master a task.
2. The master writes `share/handoffs/00_user_task.md` and creates `tasks/<task-id>.md`.
3. Research runs. You may get clarifying questions. Answer them.
4. Planning runs. You see the plan. Confirm or request changes.
5. Coder runs in chunks. Each chunk ends with a summary.
6. Review runs after each chunk. You see verdicts.
7. Loop (fix → review) until clean, then the task is closed.

## Adding a new sub-agent

1. Create `agents_manager/<name>/` with `SKILL.md`, `rules.md`, `notes/`, `resources/`.
2. Add a row to the **sub-agents table** in `agents_manager/SKILL.md`.
3. Decide where in the pipeline it sits and document the gate.
4. Update this README's **five agents** table.
