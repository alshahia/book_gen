# AGENTS.md — context_gen

This repo IS the **agents-manager controller**: an OpenCode multi-agent orchestration system. 9 specialist agents are defined in `opencode.jsonc` (master + research + planning + design + assets + coder + review + investigate + ship + health). Walls are enforced by prose (v0.5.0+ soft walls — every agent has `permission: "allow"`), not by OpenCode's permission layer.

**Working in this repo:** when the task is to edit the controller itself (a specialist's `SKILL.md`, a release, a controller bug), edit directly — do NOT spawn the `master` agent. Master is for downstream projects that have installed the controller. The same hard rules still apply (no auto-commits, no skipping review, no editing other specialists' `SKILL.md` unless it's a deliberate controller redesign).

## Pipeline (default shape — v0.16.0+ adaptive)

```
master -> am-research -> am-planning -> [am-assets if visual template] -> am-design + am-coder (parallel) -> am-review
                                                            |                            |
                                                            v                            v
                                                  [am-investigate]  <--- recommended by am-review for CRITICAL/HIGH
                                                            |
                                                            v
                                                       am-coder (fix)
                                                            |
                                                            v
                                                       am-review (re-validate)
                                                            |
                                                            v
                                                       am-ship (release)
                                                       am-health (score)
```

- **master** orchestrates ONLY. Never codes, plans, designs, or reviews directly.
- **Specialists never spawn other specialists.** Only master orchestrates.
- All inter-agent communication goes through files in `share/`. No out-of-band chat.
- Review reports must be brutally honest. False PASS ships bugs; false FAIL just costs a fix loop.
- Master runs a 5-question preflight before dispatching any specialist.
- `am-assets` is dispatched at **Phase 3a** (between Planning and Build) only when the task uses a visual template that declares assets in its frontmatter AND no `assets/MANIFEST.json` exists yet. v0.16.0+ allows `am-design` and `am-coder` to run in parallel.
- `am-investigate` is dispatched when am-review's report includes a `## Recommend am-investigate` block (CRITICAL/HIGH findings with unclear cause) OR when the user reports a bug directly.
- `am-ship` is dispatched at Phase 5 release when the user says "ship" / "release" / "tag". Runs validation + VERSION bump + CHANGELOG block + tag + push. Idempotent.
- `am-health` is dispatched on demand ("is this healthy?" / "run all checks") or at Phase 5 close when health tracking is enabled. Report-only — never fixes.
- `agents_manager/extract/` is a non-roster on-demand skill (loaded by any specialist for "extract this to a template" requests). It is **not** registered in `opencode.jsonc`.

## Auto-routing

- Multi-step work (research -> plan -> build -> review) -> spawn master via `task(subagent_type="master", prompt="...")`.
- Single-step work (quick edit, one-off question) -> do it directly. No master needed.
- Book intent ("write a book", "book about X", "draft a guide on Y") -> master loads `agents_manager/book-gen-orchestrator/SKILL.md` and drives the 7-phase pipeline. See **Book-gen mode** below.

## Book-gen mode (added 2026-07-30)

**Trigger:** user signals long-form multi-chapter output ("write a book", "book about X", "draft a guide on Y").

**Routing:** master loads `agents_manager/book-gen-orchestrator/SKILL.md` and drives the 7-phase pipeline (intake → skeleton → research → outline → style → writing-plan → per-chapter write → 3-pass review). The orchestrator reuses the existing 5 specialists (am-planning, am-research, am-design, am-coder, am-review) — **no new agents added to `opencode.jsonc`**. The orchestrator's dispatch prompts override the specialists' default soft-wall CAN-lists at runtime (e.g. am-research writes `books/<slug>/research-log.md`, not `share/notes/01_research_*.md`).

**Two new skill files, both non-roster** (loaded on demand via the skill tool, not dispatched as agents):
- `agents_manager/book-gen-orchestrator/SKILL.md` — phase routing + template pointers. Master loads this.
- `agents_manager/book-writer/SKILL.md` — prose-writing posture for am-coder during Phase 6. Master instructs am-coder to load it via the skill tool.
- `agents_manager/book-reviewer/SKILL.md` (v0.22.0+, translation-mode only) — two-pass review posture for am-review when the dispatch includes `books/<slug>/chapters/ch-NN.md` AND `source-map.md`. Master dispatches Pass 1 (accuracy vs. source) and Pass 2 (cross-chapter consistency) as **separate invocations** — never combined. When `source-map.md` is absent, am-review falls back to the standard 3-pass posture (dev / line / copy).

**Output root: `books/<slug>/`** — NOT `share/`. Books are the project's product; `share/` is reserved for inter-agent communication. Per-book files: `intake.md`, `skeleton.md`, `research-log.md`, `outline.md`, `style-guide.md`, `writing-plan.md`, `bible.md`, `ledger.md`, `decisions-log.md`, `source-map.md` (translation-mode only), `frozen-lines.json`, `.translate-progress.json` (translation-mode only), `chapters/ch-XX.md`.

**Upstream spec: `book_workflow/book-agents/`** (NOT in `agents_manager/`). Templates at `book_workflow/book-agents/templates/` (18 markdown + 1 JSON schema) + 6 sub-agent SKILL.md files. The orchestrator skill references these for canonical structure.

**Smoke-test reference: `books/daily-focus/`** — ch-01 reached `approved` (2,465 words), ch-02–05 stubbed `skipped`. Read this first to see what good book-gen output looks like before producing more. Two review reports: `share/reports/04_review_T-2026-07-30-001_dev-ch01.md` + `04_review_T-2026-07-30-001_lineedit-ch01.md`.

**User gates** (work pauses for confirmation): Phase 0 (intake fields — §10 translation-mode fields appear only when user signals translation intent), Phase 3 (outline contradictions + dependency graph; refuses to advance without populated `source-map.md` when §10 `Is translation? = yes`), Phase 4 (style-guide confirmation). Phase 5 has no checkpoint. Phase 7 review = **Branch A** (translation-mode: 2-pass `book-reviewer` accuracy + consistency) OR **Branch B** (native: 3-pass dev → line → copy-edit); copy-edit only when ALL chapters `approved` — skipped on partial runs.

**Publish-time strip:** `books/daily-focus/chapters/ch-01.md` lines 87-94 hold a self-critique HTML comment for orchestrator/reviewer handoff. Strip before any external publish.

## Hard rules

- **Do NOT commit unless explicitly asked.** Project convention; commits are user-driven.
- **Do NOT skip the review phase** because "it looks fine."
- **Do NOT accept the first review report without reading it.**
- **max_fix_loops = 3.** Cap on review -> fix -> re-review cycles; surface to user after.
- **Do NOT edit `agents_manager/<role>/SKILL.md`** unless explicitly redesigning the controller.
- **v0.9.0+**: `am-design` never writes `src/**`; reference implementations are `am-coder`'s job.
- **v0.22.0+**: Every agent must validate external module/library/framework/SDK/API usage with `chub` before writing code against it. Training data may be outdated or hallucinated; chub is canonical. Enforced by: (1) `bin/agents-manager` install installs `chub` by default and copies the `chub-gate` opencode plugin + `chub-validate` skill (project-local by default; `--chub-global` for `~/.config/opencode/`, for users without agents-manager), (2) the `chub-gate` plugin re-injects the chub reminder into context after every compaction so the rule survives mid-session memory loss, (3) specialist SKILL.md has a pre-write step requiring `chub get <id>` citation in the coder summary, (4) `am-review` checks for the citation and FAILs tasks with unvalidated imports. If chub isn't installed in the target project, install it (`npm install -g @aisuite/chub`) or surface to master. See master SKILL.md § Context-hub protocol for the full workflow.

## Per-agent output paths ("Owns" column)

| Agent | Primary output destination |
|---|---|
| master | `share/handoffs/`, `share/notes/99_decisions.md`, `tasks/` |
| am-research | `share/notes/01_research_*.md` |
| am-planning | `share/notes/02_plan_*.md`, `tasks/<id>.md` rows; v0.17.0+ also writes `share/notes/02_plan_review_*.md` for plan-mode review angles (plan-ceo / plan-eng / plan-design / plan-devex) |
| am-design (v0.9.0+) | `share/design/<task-id>/**` |
| am-assets (v0.9.0+, Phase 3a) | `assets/MANIFEST.json`, `share/notes/03a_assets_*.md`, `share/handoffs/03a_assets-to-coder-*.md` |
| am-coder | source code, `share/notes/03_coder_summary_*.md` |
| am-review | `share/reports/04_review_*.md`; v0.18.0+ also writes `## Recommend am-investigate` blocks when findings need root-cause work |
| am-investigate (v0.18.0+) | `share/notes/04_investigate_*.md` |
| am-ship (v0.18.0+) | `share/notes/05_ship_*.md`; edits `VERSION` + `agents_manager/CHANGELOG.md` |
| am-health (v0.18.0+) | `share/health/<date>.json` + `share/notes/05_health_*.md` |

In v0.5.0+ any agent can technically read/write anywhere (`permission: "allow"`); the convention is to write only to the listed paths unless coordination requires more.

## Tool surface (v0.19.0+/v0.20.0+)

Five tools (four MCP servers + the chub CLI) are wired into specialists as documented in their SKILL.md `allowed-tools`:

| Tool | Type | Used by | Purpose |
|---|---|---|---|
| `browsermcp` | MCP | am-research (v0.18.0+) | Live-site research via headless browser |
| `codebase-memory` | MCP | am-research, am-review, am-investigate, am-coder (v0.19.0+) | Graph-based code intelligence: symbol search, call-path tracing, complexity audit, blast-radius analysis |
| `github` | MCP | am-ship (v0.19.0+) | PR creation + release verification (gh CLI retained as fallback) |
| `testsprite` | MCP | am-coder (run), am-review (cite) (v0.19.0+, optional) | Post-build UI smoke tests for downstream projects with a running UI |
| `chub` (context-hub) | CLI | all 10 agents (v0.20.0+, MANDATORY) | Library/API/SDK doc fetcher; install on-demand via `npm install -g @aisuite/chub`. See master SKILL.md § Context-hub protocol. |

MCPs are enabled at the host level (parent `opencode.json`), not per-agent — so availability is environment-dependent. Each SKILL.md documents the fallback (grep/glob/gh) when the MCP isn't installed in the target project. The chub CLI is invoked via Bash and installed on-demand by any agent when missing.

## Task tracking

- ID format: `T-YYYY-MM-DD-NNN`. One file per id in `tasks/`.
- Phase log + sub-task rows live in `tasks/<id>.md`.
- Each phase writes its own handoff/summary/report file (see "Owns" column above).

## Controller dispatchers (v0.11.0+)

Three install paths for putting agents-manager into a target project:

- `bin/agents-manager` (bash) — reads manifest via inline Python3
- `bin/agents-manager.ps1` (PowerShell) — reads manifest via `ConvertFrom-Json`
- `bin/agents-manager.py` (Python UX) — single dialect, stdlib only, recommended

All three accept `--global/--local/--both/--skip` on `skills add` (v0.11.0). Default scope = `both` (honors per-skill source).

## Standalone installer (downloads alone, runs anywhere)

`bin/standalone-installer/install.{py,sh,cmd}` + `README.md`. Downloads latest release from GitHub API, extracts to temp, runs bundled installer, cleans up. Stdlib only.

## Releases (tag-driven, fully automated)

1. Add a `## vX.Y.Z — <theme> (YYYY-MM-DD)` block to `agents_manager/CHANGELOG.md` (newest on top) **before** tagging. The release workflow extracts this block as the GitHub Release notes; without it the release body is a placeholder.
2. `git tag -a vX.Y.Z -m "vX.Y.Z: <one-line>"` then `git push origin vX.Y.Z`. `release.yml` builds the ZIP from a fixed allowlist (`opencode.jsonc`, `CLAUDE.md`, `agents_manager`, `share`, `tasks`, `.agents/skills/mavis-team`, `bin`) and runs a 3-step gh-api dance (create→PATCH→upload) to dodge an HTTP 500 quirk on the initial POST when `name`/`body` are set.
3. Release appears in <2 min at `https://github.com/<owner>/agents-manager/releases/tag/vX.Y.Z`.

## Lint / verify

```bash
# Bash (file is CRLF on Windows working tree; convert first)
npx --yes shellcheck <(python3 -c "open('bin/agents-manager','rb').read().replace(b'\r\n',b'\n').decode().encode()")

# PowerShell
pwsh -NoProfile -Command "Invoke-ScriptAnalyzer -Path bin/agents-manager.ps1"

# Python
python3 -m py_compile bin/agents-manager.py bin/install.py bin/standalone-installer/install.py

# Frontmatter (controller files)
python3 scripts/validate-frontmatter.py
```

There are no tests for `bin/` scripts — only `scripts/validate-frontmatter.py`. CI runs on `ubuntu-latest` only, so `.cmd` scripts can't be CI-linted; use the manual smoke checklist in CHANGELOG / plan files instead.

## EOL

`.gitattributes` rules: `*.sh text eol=lf`, `*.ps1 text eol=crlf`, `*.cmd text eol=crlf`, `*.bat text eol=crlf`, `*.json/yaml/md text eol=lf`. Windows working tree may show CRLF due to `core.autocrlf=true`; git normalizes on commit.

## Reading order for a new session

1. `CLAUDE.md` — top-level orientation + auto-routing rule
2. `opencode.jsonc` — agent definitions
3. `agents_manager/SKILL.md` — master orchestration protocol
4. `agents_manager/<role>/SKILL.md` — for any specialist you dispatch
5. `agents_manager/CHANGELOG.md` — system evolution (read latest entry first)
6. `share/notes/02_plan_*.md` + `tasks/<id>.md` — current in-flight work
7. **Book-gen intent?** also read `agents_manager/book-gen-orchestrator/SKILL.md`, `agents_manager/book-writer/SKILL.md`, `agents_manager/book-reviewer/SKILL.md` (translation-mode only), `books/daily-focus/` (smoke-test reference), `book_workflow/book-agents/templates/`.

## Tool usage efficiency (v0.5.1+)

### Read workflow
- **Discovery first, read second.** When you don't know what files exist, use `glob` (by pattern) or `grep` (by content) to find them. Read in parallel only AFTER you know which files you need.
- **Batch parallel reads when files are known.** A folder analysis that surfaces N files to read → issue all N `read` calls in one message, not N messages.
- **Use `offset`/`limit` for large files** (>2000 lines). Reserve full reads for files you genuinely need in one piece.
- **Re-read or re-grep after edits.** Edits shift line numbers; the next edit's `oldString` may no longer match.

### Edit workflow
- **A `read` precedes every `edit` batch** (tool contract). Read once, then issue all edits in a single message.
- **Batch parallel `edit` calls** when independent. Sequence only when later edits depend on earlier (line shifts, shared mutating context).
- **Use `write` for full-file replacement** (new files, full rewrites). `edit` is for surgical changes only.
- **Verify `oldString` uniqueness across the batch** before issuing. Silent collisions are the #1 edit-batch failure mode.
- **Verify once after the batch completes**, not mid-batch.

### Other parallelism (when in doubt, batch)
- `bash`: multiple independent commands → one message with multiple tool calls.
- `glob` + `grep`: often worth batching together — pattern search + content search in one message.
- `task` (subagent dispatch): NOT batchable. Only `master` dispatches subagents per pipeline rule.