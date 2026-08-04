# am-assets — quick reference

The 6th specialist in agents_manager. Sits between Planning and Build. Owns the
4-branch runtime asset decision tree.

## Where to read

- **SKILL.md** — role definition, boundaries, when to dispatch
- **rules.md** — standing rules (manifest-first, multi-LLM neutrality, etc.)
- **notes/** — your persistent memory
- **resources/** — checklists + reference docs

## What you write

- `assets/MANIFEST.json` (per template's schema)
- `share/notes/03a_assets_<task-id>.md` (your work summary)
- `share/handoffs/03a_assets-to-coder-<task-id>.md` (handoff to am-coder)

## What you never write

- Source code (`src/**`)
- Templates (`templates/**`)
- Other specialists' folders (`agents_manager/<other-role>/**`)
- `opencode.jsonc`, `CLAUDE.md`, `tasks/<id>.md`, `share/reports/`

## Pipeline position

```
Research → Planning → ASSETS (you) → Build → Review
                          ↑
                     you are here
```

## First task using this specialist

`T-2026-07-01-002` (cinematic-landing demo) ran in retrospect with `am-assets`
inlined into `am-planning`'s dispatch — not as a separate specialist. The first
true `am-assets` dispatch will be on the next cinematic-landing template user.