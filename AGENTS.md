# AGENTS.md -- agents_manager controller

This repo IS the **agents-manager controller**: an OpenCode multi-agent orchestration system. The 10 agents (`master` + 9 specialists) are defined in `opencode.jsonc`. Soft walls since v0.5.0: every agent has `permission: "allow"`; boundaries are enforced by the per-agent `Boundaries` section in its own `SKILL.md`, not by OpenCode's permission layer.

> **Note:** README.md frames this repo as a "book-generation system". That's the book-kit *use case*. The repo itself is the controller. README.md is being reconciled in a follow-up.

**`book-kit/` is a separate shippable** (its own `VERSION`, `CHANGELOG.md`, and release flow). It installs agents-manager into downstream projects. Don't edit `book-kit/**` from a controller task; that's a different release.

## Working in the controller

When the task is to edit the controller itself (a specialist's `SKILL.md`, a release, a controller bug), **edit directly -- do NOT spawn the `master` agent**. `master` is for downstream projects that have installed the controller. The same hard rules still apply.

When the task is to do controller work in a downstream project that has the controller installed, dispatch `master` via `task(subagent_type="master", prompt="...")`. The master orchestrates; specialists never spawn other specialists.

## Directory layout (what's here)

| Path | What |
|---|---|
| `agents_manager/` | Controller: `master` + 9 specialists + non-roster skills (book-gen, book2media, book-writer, book-reviewer, extract, chub-gate, chub-validate). |
| `agents_manager/CHANGELOG.md` | Controller release notes (separate from book-kit). |
| `opencode.jsonc` | Agent definitions + per-agent prompts. Master has Boundaries section here too. |
| `book-kit/` | Separate shippable kit -- installs agents-manager into downstream projects. Has its own `VERSION` + `CHANGELOG.md`. |
| `books/` | Book-gen output root (`<slug>/chapters/ch-NN.md`). Smoke-test reference: `books/daily-focus/`. Sandbox: `books/daily-focus-smoke/`, `books/daily-focus-render/` (gitignored). |
| `books_from_other_projects/` | Style library + vision-OCR tools (29 archetypes, see `book_workflow/book-agents/templates/style-guide.md`). |
| `book_workflow/` | Book-gen upstream spec (templates + sub-agents). |
| `bin/` | Installer scripts (3 dialects: bash, PowerShell, Python). |
| `share/` | Inter-agent communication bus (notes, handoffs, reports, decisions). |
| `shares/` | TTS audio output (gitignored). |
| `tasks/` | Task tracker; one file per id `T-YYYY-MM-DD-NNN`. |
| `scripts/` | Repo-level utilities (e.g., `validate-frontmatter.py`). |
| `.agents/skills/mavis-team/` | mavis-team skill (used on explicit `/mavis-team` or `/team` invocation). In release.yml allowlist. |

Note: `master` is registered in `opencode.jsonc`, but its SKILL.md is at `agents_manager/SKILL.md` (controller root, not `agents_manager/master/SKILL.md` like specialists). Don't search for `agents_manager/master/SKILL.md` -- it doesn't exist.

## Hard rules

- **Do NOT commit unless explicitly asked.** Project convention; commits are user-driven.
- **Do NOT skip the review phase** because "it looks fine."
- **Do NOT accept the first review report without reading it.**
- **max_fix_loops = 3.** Cap on review -> fix -> re-review cycles; surface to user after.
- **Do NOT edit `agents_manager/<role>/SKILL.md`** unless explicitly redesigning the controller.
- **v0.9.0+**: `am-design` never writes `src/**`; reference implementations are `am-coder`'s job.
- **ASCII-only on newly written code and docs.** Use `--` not em-dash, `->` not arrow, `Section` not section symbol. Applies to SKILL.md edits, doc rewrites, AGENTS.md/CLAUDE.md updates.
- **v0.20.0+**: Every agent must validate external module/library/framework/SDK/API usage with `chub` before writing code against it. Training data may be outdated or hallucinated; chub is canonical. See `agents_manager/SKILL.md` Section Context-hub protocol for the mandatory workflow (search -> get -> use -> annotate -> feedback). Install: `npm install -g @aisuite/chub`.

## Pipeline (default shape -- v0.16.0+ adaptive)

`master` orchestrates only; it never codes, plans, designs, or reviews directly. Default shape:

```
master -> am-research -> am-planning -> [am-assets if visual template, Phase 3a]
                                    -> am-design + am-coder (parallel) -> am-review
                                                                          |
                                                                          v (CRITICAL/HIGH with unclear cause)
                                                                     am-investigate
                                                                          -> am-coder (fix) -> am-review (re-validate)
                                                                          -> am-ship (release) / am-health (score)
```

Adaptive mode (v0.16.0+): the pipeline is the **default shape**, not an absolute rule. Master triages by complexity (trivial / one-step / standard / complex) and dispatches accordingly. Re-dispatch, parallel, and out-of-phase work are normal.

`am-investigate` is dispatched when am-review's report includes a `## Recommend am-investigate` block (CRITICAL/HIGH with unclear cause) OR when the user reports a bug directly.
`am-ship` is dispatched at Phase 5 release when the user says "ship" / "release" / "tag". Idempotent.
`am-health` is dispatched on demand ("is this healthy?" / "run all checks") or at Phase 5 close. Report-only -- never fixes.
`agents_manager/extract/` is a non-roster on-demand skill (loaded by any specialist for "extract this to template" requests). Not registered in `opencode.jsonc`.

## Auto-routing

- **Multi-step work** (research -> plan -> build -> review) -> dispatch `master` via `task(subagent_type="master", prompt="...")`.
- **Single-step work** (quick edit, one-off question) -> do it directly. No `master` needed.
- **Book intent** ("write a book", "book about X", "draft a guide on Y") -> `master` loads `agents_manager/book-gen-orchestrator/SKILL.md` and drives the 7-phase pipeline. Output root: `books/<slug>/` (NOT `share/`).
- **Book2media intent** ("convert book to video", "make audiobook", "produce reels") -> `master` loads `agents_manager/book2media-orchestrator/SKILL.md` (added v1.3.0). Triggers Phase 9 of the book-gen pipeline after writing is done. Output root: `books/<slug>/exports/` + `shares/audio/<slug>/`.

## Per-agent output paths ("Owns" column)

| Agent | Primary output destination |
|---|---|
| `master` | `share/handoffs/`, `share/notes/99_decisions.md`, `tasks/<id>.md` rows |
| `am-research` | `share/notes/01_research_*.md` |
| `am-planning` | `share/notes/02_plan_*.md`, `share/notes/02_plan_review_*.md` (v0.17.0+), `tasks/<id>.md` rows |
| `am-design` (v0.9.0+) | `share/design/<task-id>/**` |
| `am-assets` (v0.9.0+, Phase 3a) | `assets/MANIFEST.json`, `share/notes/03a_assets_*.md`, `share/handoffs/03a_assets-to-coder-*.md` |
| `am-coder` | source code, `share/notes/03_coder_summary_*.md` |
| `am-review` | `share/reports/04_review_*.md`; writes `## Recommend am-investigate` block when needed (v0.18.0+) |
| `am-investigate` (v0.18.0+) | `share/notes/04_investigate_*.md` |
| `am-ship` (v0.18.0+) | `share/notes/05_ship_*.md`; edits `VERSION` + `agents_manager/CHANGELOG.md` |
| `am-health` (v0.18.0+) | `share/health/<date>.json` + `share/notes/05_health_*.md` |

Full CAN/CANNOT lists are in each agent's `agents_manager/<role>/SKILL.md` Boundaries section. Convention: write only to the listed paths unless coordination requires more.

## Non-roster skills (loaded on demand via the skill tool, NOT dispatched as agents)

| Skill | Path | Trigger |
|---|---|---|
| book-gen-orchestrator | `agents_manager/book-gen-orchestrator/SKILL.md` | book intent |
| book-writer | `agents_manager/book-writer/SKILL.md` | Phase 6 prose writing |
| book-reviewer (translation-mode only) | `agents_manager/book-reviewer/SKILL.md` | 2-pass review when `source-map.md` is present |
| book2media-orchestrator (v1.3.0+) | `agents_manager/book2media-orchestrator/SKILL.md` | book2media / Phase 9 intent |
| chub-gate | `agents_manager/chub-gate/SKILL.md` | OpenCode plugin (auto-installed by `bin/agents-manager`) |
| chub-validate | `agents_manager/chub-validate/SKILL.md` | cross-check chub citations in coder summaries |
| extract | `agents_manager/extract/SKILL.md` | "extract this to template" requests |

The book-gen and book2media orchestrators override the specialists' default soft-wall CAN-lists at runtime via the dispatch prompt (e.g. am-research writes `books/<slug>/research-log.md`, not `share/notes/01_research_*.md`).

## Task tracking

- ID format: `T-YYYY-MM-DD-NNN`. One file per id in `tasks/`.
- Phase log + sub-task rows live in `tasks/<id>.md`. Schema in `tasks/README.md`.
- Each phase writes its own handoff/summary/report file (see "Owns" column).

## Controller releases (tag-driven, fully automated)

1. Add a `## vX.Y.Z -- <theme> (YYYY-MM-DD)` block to `agents_manager/CHANGELOG.md` (newest on top) **before** tagging. `release.yml` extracts this block as the GitHub Release body; without it the release body is a placeholder.
2. `git tag -a vX.Y.Z -m "vX.Y.Z: <one-line>"` then `git push origin vX.Y.Z`. The workflow builds the ZIP from a fixed allowlist (`opencode.jsonc`, `CLAUDE.md`, `agents_manager`, `share`, `tasks`, `.agents/skills/mavis-team`, `bin`) and runs a 3-step gh-api dance (create -> PATCH -> upload) to dodge an HTTP 500 quirk on the initial POST when `name`/`body` are set.
3. Release appears in <2 min at `https://github.com/<owner>/agents-manager/releases/tag/vX.Y.Z`.

Full release checklist + HARD STOPS in `agents_manager/ship/SKILL.md`. Note: `book-kit/CHANGELOG.md` is the kit's release notes (separate release flow controlled by book-kit's `ship/SKILL.md`); do not mix them up.

## Lint / verify

```bash
python3 scripts/validate-frontmatter.py                        # controller SKILL.md frontmatter
python3 -m py_compile bin/agents-manager.py bin/install.py bin/standalone-installer/install.py
```

CI runs on `ubuntu-latest` only; `.cmd` scripts can't be CI-linted (manual smoke checklist in CHANGELOG / plan files instead). EOL rules live in `.gitattributes` (`*.sh text eol=lf`, `*.ps1 text eol=crlf`, `*.cmd text eol=crlf`); Windows working tree may show CRLF due to `core.autocrlf=true` -- git normalizes on commit.

## Reading order for a new session

1. `CLAUDE.md` -- top-level orientation + auto-routing rule
2. `opencode.jsonc` -- agent definitions + soft-wall `permission: "allow"` (v0.5.0+)
3. `agents_manager/SKILL.md` -- master orchestration protocol (chub context-hub protocol is in Section Context-hub protocol)
4. `agents_manager/<role>/SKILL.md` -- for any specialist you dispatch (each has its own `Boundaries` section)
5. `agents_manager/CHANGELOG.md` -- system evolution (read the latest entry first)
6. `share/notes/02_plan_*.md` + `tasks/<id>.md` -- current in-flight work
7. **Book-gen intent->** also read `agents_manager/book-gen-orchestrator/SKILL.md`, `agents_manager/book-writer/SKILL.md`, optionally `agents_manager/book-reviewer/SKILL.md` (translation-mode only), `books/daily-focus/` (smoke-test reference), `book_workflow/book-agents/templates/`.
8. **Book2media intent->** also read `agents_manager/book2media-orchestrator/SKILL.md`, `book-kit/docs/TOOLKIT.md` (Pipeline map for Phase 9), `book-kit/docs/MEDIA.md` (narrative how-to), `book-kit/docs/SCRIPTS.md` (per-tool CLI reference).

## Tool usage efficiency (v0.5.1+)

- **Discovery first, read second.** Use `glob` (by pattern) or `grep` (by content) to find files; only THEN batch parallel `read` calls.
- **Batch parallel reads** when files are known. A folder analysis -> N `read` calls in one message, not N messages.
- **A `read` precedes every `edit` batch** (tool contract). Read once, then issue all edits in a single message.
- **Batch parallel `edit` calls** when independent. Verify `oldString` uniqueness across the batch before issuing. Verify once after, not mid-batch.
- **`task` (subagent dispatch) is NOT batchable** -- only `master` dispatches subagents per pipeline rule.
- **Re-read or re-grep after edits.** Edits shift line numbers; the next edit's `oldString` may no longer match.
