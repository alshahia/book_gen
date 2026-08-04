# CHANGELOG DRAFT — v0.13.0 (T-2026-07-03-002)

> **Standalone draft.** Phase 5 P5T3 (am-coder) pastes the body of `## v0.13.0` verbatim into `agents_manager/CHANGELOG.md` immediately after the `## v0.12.0 — ...` entry. The text below follows the v0.12.0 template (`agents_manager/CHANGELOG.md:5-67`) — same section headers, same tone, same level of rigor. Do not reformat. Do not trim. Do not change wording without surfacing to master.

---

## v0.13.0 — Three-scope memory system for agents_manager (2026-07-03)

Additive feature. **No controller behavior changes for non-substantive tasks**, **no existing specialist prompt rewrites**, no breaking changes to the v0.12.0 pipeline. Adds a three-scope memory tree (global + project + role) for specialist long-term memory, a single canonical schema source-of-truth, a write-on-exit dispatch contract, and a shipped frontmatter validator. Operators and per-task work fill the memory; the scaffold itself ships empty.

### What's new

- **Three-scope memory tree at `agents_manager/memory/`** — `global/` (cross-project facts, master-written), `projects/<slug>/` (per-project knowledge, master-written, default slug = `basename $PWD`, override via `agents_manager/.active-project`), and per-role `notes/{semantic,episodic}/` (specialist-written, owned by each specialist). Read order on re-entry: global → project → role, ≤200 lines per scope.
- **Single canonical schema source-of-truth at `agents_manager/memory/README.md`** — defines the frontmatter keys (`scope`, `topic`, `status`, `superseded_by`, `created`, `last_verified`), the lifecycle (append-only; supersession via `status: superseded` + `superseded_by:` link), the read/write protocol, the durable-insight criteria, the secrets-free rule, and the no-write-to-templates rule. Each per-role `notes/README.md` is a 2-line pointer (no duplication; prevents schema drift across 7 specialists).
- **Master's re-entry reads from 3 sources** — (a) `agents_manager/memory/global/`, (b) `agents_manager/memory/projects/<slug>/`, (c) `share/notes/99_progress_<task-id>.md`. Same 200-line cap per source. Master's own "role-scope" memory collapses into `memory/global/` (master IS the orchestrator; its accumulated lessons are inherently cross-project).
- **Dispatch contract line** — every specialist return summary gains a `Memory written: <path>` (or `No memory write: <reason>`) line. Master only gates on this for **substantive** dispatches (those that hit `tasks/<id>.md` rows); trivial status checks may use `No memory write: trivial`. Durability guardrail: write only if (a) a different agent in 3 months benefits AND (b) NOT derivable from coder summary / source AND (c) you spent >30s or it contradicted prior expectation. Per-entry size cap: ≤20 lines.
- **`scripts/validate-memory.sh` SHIPS in v0.13.0 (REQUIRED)** — ~50 LOC bash, executable, stdlib-only. Walks `agents_manager/memory/{global,projects}/` and `agents_manager/<role>/notes/{semantic,episodic}/`. Checks: frontmatter `--- ... ---` block closes; required keys present (`scope`, `topic`, `status`, `created`, `last_verified`); `scope ∈ {global, project, role}`; `status ∈ {active, superseded}`; `created` and `last_verified` parse as YYYY-MM-DD; when `status: superseded`, `superseded_by:` is present and resolves to a file that exists. Exit codes: 0 = no issues; 1 = at least one issue.
- **90-day sweep at Phase 5 close** — master sweeps memory entries with `last_verified` older than 90 days; flags them in `share/notes/04_warns_register_<task-id>.md` (WARN register); does NOT auto-delete. The sweep runs at master's Phase 5 (next-steps, opt-in via `phase_5_enabled`) when enabled; otherwise at Phase 4 close as part of `## Completion`.
- **20 files touched total** — 17 new + 9 modified (counted via the canonical delivery table below).

### Why

Before v0.13.0, every agent started each task with empty context: no cross-session memory, no project-state retention, no per-role expertise accumulation. Specialists had to rediscover repo conventions, retry already-known gotchas, and re-litigate decisions settled in prior tasks. The existing `notes/{episodic,semantic}/` shape was *declared* in every specialist SKILL.md (e.g., `agents_manager/research/SKILL.md:22-31`) but most folders were physically empty — there was no protocol for reading or writing them, and no validator to enforce schema. v0.13.0:

1. Materializes the existing-but-empty per-role scaffold under a single canonical schema (no new conventions invented — the shape was already declared).
2. Adds two master-managed scopes (`global/` + `projects/<slug>/`) so cross-task and per-project knowledge has a structural home without polluting per-role expertise.
3. Decouples the read protocol (read-on-entry, ≤200 lines/scope) from the write protocol (write-on-exit, 3-question "durable insight" test, ≤20 lines/entry) so trivial status-check dispatches don't pollute memory.
4. Ships a validator as a release blocker for v0.13.0 (not optional) so broken `superseded_by` links get caught mechanically rather than misleading readers.
5. Documents the protocol in 7 SKILL.md updates — 6 specialists + master — so every agent reads the same contract.

### Scope limits

- **No content backfill.** The scaffold ships empty; operators and the first task on each clone write memory as it earns its keep. Worked examples live in fenced code blocks in the canonical README; no `.md` files in `global/` or `projects/` ship with v0.13.0.
- **Co-exist migration stance.** Scaffold is purely additive — it does not move, rename, or delete any existing file. Power users with existing content in `agents_manager/<role>/notes/` are unaffected; their files stay put. The per-role READMEs are **replaced** (research/planning/coder/review) from a verbose 30-line schema-duplicate to a 2-line canonical pointer, enforcing the "no duplication" discipline on day one. The assets specialist's `agents_manager/assets/notes/README.md` is a NEW file documenting BOTH the new tree and the existing `branch-decisions.md` (which has a different append-only-by-task lifecycle and is preserved unchanged).
- **Master's SKILL.md edit goes through am-coder dispatch.** Per `agents_manager/SKILL.md:496` ("Editing `agents_manager/SKILL.md` during pipeline execution ... do not silently rewrite the protocol that defines the pipeline"). Master does not self-edit. This was surfaced at Phase 2 confirmation for explicit user OK before Phase 5 dispatch (T-2026-07-03-001 precedent).
- **No `opencode.jsonc` changes.** The locked design enforces the memory protocol via SKILL.md + dispatch contract, not via a new agent. One fewer wall conflict; matches v0.12.0's surgical-edit ethos.
- **No changes to the controller fence zone.** The 11 files modified + 19 untracked by v0.12.x follow-ups (`git status --short` at task start) are NOT touched by any v0.13.0 phase. A new `agents_manager/.gitignore` (1 line: `.active-project`) is created to scope the project-slug override file locally; the root `.gitignore` is in the fence zone and is NOT modified.
- **No auto-summarization, no auto-pruning.** Deferred to v0.14.x. The 90-day sweep is a manual flag-and-review mechanic, not an automated deletion.
- **No memory search/indexing.** File-based grep is the v1 search; the canonical README documents the keyword hints.
- **All 7 agents share the same 200-lines-per-scope budget** for v0.13.0. Per-agent context tuning requires per-agent model selection, which OpenCode does not currently support (deferred).
- **Token cost on re-entry** is bounded: empty scaffold = 0 cost; 90-day sweep keeps the budget bounded as content grows. v0.13.0 accepts ~2k tokens per dispatch on memory alone as the cost of the value delivered. Revisit at v0.15.x if metrics show re-entry memory growing >5% of total context.

### Read protocol (specialist, on re-entry)

1. `agents_manager/memory/global/*.md` — ≤200 lines; read in date order (newest first).
2. `agents_manager/memory/projects/<active-slug>/*.md` — ≤200 lines; same order.
3. `agents_manager/<this-role>/notes/semantic/*.md` — curated insights, ≤200 lines; read every file or skim the table of contents.
4. `agents_manager/<this-role>/notes/episodic/<task-id>.md` — past notes on the same task id; skim for continuity.

If a scope exceeds 200 lines, grep by `topic:` keyword first, then read up to 200 lines of matches.

### Write protocol (specialist, on exit)

Append to one of:
- `agents_manager/memory/global/<topic>.md` — for cross-project facts only (create new file; entry ≤20 lines).
- `agents_manager/memory/projects/<active-slug>/<topic>.md` — for per-project knowledge (create new file; entry ≤20 lines).
- `agents_manager/<this-role>/notes/{semantic,episodic}/<topic>.md` — for role-specific expertise.

Mandatory filter (skip if ANY criterion fails):
- (a) Would a different agent (or me, in 3 months) benefit from knowing this on re-entry? (Yes → write.)
- (b) Is it derivable from `share/notes/03_coder_summary_*.md` or the source code? (Yes → don't write; cite the source instead.)
- (c) Did you spend >30 seconds figuring it out, or did it contradict your prior expectation? (Yes → write.)

Hard rules:
- ≤20 lines per entry.
- Must NEVER reference `share/notes/02_secrets_*` paths/values. Reference the task id instead.
- Must NOT write into `templates/<name>/memory/` — that's the template author's lane.
- When superseding an old entry, set `status: superseded` + `superseded_by: <new-entry-path>` on the OLD file; do not delete it.

### Files touched

| File | Status |
|---|---|
| `agents_manager/memory/README.md` | **NEW** — canonical schema source-of-truth (~180 lines) |
| `agents_manager/memory/.gitignore` | **NEW** — nested scope `**/*.md` + `!**/.gitkeep` |
| `agents_manager/memory/global/.gitkeep` | **NEW** — empty-scope placeholder |
| `agents_manager/memory/projects/.gitkeep` | **NEW** — empty-scope placeholder |
| `agents_manager/.gitignore` | **NEW** — 1 line: `.active-project` |
| `agents_manager/research/notes/{semantic,episodic}/.gitkeep` | **NEW** ×2 |
| `agents_manager/planning/notes/{semantic,episodic}/.gitkeep` | **NEW** ×2 |
| `agents_manager/coder/notes/{semantic,episodic}/.gitkeep` | **NEW** ×2 |
| `agents_manager/review/notes/{semantic,episodic}/.gitkeep` | **NEW** ×2 |
| `agents_manager/assets/notes/{semantic,episodic}/.gitkeep` | **NEW** ×2 |
| `agents_manager/research/notes/README.md` | **modified** — replaced verbose 30 lines with 2-line canonical pointer |
| `agents_manager/planning/notes/README.md` | **modified** — same |
| `agents_manager/coder/notes/README.md` | **modified** — same |
| `agents_manager/review/notes/README.md` | **modified** — same |
| `agents_manager/assets/notes/README.md` | **NEW** — documents both the new tree and the existing `branch-decisions.md` |
| `scripts/validate-memory.sh` | **NEW** — ~50 LOC bash, executable, stdlib-only |
| `agents_manager/SKILL.md` (master) | **modified** — appended `## Memory protocol (v0.13.0+)` section after `## Templates (v0.9.0+)`. Subsections: project-slug detection; 3-source master's re-entry; dispatch contract line; 90-day sweep hook. ~60 lines added. Edited via am-coder dispatch (deliberate maintenance task — T-2026-07-03-001 precedent). |
| `agents_manager/research/SKILL.md` | **modified** — appended `## On re-entry` + `## On exit` sections. ~25 lines added. (Same applies to all 5 specialists below.) |
| `agents_manager/planning/SKILL.md` | **modified** — same |
| `agents_manager/design/SKILL.md` | **modified** — same (design's `notes/{semantic,episodic}/` folders already existed; only the protocol is new) |
| `agents_manager/coder/SKILL.md` | **modified** — same |
| `agents_manager/review/SKILL.md` | **modified** — same |
| `agents_manager/assets/SKILL.md` | **modified** — same protocol injection + 1 paragraph noting `branch-decisions.md`'s distinct lifecycle is preserved |
| `CLAUDE.md` | **modified** — added Memory row to project structure; new `## Memory` section with 3-scope summary + canonical pointer |
| `agents_manager/CHANGELOG.md` | **modified** — this entry |

### Tag / commit

**v0.13.0 — additive minor.** No breaking changes to existing 7 specialists. Owners on v0.12.0 can apply this PR without rewriting anything else. Existing dispatches to master, am-research, am-planning, am-design, am-coder, am-review, am-assets work unchanged for non-substantive tasks (the dispatch contract is additive; `No memory write: trivial` is the default for status checks). Substantive dispatches gain a single `Memory written:` return line; this is a contract addition, not a behavior change.

### Source attribution

- **Generator:** MiniMax-M3 via opencode CLI on Windows PowerShell 7+
- **Source date:** 2026-07-03
- **Source task id:** T-2026-07-03-002
- **Source project:** `agents-manager` (carry-over from v0.12.0)
- **Source discussion ids (master brainstorming session):** m0002–m0007 (analysis + 3-question design round)
- **Source research note:** `share/notes/01_research_T-2026-07-03-002.md` (16 risks classified, 6 clarifying questions answered)
- **Source plan files:** `share/notes/02_plan_high_T-2026-07-03-002.md`, `share/notes/02_plan_phases_T-2026-07-03-002.md`
- **Source CHANGELOG draft:** `share/notes/02_changelog_draft_T-2026-07-03-002.md` (this file)
- **Precedent:** `research_doc/README.md` (tier-1/2/3 + decisions/ + overrides/ + Status lifecycle) — the existing project's working memory scheme. `agents_manager/design/notes/{semantic,episodic}/.gitkeep` (the only specialist with actual folders before v0.13.0). T-2026-07-03-001 (cinematic-landing template + am-assets) for the soft-wall wall-crossing pattern.
- **Apply notes:** All 30 file ops are purely additive or mechanical text replacement; no schema/codepath behavioral change for non-memory dispatch paths. Migration is co-exist (no rename, no relocate). 90-day sweep begins at the first master's Phase 4 close after this lands, not retroactively.

### Review-driven fixes

_None yet — pending am-review verdict on Phase 5 chunk._
