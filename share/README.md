# Share Folder — Inter-Agent Communication Bus

The `share/` folder is the **only** channel sub-agents use to talk to each other. There is no direct agent-to-agent chat. Every artifact produced by an agent is a file here.

## Layout

```
share/
├── handoffs/
│   └── 00_user_task.md          ← the original user task, captured by master at Phase 0
├── notes/
│   ├── 01_research_<task-id>.md           ← research sub-agent output
│   ├── 02_plan_high_<task-id>.md          ← planning sub-agent: high-level plan
│   ├── 02_plan_phases_<task-id>.md        ← planning sub-agent: phased plan
│   ├── 03_coder_summary_<task-id>_<phase>.md   ← coder sub-agent: work summary
│   └── 99_decisions.md                     ← append-only log of locked decisions
├── design/                     ← v0.9.0+: am-design's tree-structured output
│   └── <task-id>/
│       ├── 00_brief.md                  ← 7-question discovery answers
│       ├── 01_research/                 ← optional, when RESEARCH mode is used
│       ├── 02_brand/                    ← optional, BRAND mode
│       ├── 03_system/                   ← optional, SYSTEMIZE mode (design tokens)
│       ├── 04_mockups/                  ← optional, MOCK / PROTOTYPE mode
│       ├── 05_audit/                    ← optional, AUDIT / EVALUATE mode
│       ├── 06_copy/                     ← optional, WRITE mode (microcopy)
│       ├── 07_primitives/               ← optional, ILLUSTRATE mode (icons)
│       ├── 08_translations/             ← optional, TRANSLATE mode (locale)
│       └── 99_handoff.md                ← always — declares the next consumer + ships only the artifacts they need
└── reports/
    └── 04_review_<task-id>_<phase>.md     ← review sub-agent: per-task verdicts
```

## Naming convention

- `<phase-prefix><step>_<doc-type>_<task-id>[_<phase>].md`
- Phase prefixes are stable: `00_` ingest, `01_` research, `02_` planning, `03_` build, `04_` review, `99_` decisions.
- Task id format: `T-YYYY-MM-DD-NNN` where NNN is a daily counter.
- Phase suffix is the phase label from the plan (e.g. `Phase_1`, `P1`).

## Who reads / writes what

| Path | Written by | Read by |
|---|---|---|
| `handoffs/00_user_task.md` | master (Phase 0) | all agents |
| `notes/01_research_*.md` | research (canonical) or research-per-angle (parallel mode) | master, planning |
| `notes/01_research_*_angle-*.md` | research (parallel mode only) | master (for merge) |
| `notes/02_plan_high_*.md` | planning | master, user |
| `notes/02_plan_phases_*.md` | planning | master, coder, review |
| `notes/03_coder_summary_*.md` | coder | master, review |
| `design/<task-id>/00_brief.md` | am-design (v0.9.0+) | master, am-coder (Phase 3 reference) |
| `design/<task-id>/<mode>-files>` | am-design (v0.9.0+) | per the audience declared in `99_handoff.md` |
| `design/<task-id>/99_handoff.md` | am-design (v0.9.0+) | master, am-coder (next consumer) |
| `reports/04_review_*.md` | review | master (and the user, on demand) |
| `notes/99_decisions.md` | any agent (append) | all agents |

## Handoff protocol

1. The master writes `handoffs/00_user_task.md` at Phase 0. Every other artifact references the task id from this file.
2. Each phase's output file is **the canonical handoff** to the next phase. The master copies the file path into the task tracker.
3. When a phase loops back (e.g. review → coder), the master writes a short note in `notes/` with a name like `notes/feedback_review_to_coder_<task-id>_<phase>.md` so the coder has a single, named input.

## Parallel research aggregation

When the master runs research in parallel (see master `SKILL.md` → `## Parallel research mode`), the file layout differs:

- Per-angle files: `share/notes/01_research_<task-id>_angle-<name>.md` (one per parallel call).
- Merge step: the master (or a single follow-up research call) merges all per-angle files into the canonical `share/notes/01_research_<task-id>.md`, with a `## Sources` section listing each angle file at the top.

The canonical `01_research_<task-id>.md` is what Phase 2 (planning) reads. Per-angle files stay in place — never deleted — for traceability.

## Decisions log

`notes/99_decisions.md` is **append-only**. When any agent makes a locked decision (chose library X, rejected approach Y, accepted a tradeoff), append:

```markdown
## YYYY-MM-DD HH:MM — <agent>
**Decision:** <one sentence>
**Why:** <one paragraph>
**Tradeoff:** <what we gave up>
**Refs:** `research_doc/decisions/<topic>.md`, `share/notes/02_plan_high_<task-id>.md`
```

Never edit or delete past entries.

## Conflict resolution

If two files disagree:
- The more recent file wins for active work.
- The older one stays in place — never deleted — and a note is added to `99_decisions.md` explaining the supersession.
- The task tracker (`tasks/<task-id>.md`) is the source of truth for "what is currently in scope."

## What never goes in `share/`

- Source code (lives in the actual project repo).
- Build artifacts.
- Secrets / API keys.
- Scratch / draft files. Use a sub-agent's own `notes/` for scratch.
