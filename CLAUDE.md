# CLAUDE.md

# agents_manager — Multi-Agent Task Orchestration

This repository implements a multi-agent task pipeline built on OpenCode's agent system.

## Auto-routing

When the user provides a task that requires multiple steps (research → plan → build → review), spawn the **master** agent via the task tool:

```
task(subagent_type="master", prompt="<the user's task>")
```

The master handles everything: writing the task capture, calling specialists, enforcing gates, escalating to the user when needed.

For single-step work (a quick file edit, a one-off question), do it directly — no need to invoke the master.

**Soft-wall architecture (v0.5.0+):** all 10 agents have `permission: "allow"`. Walls are soft — enforced by each agent reading its SKILL.md boundaries + the inline prompt's Can/Can't list, not by OpenCode's permission layer.

**v0.9.0:** `am-design` (12-mode design specialist) added. Strict separation: am-design never writes `src/**`; reference implementations are am-coder's job.

## Tool usage efficiency (v0.5.1+)

This applies to **this** LLM (Claude Code / OpenCode session) when operating in this repo, not just to the 5 agents.

**Batch parallel edits when independent.** Issue all edits in a single message instead of one per turn. Sequence only when later edits depend on earlier (line shifts, shared context).

**Batch parallel reads when known.** When you know which files you need (and they fit in context), issue all reads in one message. Discovery (grep/glob) goes in its own message, then reads in a follow-up batch.

**Read once, edit many.** The combined pattern is two messages (batch reads, then batch edits), not N messages.

**Verify oldString uniqueness across a batch** before issuing it. Edits within one message land in some order — collisions fail silently.

**Verify once after the batch**, not mid-batch.

## Available agents

Defined in `opencode.jsonc` with soft walls (v0.5.0+). Each agent has `permission: "allow"` and enforces its boundaries via the SKILL.md "Boundaries" prose + the inline prompt's Can/Can't list. The "Owns" column below shows the primary output destination; in v0.5.0+ any agent can technically read/write anything, but the convention is to write only to the listed paths unless coordination requires more.

| Agent | Type | Purpose | Owns |
|---|---|---|---|
| `master` | agent | Orchestrates the pipeline; does not implement | `share/handoffs/`, `share/notes/99_decisions.md`, `tasks/` |
| `am-research` | agent | Brainstorm, doubt, analyze, investigate | `share/notes/01_research_*.md` |
| `am-planning` | agent | Turn research into a phased plan + task list | `share/notes/02_plan_*.md`, `tasks/<id>.md` rows |
| `am-design` (v0.9.0+) | agent | Visual / UX / brand / mockup / audit — never `src/**` | `share/design/<task-id>/**` |
| `am-assets` (v0.9.0+) | agent | Asset gatekeeper — visual-template manifests (Phase 3a) | `assets/MANIFEST.json`, `share/notes/03a_assets_*.md` |
| `am-coder` | agent | Implement assigned tasks | source code, `share/notes/03_coder_summary_*.md` |
| `am-review` | agent | Verify coder work, produce per-task verdicts | `share/reports/04_review_*.md` |
| `am-investigate` (v0.18.0+) | agent | Root-cause bug investigation; iron law: no fixes without root cause | `share/notes/04_investigate_*.md` |
| `am-ship` (v0.18.0+) | agent | Release: VERSION bump + CHANGELOG block + tag + push (idempotent) | `share/notes/05_ship_*.md`, `agents_manager/CHANGELOG.md` |
| `am-health` (v0.18.0+) | agent | Code-quality dashboard (frontmatter + py_compile + shellcheck); report only | `share/health/<date>.json` |

Walls are soft in v0.5.0+. Each agent's `SKILL.md` declares its boundaries as a prose contract; the LLM is expected to honor them. Full output-path table in `AGENTS.md` § Per-agent output paths.

## Project structure

```
agents_manager/        — controller: 1 master + 9 specialists (research, planning, design, assets, coder, review, investigate, ship, health), each with SKILL.md + rules.md
share/                 — inter-agent communication bus (handoffs, notes, reports, design/, messages/)
books/                 — book-gen output root, one folder per book (see AGENTS.md § Book-gen mode)
book_workflow/         — book-gen upstream spec (read-only reference for the orchestrator skill)
tasks/                 — canonical task tracker (one .md per task id)
research_doc/          — long-term research notes and decision records
opencode.jsonc         — agent definitions + permissions
CLAUDE.md              — this file
agents_manager/memory/ — v0.13.0+ cross-session memory (global + projects) — see [Memory](#memory) section below
```

## Key conventions

- The master NEVER codes, plans, or reviews directly. It routes to specialists.
- Specialists NEVER spawn other specialists. Only the master orchestrates.
- All inter-agent communication goes through files in `share/`. No out-of-band chat.
- Task id format: `T-YYYY-MM-DD-NNN`. One task file per id in `tasks/`.
- Review reports are brutally honest. False PASS ships bugs; false FAIL just costs a fix loop.
- Sub-agent `SKILL.md` and `rules.md` files are reference docs read on agent startup. They contain the full role definition, output templates, and standing rules.
- **The master runs a 5-question preflight before dispatching any specialist** (deliverable / why-needed / independence / tools / evidence-closure). Sub-agent SKILL.md see this internally; the user is expected to wait for the dispatch or the BLOCKED signal — not prompt in between. (v0.6.0+ G6 — multi-agent preflight is now user-visible.)

## Don't do

- Do NOT edit files inside `agents_manager/` unless explicitly redesigning the controller.
- Do NOT spawn specialists from a specialist. Only the master orchestrates.
- Do NOT skip the review phase because "it looks fine."
- Do NOT accept the first review report without reading it.

## Memory

Cross-session memory lives in three scopes, read in this order on re-entry:

1. **Global** — `agents_manager/memory/global/` — cross-project insights
2. **Project** — `agents_manager/memory/projects/<slug>/` — active project memory (slug = `agents_manager/.active-project` if present, else `basename $(pwd)`)
3. **Role** — `agents_manager/<role>/notes/{semantic,episodic}/` — per-specialist memory

Master writes global + project; specialists write role. All entries follow the schema + lifecycle in [`agents_manager/memory/README.md`](agents_manager/memory/README.md). Validator: `bash scripts/validate-memory.sh`.

## See also

- `agents_manager/SKILL.md` — full master orchestration protocol
- `agents_manager/README.md` — pipeline overview
- `agents_manager/CHANGELOG.md` — system evolution history
- `AGENTS.md` — repo-local instruction file (high-signal facts only)
